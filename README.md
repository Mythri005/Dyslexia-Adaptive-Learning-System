🎯 Dyslexia Adaptive Learning System

A Full-Stack AI-Based Adaptive Learning Platform designed to support children with dyslexia through intelligent, real-time personalized learning.

The system dynamically adjusts question difficulty using:

✅ Accuracy
❤️ Pulse Rate
👁 Camera Attention
🧠 Stress Level

🚀 Project Overview

This project consists of:

🔹 React Frontend
🔹 Flask Backend
🔹 Rule-Based AI Adaptive Algorithm
🔹 Real-Time Camera Monitoring (OpenCV + MediaPipe)
🔹 Pulse Sensor Integration (ESP32 + MAX30102)
🔹 Speech Recognition System (Web Speech API)
🔹 Performance & Progress Analytics

The system continuously analyzes user behavior and performance to adapt difficulty after every question attempt.

🧠 Core Features
🎯 Learning Modules

🧮 Math Module
🔤 Spelling Module
📖 Reading Module

Each module dynamically updates difficulty based on real-time performance and physiological inputs.

📊 Real-Time Adaptive System

Difficulty is adjusted using:

Accuracy + Stress Level + Attention Score + Pulse Rate

Adaptive Logic

Lower stress → Increase difficulty

High stress → Decrease difficulty

Poor attention → Reduce difficulty

High accuracy + Calm state → Increase challenge

All four factors contribute equally (25% each) to compute the adaptive score.

The adaptive system is implemented using a rule-based AI decision engine, not machine learning training models.

👁 Camera-Based Attention Monitoring

Implemented using OpenCV + MediaPipe.

Features include:

Face detection

Eye detection

Head pose tracking

Multiple face detection

Looking-away detection

Attention score computation

If camera is unavailable, the system safely falls back to performance-based adaptation.

❤️ Pulse Monitoring

Hardware Used:

ESP32 Microcontroller

MAX30102 Pulse Sensor

Working:

MAX30102 connected via I2C to ESP32

ESP32 sends pulse data via USB Serial

Browser reads pulse using Web Serial API

Pulse variation contributes to stress estimation

Pulse influences adaptive difficulty decisions

If pulse sensor is not connected, system continues using accuracy + attention logic.

🎤 Speech Recognition

Used in Reading Module.

Features:

Voice recording

Speech-to-text conversion

Pronunciation evaluation

Browser-based Web Speech API

No external speech AI model is hosted on backend.

📈 Progress Tracking

System tracks:

Accuracy percentage

Streak tracking

Stress trend analysis

Attention history

Session analytics

Performance reports

Data stored using SQLite + SQLAlchemy ORM.

🔌 Hardware Components

🛠 Hardware Used:

ESP32

MAX30102 Pulse Sensor

USB Serial Communication

Webcam

🏗 Technology Stack
🔹 Frontend

React 18

React Router DOM

Context API + Hooks

Axios (REST API Communication)

Web Serial API

Web Speech API

CSS3 (Responsive UI)

🔹 Backend

Python 3.11

Flask

SQLAlchemy

SQLite

OpenCV

MediaPipe

REST API Architecture

🔗 Frontend–Backend Architecture

User
↓
React Frontend (Port 3000)
↓ (Axios – REST API)
Flask Backend (Port 5001)
↓
Adaptive Algorithm Engine
↓
SQLite Database

The frontend communicates with the backend using REST APIs via Axios.

No WebSocket communication is used.

🔄 How Adaptive System Works

For each question:

Student answers question

Accuracy is updated

Camera analyzes attention

Pulse rate captured (if connected)

Stress level estimated

Adaptive algorithm computes adaptive score

Difficulty updated

Next question fetched from dataset

This ensures per-question adaptive personalization.

🧮 Key Variables
Variable	Description
accuracy_score	Ratio of correct answers to total questions
stress_level	Stress value (0–1) from pulse + performance
pulse_rate	Real-time BPM from MAX30102
attention_score	Camera-based attention score (0–100)
difficulty_level	Current level (easy / medium / difficult)
adaptive_score	Combined weighted score
streak_count	Consecutive correct answers
performance_points	Reward points earned
💻 System Requirements
Minimum Hardware

Intel i5 or equivalent

8GB RAM

Webcam

USB Port (for ESP32)

Software

Python 3.10+

Node.js 16+

Chrome Browser (recommended for Web Serial + Speech API)

Windows 10 / 11

⚙ Installation Guide
1️⃣ Backend Setup
cd Dyslexia_Adaptive_backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py

Backend runs at:

http://localhost:5001

2️⃣ Frontend Setup
cd dyslexia-frontend
npm install
npm start

Frontend runs at:

http://localhost:3000

🧪 Testing

To test camera integration:

python camera_integration.py

To test backend:

python run.py

To test full system:

Start backend

Start frontend

Open browser

Attempt questions

Observe adaptive difficulty changes

📦 .gitignore
venv/
node_modules/
__pycache__/
build/
📌 Key Highlights

✔ Per-question adaptive difficulty
✔ Multi-parameter decision logic
✔ Camera-based attention monitoring
✔ Hardware pulse integration
✔ Dataset-driven structured system
✔ Modular full-stack architecture
✔ Research-oriented assistive prototypes