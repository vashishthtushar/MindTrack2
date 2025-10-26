# 🚀 Quick Start Guide for Anaconda

## Connection Status Summary

**✅ What's Connected:**
- ✅ Frontend → Backend API
- ✅ Backend API → Database
- ✅ Backend API → ML Model
- ⚠️ Frontend → ML Predictions (endpoint ready, UI not added)

**Integration Level: 85% Complete**

---

## 🎯 Quick Start (Copy-Paste Commands)

### **Step 1: Open Anaconda Prompt**

### **Step 2: Navigate to Project**
```cmd
cd C:\Users\USER\Downloads\MindTrack2\MindTrack
```

### **Step 3: Create Environment & Install**
```cmd
conda create -n mindtrack python=3.10 -y
conda activate mindtrack
cd backend && pip install -r requirements.txt
cd ../frontend && pip install -r requirements.txt
cd ..
```

### **Step 4: Run Application**

**Terminal 1 (Backend):**
```cmd
conda activate mindtrack
cd backend
python app/main.py
```
✅ Backend running at http://localhost:8000

**Terminal 2 (Frontend):**
```cmd
conda activate mindtrack
cd frontend
streamlit run MindTracker_frontend/app.py
```
✅ Frontend running at http://localhost:8501

---

## 🧪 Test Integration

### **1. Test Backend**
Open browser: http://localhost:8000
Should see: `{"message": "MindTrack API is running"}`

### **2. Test API Docs**
Open browser: http://localhost:8000/docs

### **3. Test ML Pipeline**
Open browser: http://localhost:8000/predictions/health
Should see: `{"status": "available"}`

### **4. Test Frontend**
Open browser: http://localhost:8501

---

## 📋 What's Working

✅ User creation via API
✅ Habit tracking saves to database
✅ Streak calculation
✅ Badge awarding
✅ Insights from backend
✅ ML predictions (via API)

---

## 🎉 You're Ready!

Access the app at: **http://localhost:8501**

