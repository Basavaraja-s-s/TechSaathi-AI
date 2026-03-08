@echo off
echo Starting TechSaathi AI - Smart Study Copilot...
echo.
echo Make sure you have:
echo 1. Installed dependencies: pip install -r requirements.txt
echo 2. Created .env file with your API keys
echo.
uvicorn main:app --reload
