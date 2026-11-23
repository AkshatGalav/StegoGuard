"""
StegoGuard FastAPI Backend Server.
Provides RESTful API endpoints for AES-256-GCM encryption, LSB steganography,
RSA-2048 digital signatures, classical ML steganalysis, and SQLite audit logging.
"""
import os
from dotenv import load_dotenv
load_dotenv()
import base64
import tempfile
import numpy as np
import pandas as pd
from PIL import Image
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from modules.encryption import generate_key, encrypt_message, decrypt_message, EncryptionError
from modules.steganography import (
    load_image,
    save_stego_image,
    calculate_capacity,
    embed_data,
    extract_data,
    SteganographyError
)
from modules.feature_extraction import extract_features_from_path
from modules.model_training import load_models, predict_image
from modules.verification import (
    calculate_sha256,
    calculate_file_hash,
    generate_signing_keys,
    sign_data,
    verify_signature,
    verify_integrity
)
from modules.database import (
    initialize_database,
    insert_record,
    get_records,
    clear_all_records
)
from modules.validation import validate_uploaded_image
from modules.auth import (
    create_user,
    get_user_by_username_or_email,
    get_user_by_id,
    verify_password,
    create_access_token,
    verify_access_token,
    save_user_key,
    get_user_keys,
    delete_user_key
)
from fastapi import Header

# Initialize FastAPI app
app = FastAPI(
    title="StegoGuard Sentinel API",
    description="REST API for Classical ML Image Steganalysis & Encrypted Data Embedding",
    version="2.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database schema on startup
@app.on_event("startup")
def startup_event():
    initialize_database()

# Global loaded models cache
cached_models = {}

def get_models():
    global cached_models
    if not cached_models:
        try:
            cached_models = load_models("models")
        except Exception:
            cached_models = {}
    return cached_models


def get_current_user_optional(authorization: Optional[str] = Header(None)) -> Optional[dict]:
    """Helper to extract current logged in user dict from Authorization header if present."""
    if not authorization:
        return None
    try:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            payload = verify_access_token(parts[1])
            if payload:
                user_id = str(payload["sub"])
                return get_user_by_id(user_id)
    except Exception:
        pass
    return None


# AUTHENTICATION & VAULT ENDPOINTS

@app.post("/api/auth/register")
def api_register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    """Registers a new user account and returns JWT token."""
    try:
        user = create_user(username, email, password, role="user")
        token = create_access_token(user["id"], user["username"], user["role"])
        return {
            "status": "SUCCESS",
            "token": token,
            "user": user
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@app.post("/api/auth/login")
def api_login(
    identifier: str = Form(...),  # username or email
    password: str = Form(...)
):
    """Authenticates user and returns JWT access token."""
    user = get_user_by_username_or_email(identifier)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username/email or password.")

    token = create_access_token(user["id"], user["username"], user["role"])
    user_profile = {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user["role"],
        "created_at": user["created_at"]
    }
    return {
        "status": "SUCCESS",
        "token": token,
        "user": user_profile
    }


@app.get("/api/auth/me")
def api_get_current_user(authorization: Optional[str] = Header(None)):
    """Returns profile of currently logged-in user."""
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    return {"status": "SUCCESS", "user": user}


@app.get("/api/vault/keys")
def api_get_vault_keys(authorization: Optional[str] = Header(None)):
    """Returns saved keys from logged-in user's private key vault."""
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    keys = get_user_keys(user["id"])
    return {"status": "SUCCESS", "keys": keys}


@app.post("/api/vault/keys")
def api_save_vault_key(
    key_name: str = Form(...),
    key_type: str = Form(...),
    key_data: str = Form(...),
    authorization: Optional[str] = Header(None)
):
    """Saves a cryptographic key or RSA keypair into user's key vault."""
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    key_id = save_user_key(user["id"], key_name, key_type, key_data)
    return {"status": "SUCCESS", "key_id": key_id, "message": "Key saved to vault successfully."}


@app.delete("/api/vault/keys/{key_id}")
def api_delete_vault_key(key_id: int, authorization: Optional[str] = Header(None)):
    """Deletes a key from logged-in user's vault."""
    user = get_current_user_optional(authorization)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated.")
    success = delete_user_key(user["id"], key_id)
    if not success:
        raise HTTPException(status_code=404, detail="Key not found in vault.")
    return {"status": "SUCCESS", "message": "Key deleted from vault."}


@app.get("/api/health")
def health_check():
    return {"status": "ONLINE", "version": "2.0.0", "framework": "FastAPI"}


@app.post("/api/encode")
async def api_encode(
    message: str = Form(...),
    key_b64: Optional[str] = Form(None),
    cover_image: UploadFile = File(...),
    authorization: Optional[str] = Header(None)
):
    """Encrypts text using AES-256-GCM and embeds ciphertext into cover image LSBs."""
    tmp_cover_path = None
    stego_out_path = None
    user = get_current_user_optional(authorization)
    user_id = user["id"] if user else None
    try:
        image_bytes = await cover_image.read()
        validate_uploaded_image(image_bytes, cover_image.filename)

        # Parse or generate AES key
        if key_b64 and key_b64.strip():
            key_bytes = base64.b64decode(key_b64.strip())
        else:
            key_bytes = generate_key()
            key_b64 = base64.b64encode(key_bytes).decode('utf-8')

        # Encrypt message
        encrypted_data = encrypt_message(message, key_bytes)
        encrypted_bytes = encrypted_data.encode('utf-8')
        payload_hash = calculate_sha256(encrypted_bytes)

        # Save uploaded image to temp file
        suffix = os.path.splitext(cover_image.filename)[1] or ".png"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(image_bytes)
            tmp_cover_path = tmp_file.name

        image_array = load_image(tmp_cover_path)
        capacity = calculate_capacity(image_array)

        if len(encrypted_bytes) > capacity:
            raise HTTPException(status_code=400, detail=f"Payload size ({len(encrypted_bytes)} B) exceeds capacity ({capacity} B).")

        stego_array = embed_data(image_array, encrypted_bytes)
        stego_out_path = tmp_cover_path.replace(suffix, "_stego.png")
        save_stego_image(stego_array, stego_out_path)

        stego_hash = calculate_file_hash(stego_out_path)

        with open(stego_out_path, "rb") as f:
            stego_b64 = base64.b64encode(f.read()).decode('utf-8')

        # Log to audit database
        insert_record({
            'user_id': user_id,
            'operation_type': 'Secure Encode',
            'input_filename': cover_image.filename,
            'output_filename': 'stego_image.png',
            'image_hash': stego_hash,
            'payload_hash': payload_hash,
            'status': 'SUCCESS'
        })

        return {
            "status": "SUCCESS",
            "key_b64": key_b64,
            "stego_image_b64": f"data:image/png;base64,{stego_b64}",
            "payload_hash": payload_hash,
            "stego_hash": stego_hash,
            "capacity_bytes": capacity,
            "payload_bytes": len(encrypted_bytes)
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except (EncryptionError, SteganographyError) as err:
        raise HTTPException(status_code=400, detail=str(err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encoding failed: {str(e)}")
    finally:
        if tmp_cover_path and os.path.exists(tmp_cover_path):
            os.remove(tmp_cover_path)
        if stego_out_path and os.path.exists(stego_out_path):
            os.remove(stego_out_path)


@app.post("/api/decode")
async def api_decode(
    key_b64: str = Form(...),
    stego_image: UploadFile = File(...)
):
    """Extracts stego payload from PNG and decrypts message using AES-256-GCM."""
    tmp_stego_path = None
    try:
        image_bytes = await stego_image.read()
        validate_uploaded_image(image_bytes, stego_image.filename, allowed_formats=('PNG',))

        key_bytes = base64.b64decode(key_b64.strip())

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_file.write(image_bytes)
            tmp_stego_path = tmp_file.name

        image_array = load_image(tmp_stego_path)
        encrypted_bytes = extract_data(image_array)
        encrypted_data = encrypted_bytes.decode('utf-8')

        payload_hash = calculate_sha256(encrypted_bytes)
        decrypted_message = decrypt_message(encrypted_data, key_bytes)

        insert_record({
            'operation_type': 'Secure Decode',
            'input_filename': stego_image.filename,
            'payload_hash': payload_hash,
            'status': 'SUCCESS'
        })

        return {
            "status": "SUCCESS",
            "decrypted_message": decrypted_message,
            "payload_hash": payload_hash
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Decoding failed: {str(e)}")
    finally:
        if tmp_stego_path and os.path.exists(tmp_stego_path):
            os.remove(tmp_stego_path)


@app.post("/api/steganalysis")
async def api_steganalysis(
    model_name: str = Form(...),
    image: UploadFile = File(...)
):
    """Extracts 29 features from image and classifies it using classical ML models."""
    tmp_img_path = None
    try:
        image_bytes = await image.read()
        validate_uploaded_image(image_bytes, image.filename)

        models = get_models()
        if model_name not in models:
            raise HTTPException(status_code=400, detail=f"Model '{model_name}' not available.")

        suffix = os.path.splitext(image.filename)[1] or ".png"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(image_bytes)
            tmp_img_path = tmp_file.name

        features = extract_features_from_path(tmp_img_path)

        feature_names = None
        csv_path = "reports/features.csv"
        if os.path.exists(csv_path):
            try:
                df_feat = pd.read_csv(csv_path)
                feature_names = [c for c in df_feat.columns if c not in ['label', 'image_path']]
            except Exception:
                pass

        single_model_dict = {model_name: models[model_name]}
        pred_results = predict_image(tmp_img_path, single_model_dict, feature_names=feature_names)
        res = pred_results[model_name]
        image_hash = calculate_file_hash(tmp_img_path)

        insert_record({
            'operation_type': 'Steganalysis',
            'input_filename': image.filename,
            'image_hash': image_hash,
            'model_used': model_name,
            'prediction_result': res['label'],
            'status': 'SUCCESS'
        })

        stego_prob = float(res['stego_probability']) if not np.isnan(res['stego_probability']) else 0.0

        return {
            "status": "SUCCESS",
            "model_used": model_name,
            "prediction": res['prediction'],  # 0 for Cover, 1 for Stego
            "label": res['label'],            # "Cover Image" or "Stego Image"
            "stego_probability": stego_prob,
            "image_hash": image_hash,
            "features": features
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Steganalysis error: {str(e)}")
    finally:
        if tmp_img_path and os.path.exists(tmp_img_path):
            os.remove(tmp_img_path)


@app.post("/api/verification/hash")
async def api_hash(
    text: Optional[str] = Form(None),
    expected_hash: Optional[str] = Form(None),
    file: Optional[UploadFile] = None
):
    """Calculates SHA-256 hash digest for file or text string and verifies integrity."""
    try:
        if file is not None:
            content_bytes = await file.read()
            computed_hash = calculate_sha256(content_bytes)
            filename = file.filename
        elif text is not None and text.strip():
            content_bytes = text.strip()
            computed_hash = calculate_sha256(content_bytes)
            filename = "Raw Text"
        else:
            raise HTTPException(status_code=400, detail="Must provide either file or text.")

        is_verified = None
        if expected_hash and expected_hash.strip():
            is_verified = verify_integrity(content_bytes, expected_hash.strip())

        verification_result = "VERIFIED" if is_verified is True else ("MISMATCH" if is_verified is False else "HASH_COMPUTED")

        insert_record({
            'operation_type': 'Verification',
            'input_filename': filename,
            'payload_hash': computed_hash,
            'verification_result': verification_result,
            'status': 'SUCCESS'
        })

        return {
            "status": "SUCCESS",
            "computed_hash": computed_hash,
            "expected_hash": expected_hash,
            "is_verified": is_verified,
            "verification_result": verification_result
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/verification/generate-keys")
def api_generate_keys():
    """Generates RSA-2048 signing key pair (PEM format)."""
    try:
        priv_bytes, pub_bytes = generate_signing_keys(2048)
        return {
            "status": "SUCCESS",
            "private_key": priv_bytes.decode('utf-8'),
            "public_key": pub_bytes.decode('utf-8')
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/verification/sign")
def api_sign_payload(
    payload: str = Form(...),
    private_key_pem: str = Form(...)
):
    """Signs payload string using RSA Private Key."""
    try:
        sig_bytes = sign_data(payload, private_key_pem)
        sig_b64 = base64.b64encode(sig_bytes).decode('utf-8')
        return {
            "status": "SUCCESS",
            "signature_b64": sig_b64
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Signing failed: {str(e)}")


@app.post("/api/verification/verify")
def api_verify_signature(
    payload: str = Form(...),
    signature_b64: str = Form(...),
    public_key_pem: str = Form(...)
):
    """Verifies digital signature against payload and public key."""
    try:
        sig_bytes = base64.b64decode(signature_b64.strip())
        is_valid = verify_signature(payload, sig_bytes, public_key_pem)
        return {
            "status": "SUCCESS",
            "is_valid": is_valid
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Verification failed: {str(e)}")


@app.get("/api/analytics")
def api_analytics():
    """Returns model metrics CSV data and feature importances."""
    metrics_data = []
    csv_path = "reports/model_metrics.csv"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            metrics_data = df.to_dict(orient="records")
        except Exception:
            metrics_data = []

    models = get_models()
    rf_importances = []
    if "Random Forest" in models:
        rf = models["Random Forest"]
        if hasattr(rf, "named_steps") and "classifier" in rf.named_steps:
            clf = rf.named_steps["classifier"]
            if hasattr(clf, "feature_importances_"):
                csv_feat = "reports/features.csv"
                feat_names = []
                if os.path.exists(csv_feat):
                    df_f = pd.read_csv(csv_feat)
                    feat_names = [c for c in df_f.columns if c not in ['label', 'image_path']]
                
                imps = clf.feature_importances_
                for i in range(min(len(imps), len(feat_names))):
                    rf_importances.append({"feature": feat_names[i], "importance": float(imps[i])})
                
                rf_importances = sorted(rf_importances, key=lambda x: x["importance"], reverse=True)[:10]

    return {
        "status": "SUCCESS",
        "metrics": metrics_data,
        "rf_top_features": rf_importances
    }


@app.get("/api/audit-logs")
def api_audit_logs(authorization: Optional[str] = Header(None)):
    """Returns database audit records filtered by logged-in user."""
    user = get_current_user_optional(authorization)
    if user and user.get("role") != "admin":
        records = get_records(user_id=user["id"])
    else:
        records = get_records()
    return {"status": "SUCCESS", "records": records}


@app.delete("/api/audit-logs")
def api_clear_audit_logs(authorization: Optional[str] = Header(None)):
    """Clears audit records."""
    user = get_current_user_optional(authorization)
    if user and user.get("role") != "admin":
        # Clear only user's records if not admin
        records = get_records(user_id=user["id"])
        for r in records:
            from modules.database import delete_record
            delete_record(r["id"])
    else:
        clear_all_records()
    return {"status": "SUCCESS", "message": "Audit logs cleared."}


# Serve Static Frontend Files
app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
