@echo off
REM Quick deployment script for Windows

echo ========================================
echo Rubik's Cube Recorder - Git Push Script
echo ========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing git repository...
    git init
    git branch -M main
)

echo Adding all files...
git add .

echo.
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Update Rubik's Cube Recorder app

echo Committing changes...
git commit -m "%commit_msg%"

echo.
echo Checking remote...
git remote -v

REM Check if remote exists
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo.
    echo No remote found. Please add your GitHub repository:
    echo git remote add origin https://github.com/BartonChenTW/Rubik-s-cube-recorder.git
    echo.
    echo Then run: git push -u origin main
    pause
    exit /b
)

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo ========================================
echo Done! Your code is now on GitHub.
echo.
echo Next steps:
echo 1. Go to https://share.streamlit.io/
echo 2. Sign in with GitHub
echo 3. Click "New app"
echo 4. Select your repository
echo 5. Click "Deploy!"
echo ========================================
pause
