@echo off
setlocal enabledelayedexpansion

echo 🚀 Deploying to GitHub Container Registry...

if "%1"=="" (
    echo ❌ Usage: deploy_ghcr.bat YOUR_GITHUB_USERNAME YOUR_GITHUB_TOKEN
    exit /b 1
)

if "%2"=="" (
    echo ❌ Usage: deploy_ghcr.bat YOUR_GITHUB_USERNAME YOUR_GITHUB_TOKEN  
    exit /b 1
)

set GITHUB_USERNAME=%1
set GITHUB_TOKEN=%2
set IMAGE_TAG=latest

cd runpod

echo 🐳 Building Docker image...
docker build -t slice-lemonade-demucs:%IMAGE_TAG% .

if errorlevel 1 (
    echo ❌ Docker build failed
    exit /b 1
)

echo 🏷️ Tagging image for GHCR...
set IMAGE_NAME=ghcr.io/%GITHUB_USERNAME%/slice-lemonade-demucs:%IMAGE_TAG%
docker tag slice-lemonade-demucs:%IMAGE_TAG% %IMAGE_NAME%

if errorlevel 1 (
    echo ❌ Docker tag failed
    exit /b 1
)

echo 🔐 Logging in to GHCR...
echo %GITHUB_TOKEN% | docker login ghcr.io -u %GITHUB_USERNAME% --password-stdin

if errorlevel 1 (
    echo ❌ Docker login failed
    exit /b 1
)

echo 📤 Pushing image to GHCR...
docker push %IMAGE_NAME%

if errorlevel 1 (
    echo ❌ Docker push failed
    exit /b 1
)

echo ✅ Successfully deployed to GHCR!
echo.
echo 📦 Image URL: %IMAGE_NAME%
echo.
echo Next steps:
echo 1. Go to RunPod Console → Serverless → Templates
echo 2. Create new template with image: %IMAGE_NAME%
echo 3. Deploy endpoint and update backend/.env

cd ..