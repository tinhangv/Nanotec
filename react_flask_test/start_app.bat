@echo off
echo Starting Flask backend...
start cmd /k "venv\Scripts\activate && cd backend && python app.py"

echo Starting React frontend...
start cmd /k "cd frontend && npm start"
