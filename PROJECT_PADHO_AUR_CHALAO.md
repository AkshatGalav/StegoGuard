# 📖 StegoGuard - Dost Ke Liye Complete Guide (Hinglish)

Bhai, yeh document tere liye banaya hai taaki tu is project ko asaani se **padh sake, samajh sake, apne laptop me chala sake aur online host kar sake**.

---

## 🧐 1. Project Kya Karta Hai? (Easy Explanation)

**StegoGuard** ek advanced **Cybersecurity & Machine Learning Web Application** hai:
1. **Secret Message Chhupana (Encode / Steganography)**:
   - Kisi bhi image (PNG/BMP) ke andar koi secret message hide karna.
   - Chhupane se pehle us message ko **AES-256-GCM** encryption se lock kiya jaata hai taaki agar koi data nikal bhi le, toh bina key ke koi padh na sake.
   - Saath me **RSA-2048** digital signature generate hota hai jisse authenticity verify ho sake.
2. **Message Nikalna (Decode)**:
   - Image upload karke encrypted message nikalna aur secret key daal kar decrypt karna.
3. **Steganalysis (AI / Machine Learning Detection)**:
   - Agar kisi suspect image me secret data chhupa hai, toh Machine Learning models (**Random Forest**, **Logistic Regression**, **SVM**) image ke 29 mathematical features (entropy, pixel variation, texture) analyze karke bata dete hain ki image normal hai ya uske andar data chhupa hai!
4. **Audit Logs & Vault**:
   - Har operation MongoDB database me log hota hai (bina sensitive secret key save kiye).

---

## 📂 2. Kaunsi File Kaha Hai? (Folder Guide)

| Folder / File | Iska Kaam Kya Hai |
|---|---|
| `server.py` | **Main Backend Server** (FastAPI par bana hai, API endpoints provide karta hai aur website ko serve karta hai). |
| `app.py` | **Streamlit App** (Agar Python GUI dashboard chalana ho toh). |
| `modules/` | **Core Backend Logic** (Encryption, Steganography, Feature Extraction, Auth, DB yahi likha hai). |
| `models/` | **Trained Machine Learning Models** (`.joblib` files jo steganalysis detect karte hain). |
| `dataset/` | Cover (original) aur Stego (hidden data wali) sample images. |
| `reports/` | Models ki accuracy metrics, CSVs aur confusion matrix images. |
| `static/` | **Ready-to-use Web UI** (React frontend ka built version. Is wajah se Node.js ke bina bhi direct Python se poori website khul jaati hai!). |
| `frontend/` | **React 19 + Vite Source Code** (Agar React code me UI/design badalna ho toh is folder me kaam hoga). |
| `.env` | MongoDB connection string aur environment secrets. |
| `requirements.txt` | Saare Python packages ki list jo install karni hoti hai. |

---

## ⚡ 3. Apne Laptop Me Kaise Chalaye? (Step-by-Step)

### Option A: Sabse Simple Tareeka (1-Click Run) ⭐
1. Pehle terminal khol kar Python packages install kar lo:
   ```bash
   pip install -r requirements.txt
   ```
2. Ab Windows par simply **`run_backend.bat`** par double click kar do!
   *(Ya terminal me command chalao: `python server.py`)*
3. Browser kholo aur open karo:
   👉 **http://127.0.0.1:8000**
   Poori website live chalne lagegi!
4. Swagger API documentation dekhne ke liye:
   👉 **http://127.0.0.1:8000/docs**

---

### Option B: Agar React Code me Changes Karne Ho (Frontend Dev Mode)
1. Terminal 1 me backend chalu rakho:
   ```bash
   python server.py
   ```
2. Terminal 2 me frontend folder me jaao aur dev server chalao:
   ```bash
   cd frontend
   npm install
   npm run dev
   # Ya run_frontend_dev.bat par double click karo
   ```
3. Browser me `http://localhost:5173` par live hot-reload ke saath website modify karo!

---

### Option C: Streamlit GUI Chalana Ho Toh
1. Terminal me run karo:
   ```bash
   streamlit run app.py
   # Ya run_streamlit.bat par double click karo
   ```
2. Browser me `http://localhost:8501` par Streamlit dashboard khul jaayega.

---

## 🌐 4. Website Ko Free Me Online Host Kaise Kare?

### Tareeka 1: Render.com Par Host Karna (Best & Easiest)
1. Is folder ko apne GitHub account par push karo (as private or public repo).
2. [Render.com](https://render.com) par free account banao.
3. **New +** par click karke **Web Service** choose karo.
4. Apna GitHub repository connect karo.
5. Yeh settings bharo:
   - **Name**: `stegoguard`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
6. **Environment Variables** me jaao aur add karo:
   - Key: `MONGODB_URI`
   - Value: Apna MongoDB Atlas cluster connection string (jo `.env` me hai)
7. **Deploy** par click kar do. 2-3 minute me tumhara free online live URL ready ho jaayega (e.g. `https://stegoguard.onrender.com`)!

---

### Tareeka 2: Railway.app Par Host Karna
1. [Railway.app](https://railway.app) par login karo.
2. **New Project** -> **Deploy from GitHub repo** select karo.
3. Settings me Start Command daalo: `uvicorn server:app --host 0.0.0.0 --port $PORT`.
4. Variables tab me `MONGODB_URI` set karo.
5. Generate Domain par click karo, aur website live ho jaayegi!

---

## 🛠️ 5. Agar Koi Dikkat Aaye Toh (Troubleshooting)

- **Issue**: `ModuleNotFoundError: No module named 'fastapi'` (ya koi aur package).
  - **Solution**: Terminal me `pip install -r requirements.txt` dubara run karo.
- **Issue**: MongoDB connect nahi ho raha / Timeout error.
  - **Solution**: MongoDB Atlas dashboard me jaakar `Network Access` me `0.0.0.0/0` (Allow Access from Anywhere) enable kiya hua hona chahiye.
- **Issue**: Image encode karte waqt error "Message too large".
  - **Solution**: LSB steganography me image ke resolution ke hisaab se space hoti hai. Badi text ke liye thodi badi image (PNG) use karo.
