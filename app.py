"""
Main Streamlit application for StegoGuard.
This file serves as the entry point for the web application and handles routing.
"""
import os
import base64
import tempfile
import numpy as np
import pandas as pd
from PIL import Image
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.pipeline import Pipeline

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
    get_record_by_id,
    delete_record,
    clear_all_records
)
from modules.validation import validate_uploaded_image
from modules.ui_theme import inject_cyber_theme, render_hero_header


@st.cache_resource
def get_cached_models(models_dir: str = "models") -> dict:
    """Loads and caches trained ML models from the models directory."""
    try:
        return load_models(models_dir)
    except FileNotFoundError:
        return {}


@st.cache_data
def get_cached_metrics(csv_path: str = "reports/model_metrics.csv") -> pd.DataFrame:
    """Loads and caches model evaluation metrics from CSV."""
    if os.path.exists(csv_path):
        try:
            return pd.read_csv(csv_path)
        except Exception:
            return None
    return None


@st.cache_data
def get_cached_features(csv_path: str = "reports/features.csv") -> pd.DataFrame:
    """Loads and caches extracted features dataset CSV."""
    if os.path.exists(csv_path):
        try:
            return pd.read_csv(csv_path)
        except Exception:
            return None
    return None


def main():
    # Initialize SQLite database schema
    initialize_database()

    st.set_page_config(
        page_title="StegoGuard - Security & Steganalysis",
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inject CyberSentinel Glassmorphism UI Theme
    inject_cyber_theme()
    
    st.sidebar.title("🛡️ StegoGuard")
    st.sidebar.caption("Classical ML Image Steganalysis & Security Framework")
    
    # Sidebar navigation options
    pages = [
        "Home",
        "Secure Encode",
        "Secure Decode",
        "Steganalysis",
        "Verification",
        "Model Analytics",
        "Evidence History"
    ]
    
    selection = st.sidebar.radio("Navigation", pages, help="Navigate between StegoGuard security modules.")
    
    render_hero_header(
        title="StegoGuard Sentinel",
        subtitle="Classical ML-Based Image Steganalysis with Encrypted Data Embedding & Integrity Verification",
        status_text="CYBERSENTINEL ACTIVE"
    )
    
    if selection == "Home":
        st.header("📌 Project Home & System Overview")
        st.write("""
        **StegoGuard** is a security and steganalysis framework developed for secure covert communication and statistical detection of image steganography using classical machine learning techniques.
        """)
        
        st.markdown("### 🔑 Key Modules & Capabilities")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.info("""
            **🔒 Secure Encode**  
            Encrypt confidential text with **AES-256-GCM** and embed the ciphertext payload into lossless PNG/BMP cover images via **LSB steganography**.
            """)
            st.info("""
            **🔏 Verification**  
            Calculate SHA-256 image/payload digests, generate RSA-2048 key pairs, sign payloads, and verify digital signatures for sender authenticity.
            """)
        with col_m2:
            st.info("""
            **🔓 Secure Decode**  
            Extract embedded stego payloads and authenticate ciphertext integrity via AES-GCM MAC tags before decrypting the original plaintext.
            """)
            st.info("""
            **📊 Model Analytics**  
            Inspect evaluation metrics (Accuracy, Precision, Recall, F1-Score, ROC-AUC), confusion matrices, and Random Forest feature importances.
            """)
        with col_m3:
            st.info("""
            **🔎 Steganalysis**  
            Analyze suspect images with trained classical ML models (**Logistic Regression, Random Forest, SVM**) to detect spatial LSB steganography anomalies.
            """)
            st.info("""
            **📜 Evidence History**  
            Review non-sensitive SQLite audit logs for past security operations with privacy retention enforcement (plaintext and keys are never stored).
            """)

        st.markdown("---")
        st.markdown("### 🔄 System Workflows & Architecture")
        
        tab_w1, tab_w2 = st.tabs(["1. Secure Encoding & Decoding Workflow", "2. Steganalysis ML Pipeline Workflow"])
        
        with tab_w1:
            st.markdown("""
            ```mermaid
            graph TD
                A[Plaintext Secret Message] -->|1. AES-256-GCM Encrypt| B(Encrypted Ciphertext Payload)
                C[Cover Image PNG/BMP] --> D{2. LSB Embedding Engine}
                B --> D
                D --> E[StegoGuard Stego Image]
                E --> F{3. LSB Extraction Engine}
                F --> G(Encrypted Ciphertext Payload)
                G -->|4. AES-256-GCM Decrypt & Authenticate| H[Original Plaintext Message]
            ```
            """)
            st.caption("Figure 1: End-to-end secure encoding and decoding workflow with authenticated AES-GCM encryption and LSB steganography.")

        with tab_w2:
            st.markdown("""
            ```mermaid
            graph TD
                I[Cover & Stego Image Dataset] --> J{1. Feature Extraction Module}
                J --> K[29 Image Features: Pixel Stats, Entropy, Differences, LBP, GLCM]
                K --> L[2. Stratified Train/Test Split 80/20]
                L --> M[3. Train Classifiers: Logistic Regression, Random Forest, SVM]
                M --> N[4. Save Trained Pipelines .joblib]
                O[Target Suspect Image] --> P{5. Extract Features}
                P --> Q(Trained ML Model Pipeline)
                Q --> R[Class Prediction: Cover 0 vs Stego 1 + Stego Probability]
            ```
            """)
            st.caption("Figure 2: Classical machine learning steganalysis training and real-time image prediction pipeline.")

        st.markdown("---")
        st.markdown("### 💻 Technology Stack")
        tech_data = {
            "Component": ["Application Framework", "Cryptography Engine", "Image Processing", "Machine Learning", "Data Analysis & Visualization", "Audit Database"],
            "Technologies Used": ["Python 3.x, Streamlit", "PyCryptodome, Cryptography", "OpenCV, Scikit-Image, Pillow", "Scikit-Learn, Joblib", "Pandas, NumPy, Plotly, Matplotlib", "SQLite3"],
            "Role & Purpose": [
                "Interactive Web UI dashboard, navigation routing, and user interface",
                "AES-256-GCM authenticated encryption and RSA-2048 PSS digital signatures",
                "RGB pixel loading, spatial LSB embedding, LBP texture & GLCM feature extraction",
                "Logistic Regression, Random Forest, and Support Vector Machine classifiers",
                "Metric reporting, comparison bar charts, and feature importance visualizers",
                "Persistent audit logging of operation timestamps, SHA-256 digests, and prediction results"
            ]
        }
        st.dataframe(pd.DataFrame(tech_data), use_container_width=True)

        st.markdown("---")
        st.markdown("### 🔒 Core Security Principles")
        st.warning("""
        - **Confidentiality**: Secret messages are encrypted prior to embedding using AES-256-GCM so intercepted payloads yield random noise without the key.
        - **Integrity**: SHA-256 hashing and AES-GCM MAC authentication tags detect any post-embedding data corruption or tampering.
        - **Authenticity**: RSA-2048 PSS digital signatures prove payload origin and prevent sender spoofing.
        - **Covertness**: LSB steganography conceals the very existence of confidential payload data inside spatial image pixels.
        - **Privacy Enforcement**: Plaintext secret messages, symmetric encryption keys, private signing keys, and passwords are **never** logged to disk or stored in SQLite database logs.
        """)
    
    elif selection == "Secure Encode":
        st.header("🔒 Secure Encode")
        st.write("Demonstration of AES-256-GCM Encryption and LSB Steganography embedding.")
        
        message = st.text_area(
            "Enter Secret Message to Encode",
            help="Type the confidential plaintext message you wish to encrypt and embed into a cover image."
        )
        cover_image_file = st.file_uploader(
            "Upload Cover Image (PNG, JPG, BMP)",
            type=["png", "jpg", "jpeg", "bmp", "tiff"],
            help="Select a lossless cover image file (max 10MB). PNG format is strongly recommended for lossless LSB embedding."
        )
        
        if cover_image_file is not None:
            try:
                img_meta = validate_uploaded_image(cover_image_file.getvalue(), cover_image_file.name)
                st.caption(f"Validated Image: {img_meta['format']} | {img_meta['width']}x{img_meta['height']} | {img_meta['size_bytes'] / 1024:.1f} KB")
            except ValueError as val_err:
                st.error(f"Image Validation Error: {str(val_err)}")
                cover_image_file = None
        
        if 'encryption_key' not in st.session_state:
            st.session_state.encryption_key = None
            
        if st.button("Generate Secure Key", help="Generates a new random 256-bit (32-byte) AES key."):
            st.session_state.encryption_key = generate_key()
            st.success("New 256-bit encryption key generated successfully!")
            
        if st.session_state.encryption_key:
            st.text_input("Current Key (Base64)", value=base64.b64encode(st.session_state.encryption_key).decode('utf-8'), disabled=True, help="Copy and save this 256-bit key to decrypt the message later.")
            
            if st.button("Encrypt & Embed", help="Encrypts the message with AES-256-GCM and embeds the payload into the cover image LSBs."):
                if message and cover_image_file:
                    tmp_path = None
                    stego_path = None
                    try:
                        encrypted_data = encrypt_message(message, st.session_state.encryption_key)
                        encrypted_bytes = encrypted_data.encode('utf-8')
                        
                        payload_hash = calculate_sha256(encrypted_bytes)
                        st.caption(f"Encrypted Payload SHA-256: `{payload_hash}`")
                        
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                            tmp_file.write(cover_image_file.getvalue())
                            tmp_path = tmp_file.name
                        
                        image_array = load_image(tmp_path)
                        capacity = calculate_capacity(image_array)
                        st.info(f"Image Capacity: {capacity} bytes. Payload size: {len(encrypted_bytes)} bytes.")
                        
                        stego_array = embed_data(image_array, encrypted_bytes)
                        st.success("Data encrypted and embedded successfully!")
                        
                        stego_path = tmp_path.replace(".png", "_stego.png")
                        save_stego_image(stego_array, stego_path)
                        
                        stego_hash = calculate_file_hash(stego_path)
                        st.caption(f"Stego Image SHA-256: `{stego_hash}`")
                        
                        # Log audit record
                        insert_record({
                            'operation_type': 'Secure Encode',
                            'input_filename': cover_image_file.name,
                            'output_filename': 'stego_image.png',
                            'image_hash': stego_hash,
                            'payload_hash': payload_hash,
                            'status': 'SUCCESS'
                        })
                        
                        with open(stego_path, "rb") as file:
                            st.download_button(
                                label="Download Stego Image",
                                data=file,
                                file_name="stego_image.png",
                                mime="image/png",
                                help="Download the generated PNG stego image containing your encrypted payload."
                            )
                        
                    except SteganographyError as e:
                        st.error(f"Steganography failed: {str(e)}")
                    except EncryptionError as e:
                        st.error(f"Encryption failed: {str(e)}")
                    except Exception as e:
                        st.error(f"Unexpected error: {str(e)}")
                    finally:
                        if tmp_path and os.path.exists(tmp_path):
                            os.remove(tmp_path)
                        if stego_path and os.path.exists(stego_path):
                            os.remove(stego_path)
                else:
                    st.warning("Please enter a message and upload a cover image.")
        
    elif selection == "Secure Decode":
        st.header("🔓 Secure Decode")
        st.write("Demonstration of LSB Steganography extraction and AES-256-GCM Decryption.")
        
        stego_image_file = st.file_uploader("Upload Stego Image (PNG)", type=["png"], help="Upload a StegoGuard PNG image containing an embedded payload.")
        
        if stego_image_file is not None:
            try:
                validate_uploaded_image(stego_image_file.getvalue(), stego_image_file.name, allowed_formats=('PNG',))
            except ValueError as val_err:
                st.error(f"Image Validation Error: {str(val_err)}")
                stego_image_file = None
                
        key_input = st.text_input("Enter Decryption Key (Base64)", help="Paste the 256-bit Base64 decryption key generated during encoding.")
        
        if st.button("Extract & Decrypt", help="Extracts the embedded payload and decrypts it using the provided key."):
            if stego_image_file and key_input:
                tmp_path = None
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                        tmp_file.write(stego_image_file.getvalue())
                        tmp_path = tmp_file.name
                        
                    image_array = load_image(tmp_path)
                    encrypted_bytes = extract_data(image_array)
                    encrypted_data = encrypted_bytes.decode('utf-8')
                    
                    payload_hash = calculate_sha256(encrypted_bytes)
                    st.success(f"Payload extracted successfully! (SHA-256: `{payload_hash[:16]}...`)")
                    
                    key_bytes = base64.b64decode(key_input)
                    decrypted_message = decrypt_message(encrypted_data, key_bytes)
                    st.success("Message decrypted and authenticated successfully!")
                    st.text_area("Decrypted Message", value=decrypted_message, disabled=True)
                    
                    # Log audit record
                    insert_record({
                        'operation_type': 'Secure Decode',
                        'input_filename': stego_image_file.name,
                        'payload_hash': payload_hash,
                        'status': 'SUCCESS'
                    })
                    
                except SteganographyError as e:
                    st.error(f"Failed to extract payload: {str(e)}")
                except EncryptionError as e:
                    st.error(f"Decryption/Authentication failed: {str(e)}")
                except Exception as e:
                    st.error(f"Unexpected error: {str(e)}")
                finally:
                    if tmp_path and os.path.exists(tmp_path):
                        os.remove(tmp_path)
            else:
                st.warning("Please upload a stego image and provide the decryption key.")
        
    elif selection == "Steganalysis":
        st.header("🔎 Steganalysis Dashboard")
        st.write("Analyze target images with trained classical ML models to detect steganographic modifications.")
        
        models = get_cached_models()
        
        if not models:
            st.warning("⚠️ No trained ML models found in the 'models/' directory.")
            st.info("Please run the model training script (`python -m modules.model_training`) to generate trained `.joblib` models before running steganalysis.")
        else:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                selected_model_name = st.selectbox(
                    "Select ML Model",
                    options=list(models.keys()),
                    help="Choose a pre-trained classical ML classifier (Logistic Regression, Random Forest, or SVM)."
                )
                uploaded_image = st.file_uploader(
                    "Upload Image for Analysis (PNG, JPG, BMP)",
                    type=["png", "jpg", "jpeg", "bmp", "tiff"],
                    help="Upload a target image file to analyze for LSB steganography anomaly features."
                )
                
                if uploaded_image is not None:
                    try:
                        validate_uploaded_image(uploaded_image.getvalue(), uploaded_image.name)
                        img = Image.open(uploaded_image)
                        st.image(img, caption=f"Target Image: {uploaded_image.name} ({img.width}x{img.height})", use_container_width=True)
                    except ValueError as val_err:
                        st.error(f"Image Validation Error: {str(val_err)}")
                        uploaded_image = None
            
            with col2:
                st.subheader("Analysis & Detection")
                
                if uploaded_image is not None:
                    if st.button("Run Steganalysis", type="primary", help="Extracts 29 features and evaluates the image using the selected ML classifier."):
                        suffix = os.path.splitext(uploaded_image.name)[1]
                        tmp_path = None
                        try:
                            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                                tmp_file.write(uploaded_image.getvalue())
                                tmp_path = tmp_file.name
                            
                            with st.spinner("Extracting 29 statistical & structural features..."):
                                features = extract_features_from_path(tmp_path)
                            
                            st.success("✅ Feature extraction complete (29 metrics extracted).")
                            
                            with st.spinner(f"Predicting payload class using {selected_model_name}..."):
                                single_model_dict = {selected_model_name: models[selected_model_name]}
                                feature_df = get_cached_features()
                                feature_names = None
                                if feature_df is not None:
                                    feature_names = [c for c in feature_df.columns if c not in ['label', 'image_path']]
                                
                                prediction_results = predict_image(tmp_path, single_model_dict, feature_names=feature_names)
                                result = prediction_results[selected_model_name]
                                image_hash = calculate_file_hash(tmp_path)
                            
                            st.markdown("---")
                            st.markdown("### Detection Results")
                            
                            res_col1, res_col2 = st.columns(2)
                            with res_col1:
                                if result['prediction'] == 1:
                                    st.error("🚨 Stego Image Detected")
                                else:
                                    st.success("✅ Clean Cover Image")
                            
                            with res_col2:
                                proba = result['stego_probability']
                                if not np.isnan(proba):
                                    st.metric("Stego Probability", f"{proba * 100:.1f}%")
                                else:
                                    st.metric("Stego Probability", "N/A")
                            
                            st.info(f"**Model Used**: {selected_model_name}")
                            
                            # Log audit record
                            insert_record({
                                'operation_type': 'Steganalysis',
                                'input_filename': uploaded_image.name,
                                'image_hash': image_hash,
                                'model_used': selected_model_name,
                                'prediction_result': result['label'],
                                'status': 'SUCCESS'
                            })
                            
                            with st.expander("View Extracted Image Features (29 Metrics)"):
                                df_feat = pd.DataFrame([features])
                                st.dataframe(df_feat, use_container_width=True)
                            
                        except Exception as e:
                            st.error(f"Steganalysis error: {str(e)}")
                        finally:
                            if tmp_path and os.path.exists(tmp_path):
                                os.remove(tmp_path)
                else:
                    st.info("Upload an image on the left to begin steganalysis.")
            
            st.markdown("---")
            st.warning("⚠️ **Disclaimer**: ML steganalysis predictions are probabilistic estimates based on statistical anomaly detection (LSB shifts). They do not constitute absolute cryptographic proof.")
        
    elif selection == "Verification":
        st.header("🔏 Integrity Verification & Digital Signatures")
        st.write("Ensure data integrity using SHA-256 cryptographic hashing and authenticate origin using RSA digital signatures.")
        
        v_tab1, v_tab2, v_tab3, v_tab4, v_tab5 = st.tabs([
            "1. SHA-256 Hashing",
            "2. RSA Key Generator",
            "3. Digital Signing",
            "4. Signature Verification",
            "5. Security Principles"
        ])
        
        with v_tab1:
            st.subheader("SHA-256 Cryptographic Hashing")
            st.write("Compute and verify SHA-256 hash digests for files or raw text.")
            
            hash_mode = st.radio("Select Input Mode", ["Upload File", "Raw Text"], help="Choose whether to hash a file or raw text string.")
            
            if hash_mode == "Upload File":
                up_file = st.file_uploader("Upload File to Hash (Image, Payload, or Binary)", help="Upload any file to compute its SHA-256 hash digest.")
                if up_file is not None:
                    file_bytes = up_file.getvalue()
                    computed_hash = calculate_sha256(file_bytes)
                    st.success(f"SHA-256 Hash Digest: `{computed_hash}`")
                    
                    expected_hash = st.text_input("Enter Expected SHA-256 Hash (Optional for Integrity Check)", help="Paste an expected SHA-256 hash to verify against.")
                    if expected_hash:
                        res = "VERIFIED" if verify_integrity(file_bytes, expected_hash) else "MISMATCH"
                        if res == "VERIFIED":
                            st.success("✅ Integrity Verified: Hash matches expected digest!")
                        else:
                            st.error("🚨 Integrity Violation: Hash mismatch detected!")
                        
                        insert_record({
                            'operation_type': 'Verification',
                            'input_filename': up_file.name,
                            'payload_hash': computed_hash,
                            'verification_result': res,
                            'status': 'SUCCESS'
                        })
            else:
                raw_text = st.text_area("Enter Text Content to Hash", help="Type text to calculate its SHA-256 hash digest.")
                if raw_text:
                    computed_hash = calculate_sha256(raw_text)
                    st.success(f"SHA-256 Hash Digest: `{computed_hash}`")
                    
                    expected_hash = st.text_input("Enter Expected SHA-256 Hash", help="Paste an expected SHA-256 hash to verify.")
                    if expected_hash:
                        res = "VERIFIED" if verify_integrity(raw_text, expected_hash) else "MISMATCH"
                        if res == "VERIFIED":
                            st.success("✅ Integrity Verified: Hash matches expected digest!")
                        else:
                            st.error("🚨 Integrity Violation: Hash mismatch detected!")
                        
                        insert_record({
                            'operation_type': 'Verification',
                            'input_filename': 'Raw Text',
                            'payload_hash': computed_hash,
                            'verification_result': res,
                            'status': 'SUCCESS'
                        })

        with v_tab2:
            st.subheader("RSA Signing Key Pair Generator")
            st.write("Generate an asymmetric RSA-2048 key pair for digital signing and verification.")
            
            if 'private_key_pem' not in st.session_state:
                st.session_state.private_key_pem = None
                st.session_state.public_key_pem = None
                
            if st.button("Generate New RSA-2048 Key Pair", help="Generates an RSA-2048 Private and Public Key PEM pair."):
                priv, pub = generate_signing_keys(2048)
                st.session_state.private_key_pem = priv.decode('utf-8')
                st.session_state.public_key_pem = pub.decode('utf-8')
                st.success("New RSA-2048 Key Pair generated successfully!")
                
            if st.session_state.private_key_pem:
                col_priv, col_pub = st.columns(2)
                with col_priv:
                    st.text_area("Private Key (PEM)", value=st.session_state.private_key_pem, height=250)
                    st.download_button(
                        "Download Private Key",
                        data=st.session_state.private_key_pem,
                        file_name="private_key.pem",
                        mime="application/x-pem-file",
                        help="Download the RSA private key. Keep this key secret!"
                    )
                with col_pub:
                    st.text_area("Public Key (PEM)", value=st.session_state.public_key_pem, height=250)
                    st.download_button(
                        "Download Public Key",
                        data=st.session_state.public_key_pem,
                        file_name="public_key.pem",
                        mime="application/x-pem-file",
                        help="Download the RSA public key to share with recipients."
                    )
                st.warning("⚠️ Keep your Private Key secret! Never share your private key. Share only your Public Key with recipients.")

        with v_tab3:
            st.subheader("Digital Payload Signing")
            st.write("Sign a data payload using an RSA Private Key to produce a digital signature.")
            
            payload_to_sign = st.text_area("Payload Data to Sign", help="Enter payload text to generate a digital signature.")
            priv_key_input = st.text_area(
                "Private Key (PEM)",
                value=st.session_state.private_key_pem if st.session_state.get('private_key_pem') else "",
                help="Paste your RSA Private Key in PEM format."
            )
            
            if st.button("Sign Payload", help="Computes an RSA-PSS SHA-256 digital signature."):
                if payload_to_sign and priv_key_input:
                    try:
                        sig_bytes = sign_data(payload_to_sign, priv_key_input)
                        sig_b64 = base64.b64encode(sig_bytes).decode('utf-8')
                        st.success("Digital signature generated successfully!")
                        st.text_area("Base64 Digital Signature", value=sig_b64, height=120)
                    except Exception as e:
                        st.error(f"Signing failed: {str(e)}")
                else:
                    st.warning("Please provide both payload data and a valid Private Key.")

        with v_tab4:
            st.subheader("Signature & Authenticity Verification")
            st.write("Verify the digital signature of a payload using the sender's Public Key.")
            
            payload_to_verify = st.text_area("Payload Data", help="Enter the payload text to verify.")
            sig_to_verify = st.text_area("Base64 Digital Signature", help="Paste the Base64 digital signature string.")
            pub_key_input = st.text_area(
                "Public Key (PEM)",
                value=st.session_state.public_key_pem if st.session_state.get('public_key_pem') else "",
                help="Paste the sender's RSA Public Key in PEM format."
            )
            
            if st.button("Verify Signature", help="Verifies that the signature matches the payload and public key."):
                if payload_to_verify and sig_to_verify and pub_key_input:
                    try:
                        sig_bytes = base64.b64decode(sig_to_verify.strip())
                        is_valid = verify_signature(payload_to_verify, sig_bytes, pub_key_input)
                        v_res = "SIGNATURE_VALID" if is_valid else "SIGNATURE_INVALID"
                        
                        if is_valid:
                            st.success("✅ Signature Verified: Authenticity and Integrity confirmed! Payload originated from the keyholder.")
                        else:
                            st.error("🚨 Signature Verification Failed: Payload has been tampered with or public key does not match sender!")
                            
                        insert_record({
                            'operation_type': 'Verification',
                            'input_filename': 'Payload Text',
                            'payload_hash': calculate_sha256(payload_to_verify),
                            'verification_result': v_res,
                            'status': 'SUCCESS' if is_valid else 'FAILED'
                        })
                    except Exception as e:
                        st.error(f"Verification error: {str(e)}")
                else:
                    st.warning("Please provide payload data, digital signature, and public key.")

        with v_tab5:
            st.subheader("Security Principles Breakdown")
            st.markdown("""
            | Guarantee | Technique Used | Purpose |
            |---|---|---|
            | **Confidentiality** | **AES-256-GCM Encryption** | Ensures secret messages cannot be read without the symmetric key. |
            | **Integrity** | **SHA-256 Hashing** | Detects any unauthorized modification or corruption of images or payloads. |
            | **Authenticity & Non-Repudiation** | **RSA-PSS Digital Signature** | Verifies the origin/identity of the sender using public-key cryptography. |
            | **Covertness (Hidden Existence)** | **LSB Steganography** | Hides the very existence of secret data inside cover image pixels. |

            > [!IMPORTANT]
            > **Hash vs Digital Signature**: A hash function (like SHA-256) proves that data has not changed, but **does not prove sender identity** because anyone can compute a hash. Digital signatures combine hashing with asymmetric private keys to guarantee both **integrity** and **sender authenticity**.
            """)

    elif selection == "Model Analytics":
        st.header("📊 Model Analytics Dashboard")
        st.write("Compare performance metrics, confusion matrices, and feature importances across trained classical ML models.")
        
        metrics_df = get_cached_metrics()
        models = get_cached_models()
        
        if metrics_df is None or metrics_df.empty:
            st.warning("⚠️ No model evaluation metrics found in 'reports/model_metrics.csv'.")
            st.info("Please run model training (`python -m modules.model_training`) to generate evaluation reports.")
        else:
            st.markdown("### Top Performance Overview")
            best_acc_row = metrics_df.loc[metrics_df['Accuracy'].idxmax()]
            best_f1_row = metrics_df.loc[metrics_df['F1-Score'].idxmax()]
            best_auc_row = metrics_df.loc[metrics_df['ROC-AUC'].idxmax()]
            
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            with kpi_col1:
                st.metric("Highest Accuracy", f"{best_acc_row['Accuracy']*100:.1f}%", f"{best_acc_row['Model']}")
            with kpi_col2:
                st.metric("Highest F1-Score", f"{best_f1_row['F1-Score']*100:.1f}%", f"{best_f1_row['Model']}")
            with kpi_col3:
                st.metric("Highest ROC-AUC", f"{best_auc_row['ROC-AUC']*100:.1f}%", f"{best_auc_row['Model']}")
            
            st.markdown("---")
            
            st.markdown("### Model Comparison Metrics")
            st.dataframe(metrics_df, use_container_width=True)
            
            df_melted = metrics_df.melt(id_vars=['Model'], var_name='Metric', value_name='Score')
            fig_comp = px.bar(
                df_melted,
                x='Model',
                y='Score',
                color='Metric',
                barmode='group',
                title="Model Performance Metric Comparison",
                range_y=[0, 1.05]
            )
            fig_comp.update_layout(height=400)
            st.plotly_chart(fig_comp, use_container_width=True)
            
            st.markdown("---")
            
            st.markdown("### Confusion Matrices")
            selected_cm_model = st.selectbox("Select Model for Confusion Matrix", options=metrics_df['Model'].tolist(), help="Select a model to view its saved confusion matrix plot.")
            
            slug_name = selected_cm_model.lower().replace(" ", "_")
            cm_img_path = os.path.join("reports", f"confusion_matrix_{slug_name}.png")
            
            if os.path.exists(cm_img_path):
                cm_img = Image.open(cm_img_path)
                st.image(cm_img, caption=f"Confusion Matrix - {selected_cm_model}", width=500)
            else:
                st.info(f"Confusion matrix plot for {selected_cm_model} not found at {cm_img_path}.")
            
            st.markdown("---")
            
            st.markdown("### Feature Importance Analysis (Random Forest)")
            if 'Random Forest' in models:
                rf_model = models['Random Forest']
                if isinstance(rf_model, Pipeline):
                    classifier = rf_model.named_steps['classifier']
                else:
                    classifier = rf_model
                
                if hasattr(classifier, "feature_importances_"):
                    importances = classifier.feature_importances_
                    
                    feature_df = get_cached_features()
                    if feature_df is not None:
                        feature_names = [c for c in feature_df.columns if c not in ['label', 'image_path']]
                    else:
                        feature_names = [f"Feature_{i}" for i in range(len(importances))]
                    
                    imp_df = pd.DataFrame({
                        'Feature': feature_names,
                        'Importance': importances
                    }).sort_values(by='Importance', ascending=True)
                    
                    fig_imp = px.bar(
                        imp_df.tail(15),
                        x='Importance',
                        y='Feature',
                        orientation='h',
                        title="Top 15 Most Important Features for Steganalysis",
                        color='Importance',
                        color_continuous_scale='Viridis'
                    )
                    fig_imp.update_layout(height=500)
                    st.plotly_chart(fig_imp, use_container_width=True)
                else:
                    st.info("Random Forest classifier does not expose feature_importances_.")
            else:
                st.info("Random Forest model is not available in loaded models.")
        
    elif selection == "Evidence History":
        st.header("📜 Evidence History Dashboard")
        st.write("Review non-sensitive audit logs for security operations, filtering by operation type and date range.")

        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1:
            op_filter = st.selectbox("Operation Type", ["ALL", "Secure Encode", "Secure Decode", "Steganalysis", "Verification"], help="Filter audit records by operation type.")
        with col_f2:
            start_d = st.date_input("Start Date", value=None, help="Filter records logged on or after this date.")
        with col_f3:
            end_d = st.date_input("End Date", value=None, help="Filter records logged on or before this date.")

        start_str = start_d.strftime("%Y-%m-%d") if start_d else None
        end_str = end_d.strftime("%Y-%m-%d") if end_d else None

        records = get_records(operation_type=op_filter, start_date=start_str, end_date=end_str)

        if not records:
            st.info("No audit records found matching the selected filters.")
        else:
            df_records = pd.DataFrame(records)
            st.dataframe(df_records, use_container_width=True)

            st.markdown("---")
            col_del1, col_del2 = st.columns([2, 1])
            with col_del1:
                selected_id = st.selectbox("Select Record ID to Delete or Inspect", options=df_records['id'].tolist(), help="Select a record ID to view full metadata or delete.")
                if selected_id:
                    rec = get_record_by_id(selected_id)
                    if rec:
                        with st.expander(f"Inspect Details for Record #{selected_id}"):
                            st.json(rec)
            with col_del2:
                if st.button("Delete Selected Record", type="secondary", help="Deletes the selected record from evidence history."):
                    if selected_id:
                        if delete_record(selected_id):
                            st.success(f"Record #{selected_id} deleted successfully.")
                            st.rerun()

            if st.button("Clear All Evidence History", type="secondary", help="Deletes all records from the audit database."):
                if clear_all_records():
                    st.success("All evidence history cleared.")
                    st.rerun()

        st.markdown("---")
        st.info("""
        🔒 **Privacy Disclosure & Retention Policy**: StegoGuard logs non-sensitive operational metadata (timestamps, SHA-256 digests, filenames, model predictions, status) to support security auditing. Plaintext secret messages, symmetric encryption keys, passwords, and private signing keys are **never** stored.
        """)


if __name__ == "__main__":
    main()
