# 🧠 MindTrack - Habit Tracking Application

NOTE: This repository was recently reorganized — dataset and ML artifacts were moved into the
`backend/data/` folder and the training notebook moved into `backend/model/`. See the
"Running the Application" section below for updated paths. This small change keeps the
backend ML pipeline path consistent with the code (no code changes required).

MindTrack is a comprehensive habit tracking application with ML-powered insights and analytics. It helps users build healthy habits through consistent tracking, visualizations, and personalized recommendations.

## 🎯 Features

- **Habit Tracking**: Daily tracking with done/partial/missed status
- **Streak Analytics**: Current and best streak tracking for motivation
- **Gamification**: Badge system for milestone achievements
- **ML Insights**: AI-powered predictions and recommendations
- **Calendar View**: Visual heatmap of your progress
- **Activity Analytics**: Integration with sensor data for deeper insights

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (default) or PostgreSQL
- **API Endpoints**: RESTful API for CRUD operations
- **ML Integration**: Pre-trained pipeline for sleep prediction

### Frontend (Streamlit)
- **Framework**: Streamlit for rapid UI development
- **Pages**: Dashboard, Calendar, Insights, Reminders, Settings
- **API Integration**: HTTP client for backend communication

### ML/Analytics
- **Model**: Random Forest Regressor for sleep prediction
- **Features**: Activity metrics, rolling averages, lag features
- **Pipeline**: Preprocessing, scaling, and prediction pipeline

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Backend Setup

```bash
cd MindTrack/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Initialize database
python -m alembic upgrade head  # Optional: if using Alembic

# Run backend server
python app/main.py
```

Backend API will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

### Frontend Setup

```bash
cd MindTrack/frontend

# Install Streamlit (if not already installed)
pip install streamlit pandas plotly requests

# Run Streamlit app
streamlit run MindTracker_frontend/app.py
```

Frontend will be available at: http://localhost:8501

## 🚀 Usage

### Starting the Application

1. **Start Backend**:
   ```bash
   cd MindTrack/backend
   python app/main.py
   ```

2. **Start Frontend** (in new terminal):
   ```bash
   cd MindTrack/frontend
   streamlit run MindTracker_frontend/app.py
   ```

3. **Access Application**:
   - Open browser to http://localhost:8501
   - Create a demo user
   - Select habits to track
   - Start tracking!

### API Endpoints

- `POST /users/` - Create new user
- `GET /users/{user_id}` - Get user details
- `POST /habits/` - Create habit entry
- `GET /habits/user/{user_id}` - Get user habits
- `POST /badges/award-check/{user_id}` - Check and award badges
- `GET /insights/user/{user_id}` - Get insights and recommendations
- `POST /predictions/sleep` - Predict sleep duration

## 📊 Data Model

### Core Entities

1. **User**: User account with preferences and timezone
2. **HabitEntry**: Daily habit tracking entries
3. **Badge**: Achievement badges for milestones
4. **Reminder**: Scheduled reminders for habits
5. **SensorSummary**: Activity data from wearables

## 🔬 ML Model

The ML pipeline (`backend/data/pipeline.pkl`) predicts sleep duration based on:
- Total steps
- Active minutes (very/fairly/lightly)
- Sedentary time
- Calories burned
- 7-day rolling averages
- Previous day's sleep

### Using the ML Prediction API

```python
from utils.api import api

prediction = api.predict_sleep(
    total_steps=10198,
    very_active_minutes=17,
    fairly_active_minutes=20,
    lightly_active_minutes=195,
    sedentary_minutes=1208,
    calories=1755,
    avg_steps_7d=12157.0,
    prev_day_sleep=480.0,
    is_weekend=0
)

print(f"Predicted sleep: {prediction['predicted_sleep_formatted']}")
```

## 🧪 Testing

```bash
# Run backend tests
cd MindTrack/backend
pytest app/tests/

# Run specific test
pytest app/tests/test_user.py
```

## 📁 Project Structure

```
MindTrack/
├── backend/
│   ├── app/
│   │   ├── db/
│   │   └── database.py          # Database setup
│   ├── models/                  # SQLAlchemy models
│   ├── services/                # Business logic
│   ├── routers/                 # API endpoints
│   ├── tests/                   # Unit tests
│   └── main.py                  # FastAPI app
├── frontend/
│   └── MindTracker_frontend/
│       ├── app.py              # Main Streamlit app
│       ├── pages/              # Streamlit pages
│       └── utils/
│           └── api.py         # API client
├── backend/data/
│   ├── dataset.csv            # Activity dataset
│   ├── additional_dataset.csv  # Habit entries
│   └── pipeline.pkl           # Trained ML model
└── model/
    └── mindtrack_improved.ipynb # ML training notebook
```

## 🔧 Configuration

### Environment Variables

- `DATABASE_URL`: Database connection string
- `API_HOST`: Backend host (default: 0.0.0.0)
- `API_PORT`: Backend port (default: 8000)
- `SECRET_KEY`: Secret key for JWT (in production)

### Database

Default: SQLite (`mindtrack.db`)
Production: PostgreSQL (update `DATABASE_URL` in `.env`)

## 🎯 Future Enhancements

- [ ] JWT authentication
- [ ] Real-time notifications
- [ ] Mobile app (React Native)
- [ ] Advanced ML models
- [ ] Integration with wearable APIs
- [ ] Social features (sharing, challenges)

## 📄 License

MIT License

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## 📞 Support

For questions or issues, please open a GitHub issue.

---

**Built with ❤️ using FastAPI, Streamlit, and Scikit-learn**

