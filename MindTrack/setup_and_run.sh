#!/bin/bash
# MindTrack Setup and Run Script for Anaconda

echo "🧠 Setting up MindTrack..."

# Navigate to project directory
cd "$(dirname "$0")"

# Create conda environment
echo "Creating conda environment 'mindtrack'..."
conda create -n mindtrack python=3.10 -y

# Activate environment
echo "Activating mindtrack environment..."
conda activate mindtrack

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
pip install -r requirements.txt
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the application:"
echo "1. Start backend: cd backend && python app/main.py"
echo "2. Start frontend: cd frontend && streamlit run MindTracker_frontend/app.py"
echo ""

