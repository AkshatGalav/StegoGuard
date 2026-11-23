# StegoGuard 🛡️
### Classical ML-Based Image Steganalysis with Encrypted Data Embedding & Integrity Verification

Welcome to **StegoGuard** — a full-stack cybersecurity framework combining **AES-256-GCM authenticated encryption**, **lossless LSB steganography**, **RSA-2048 digital signatures**, and **Classical Machine Learning steganalysis** (Logistic Regression, Random Forest, SVM) with MongoDB audit logging.

---

## 📁 Project Structure

```text
stegoguard/
├── server.py              # FastAPI REST backend + serves pre-built React frontend
├── app.py                 # Streamlit dashboard (alternative Python UI)
├── requirements.txt       # Python dependencies (FastAPI, PyMongo, ML models, etc.)
├── .env                   # Environment file (MongoDB connection URI)
├── .env.example           # Example environment template
│
├── modules/               # Core backend security & ML modules
│   ├── encryption.py      # AES-256-GCM encryption & decryption with authentication tags
│   ├── steganography.py   # LSB image embedding with custom binary header (STEGO v1.0)
│   ├── feature_extraction.py # 29 spatial, entropy, LBP, and GLCM feature extractor
│   ├── model_training.py  # ML pipeline trainer & predictor
│   ├── steganalysis.py    # Steganalysis helper
│   ├── verification.py    # SHA-256 hashing & RSA-2048 PSS digital signatures
│   ├── auth.py            # JWT token authentication & user credential management
│   ├── database.py        # MongoDB audit logging & key vault
│   ├── validation.py      # Image format, size, and security integrity checks
│   └── ui_theme.py        # Streamlit styling & themes
│
├── models/                # Pre-trained ML model pipelines (.joblib)
│   ├── logistic_regression.joblib
│   ├── random_forest.joblib
│   └── support_vector_machine.joblib
│
├── dataset/               # Sample cover and stego images for testing/training
│   ├── cover/
│   └── stego/
│
├── reports/               # ML evaluation metrics, confusion matrices, and feature CSVs
│   ├── model_metrics.csv
│   ├── features.csv
│   └── confusion_matrix_*.png
│
├── scripts/
│   └── train_stegoguard.py # Script to retrain ML models and regenerate reports
│
├── tests/                 # Comprehensive automated test suite (pytest)
│
├── static/                # Pre-built production frontend (HTML, CSS, JS bundle)
│                          # Served directly by server.py at http://127.0.0.1:8000
│
├── frontend/              # React 19 + Vite frontend source code
│   ├── src/               # React components, pages, context, and styles
│   ├── package.json       # Frontend dependencies (React, Lucide icons, Vite)
│   └── vite.config.js     # Vite configuration
│
├── run_backend.bat        # Windows 1-click launcher for FastAPI backend
├── run_streamlit.bat      # Windows 1-click launcher for Streamlit UI
└── run_frontend_dev.bat   # Windows 1-click launcher for React development server
```

---

## 🚀 Quick Start (Local Setup)

### Prerequisites
- **Python 3.10+** installed and added to PATH.
- (Optional for frontend development) **Node.js 18+** & npm.

### Step 1: Install Python Dependencies
Open your terminal in this folder and run:
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Copy `.env.example` to `.env` (or use the pre-configured `.env` file):
```bash
# If on Linux / Mac:
cp .env.example .env
```
Ensure your `MONGODB_URI` is set properly in `.env`.

---

## 💻 How to Run the Application

You have **3 options** to run the project depending on what you need:

### Option 1: Instant Web App (FastAPI + Pre-Built Frontend) — Recommended ⭐
Run the backend server. It serves both the REST API and the pre-built React UI:
```bash
python server.py
# Or on Windows, double-click: run_backend.bat
```
- **Web App**: Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.
- **Interactive Swagger API Docs**: Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

### Option 2: Frontend Development Mode (Hot-Reload)
If you want to modify the React frontend code:
1. Start the backend in terminal 1:
   ```bash
   python server.py
   ```
2. In terminal 2, navigate to `frontend` and start Vite:
   ```bash
   cd frontend
   npm install
   npm run dev
   # Or on Windows, double-click: run_frontend_dev.bat
   ```
   Open the Vite dev URL (typically [http://localhost:5173](http://localhost:5173)).
3. After making changes, rebuild the static bundle:
   ```bash
   npm run build
   # Copy contents of frontend/dist to static/ if you update the build
   ```

---

### Option 3: Streamlit Dashboard Mode
To run the interactive Streamlit Python dashboard:
```bash
streamlit run app.py
# Or on Windows, double-click: run_streamlit.bat
```
Open [http://localhost:8501](http://localhost:8501).

---

## 🧪 Running Tests & Retraining Models

- **Run all automated tests:**
  ```bash
  python -m pytest tests/ -v
  ```

- **Retrain the ML steganalysis models:**
  ```bash
  python -m scripts.train_stegoguard
  ```

---

## 🌐 Hosting & Deployment Guide

### A. Deploy on Render.com (Easiest Cloud Option)
1. Push the code to a GitHub repository (do not commit secret credentials).
2. Go to [Render Dashboard](https://dashboard.render.com/) and click **New + > Web Service**.
3. Connect your GitHub repo.
4. Settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add:
   - `MONGODB_URI`: your MongoDB Atlas connection string.
6. Click **Deploy Web Service**. Your site will be live with a free HTTPS URL!

### B. Deploy on Railway.app
1. Go to [Railway](https://railway.app/) and create a new project from your GitHub repo.
2. Railway detects Python automatically.
3. Set the start command to:
   ```bash
   uvicorn server:app --host 0.0.0.0 --port $PORT
   ```
4. Add the `MONGODB_URI` environment variable.

### C. Deploy on a Linux VPS (Ubuntu / Debian)
1. Install Python, pip, and git:
   ```bash
   sudo apt update && sudo apt install python3-pip python3-venv nginx -y
   ```
2. Clone your project and setup virtual environment:
   ```bash
   git clone <repo-url> stegoguard
   cd stegoguard
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run with Gunicorn/Uvicorn under systemd or supervisor:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker server:app --bind 0.0.0.0:8000
   ```
4. Set up an Nginx reverse proxy to port `8000` with Let's Encrypt SSL.

---

## 🔒 Security Best Practices
- **Confidentiality**: Secret payloads are encrypted using AES-256-GCM before embedding.
- **Privacy Compliance**: Plaintext messages, private keys, and encryption passphrases are NEVER saved in MongoDB or logged anywhere.
- **Integrity**: SHA-256 cryptographic hashes and RSA digital signatures ensure transmitted images have not been altered.
