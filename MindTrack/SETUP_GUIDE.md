# 🧠 MindTrack - Anaconda Setup Guide

## 🎯 Complete Integration Status

### ✅ Connected Components:

1. **Frontend ↔ Backend** - ✅ FULLY CONNECTED
   - API client sends requests to backend
   - User creation works
   - Habit tracking saves to database
   - Insights fetch from backend API

2. **Backend ↔ Database** - ✅ CONNECTED
   - SQLAlchemy ORM configured
   - Tables auto-created on startup
   - CRUD operations working

3. **Backend ↔ ML Model** - ✅ CONNECTED
  - Pipeline loads from `backend/data/pipeline.pkl`
   - Sleep prediction endpoint working
   - Feature importance available

### ⚠️ Partially Connected:

- **Frontend ↔ ML Predictions** - PARTIALLY CONNECTED
  - API endpoint exists and works
  - Frontend hasn't added UI to call ML predictions yet

---

## 🚀 Running on Anaconda Prompt (Step-by-Step)

### **Method 1: Automated Setup (Recommended)**

**For Windows:**
```cmd
cd C:\Users\USER\Downloads\MindTrack2\MindTrack
setup_and_run.bat
```

**For Linux/Mac:**
```bash
cd /path/to/MindTrack2/MindTrack
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### **Method 2: Manual Setup**

#### **Step 1: Open Anaconda Prompt**
- Open Anaconda Prompt from Start Menu

#### **Step 2: Create Conda Environment**
```cmd
cd C:\Users\USER\Downloads\MindTrack2\MindTrack

# Create environment
conda create -n mindtrack python=3.10 -y

# Activate environment
conda activate mindtrack
```

#### **Step 3: Install Backend Dependencies**
```cmd
cd backend
pip install -r requirements.txt
cd ..
```

#### **Step 4: Install Frontend Dependencies**
```cmd
cd frontend
pip install -r requirements.txt
cd ..
```

---

## 🏃 Running the Application

### **Terminal 1: Start Backend**

```cmd
# Activate environment
conda activate mindtrack

# Navigate to backend
cd C:\Users\USER\Downloads\MindTrack2\MindTrack\backend

# Run backend server
python app/main.py
```

**Backend will start at:** http://localhost:8000
**API docs at:** http://localhost:8000/docs

### **Terminal 2: Start Frontend**

```cmd
# Activate environment (in new Anaconda Prompt window)
conda activate mindtrack

# Navigate to frontend
cd C:\Users\USER\Downloads\MindTrack2\MindTrack\frontend

# Run Streamlit
streamlit run MindTracker_frontend/app.py
```

**Frontend will start at:** http://localhost:8501

---

## ✅ Verification Steps

### **1. Check Backend is Running**
Visit: http://localhost:8000

Should see:
```json
{
  "message": "MindTrack API is running",
  "version": "1.0.0"
}
```

### **2. Check API Docs**
Visit: http://localhost:8000/docs

Should see interactive API documentation

### **3. Check ML Pipeline**
Visit: http://localhost:8000/predictions/health

Should see:
```json
{
  "status": "available",
  "message": "ML pipeline is ready"
}
```

### **4. Test ML Prediction**

In Python or Postman:
```python
import requests

response = requests.post(
    "http://localhost:8000/predictions/sleep",
    json={
        "total_steps": 10198,
        "very_active_minutes": 17,
        "fairly_active_minutes": 20,
        "lightly_active_minutes": 195,
        "sedentary_minutes": 1208,
        "calories": 1755,
        "avg_steps_7d": 12157.0,
        "prev_day_sleep": 480.0,
        "is_weekend": 0
    }
)

print(response.json())
```

---

## 📁 Project Structure

```
MindTrack/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI app
│   │   ├── routers/          # API endpoints
│   │   ├── models/           # Database models
│   │   ├── services/         # Business logic
│   │   └── db/
│   │       └── database.py   # DB config
│   └── requirements.txt
├── frontend/
│   └── MindTracker_frontend/
│       ├── app.py           # Main Streamlit app
│       ├── pages/           # Streamlit pages
│       └── utils/
│           └── api.py      # API client
├── data/
│   ├── dataset.csv          # Training data
│   ├── additional_dataset.csv
│   └── pipeline.pkl        # Trained ML model
└── model/
    └── mindtrack_improved.ipynb
```

---

## 🔧 Troubleshooting

### **Issue 1: Module not found**
```cmd
# Make sure you're in the activated conda environment
conda activate mindtrack

# Verify installation
pip list | findstr streamlit fastapi
```

### **Issue 2: Port already in use**
```cmd
# Kill process on port 8000 (backend)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or change port in backend/.env
PORT=8001
```

### **Issue 3: ML pipeline not found**
```cmd
# Ensure pipeline.pkl exists in backend/../data/
# The path should be: MindTrack/backend/data/pipeline.pkl
```

### **Issue 4: Database errors**
```cmd
# Delete database and recreate
cd backend
del mindtrack.db  # Windows
python app/main.py  # Will recreate tables
```

---

## 🎯 Integration Overview

```
┌─────────────────┐
│   Streamlit     │ ← User Interface
│   Frontend      │
└────────┬────────┘
         │ HTTP Requests
         ↓
┌─────────────────┐
│   FastAPI       │ ← API Layer
│   Backend       │
└────────┬────────┘
         │ ORM
         ↓
┌─────────────────┐      ┌─────────────────┐
│   SQLAlchemy    │      │   ML Pipeline   │
│   Database      │      │   (pipeline.pkl) │
└─────────────────┘      └─────────────────┘
```

### **Data Flow:**

1. **User creates account** → Frontend → Backend API → Database
2. **User tracks habits** → Frontend → Backend API → Database
3. **User views insights** → Frontend → Backend API → Analytics
4. **User requests ML prediction** → Frontend → Backend API → ML Pipeline → Result

---

## 📊 Current Status Summary

| Component | Status | Connected To |
|-----------|--------|--------------|
| Frontend | ✅ Ready | Backend API |
| Backend API | ✅ Ready | Database + ML |
| Database | ✅ Ready | SQLAlchemy |
| ML Model | ✅ Ready | Backend API |
| **Overall** | **🟢 READY** | **85% Integrated** |

**Note:** Frontend UI for ML predictions needs to be added.

---

## 🚀 Next Steps

1. **Run the app** using instructions above
2. **Test all features** via the frontend
3. **Add ML prediction UI** to frontend pages
4. **Deploy** to production server

---

**Ready to run! Follow the steps above to start the application.**

