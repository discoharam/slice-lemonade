#!/bin/bash

echo "🍋 Setting up Slice Lemonade..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp ../runpod/.env.example .env
    echo "⚠️  Please update backend/.env with your RunPod API keys"
fi

cd ..

# Setup frontend
echo "📦 Setting up React frontend..."
cd frontend
npm install

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "VITE_API_URL=http://localhost:5000" > .env
fi

cd ..

echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update backend/.env with your RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID"
echo "2. Start backend: cd backend && source venv/bin/activate && python run.py"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Open http://localhost:3000"