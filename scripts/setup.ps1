# Slice Lemonade Setup Script for Windows
Write-Host "🍋 Setting up Slice Lemonade..." -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan

# Backend setup
Write-Host "
Setting up backend..." -ForegroundColor Yellow
cd ../backend

# Create virtual environment
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "Created virtual environment" -ForegroundColor Green
}

# Activate virtual environment
.\venv\Scripts\Activate

# Install requirements
pip install -r requirements.txt

# Create .env from example if it doesn't exist
if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "Created .env file from example" -ForegroundColor Green
    Write-Host "PLEASE UPDATE backend/.env with your RunPod API key and endpoint ID!" -ForegroundColor Red
}

deactivate
cd ..

# Frontend setup
Write-Host "
Setting up frontend..." -ForegroundColor Yellow
cd frontend

# Install npm packages
npm install

# Create .env if it doesn't exist
if (-not (Test-Path ".env")) {
    "VITE_API_URL=http://localhost:5000/api" | Out-File -FilePath .env -Encoding UTF8
    Write-Host "Created frontend .env file" -ForegroundColor Green
}

cd ..

Write-Host "
✅ Setup complete!" -ForegroundColor Green
Write-Host "
📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Update backend/.env with your RunPod credentials"
Write-Host "2. Start backend: cd backend; python run.py"
Write-Host "3. Start frontend: cd frontend; npm run dev"
Write-Host "4. Open http://localhost:3000"
Write-Host "
🐳 For RunPod deployment:"
Write-Host "1. Push to GitHub to trigger Docker build"
Write-Host "2. Update RunPod endpoint with new image: ghcr.io/discoharam/slice-lemonade:latest"