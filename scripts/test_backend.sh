#!/bin/bash

echo "🧪 Testing Slice Lemonade Backend..."

cd backend
source venv/bin/activate

# Test if server starts
echo "Starting test server..."
python run.py &

SERVER_PID=$!
sleep 3

# Test health endpoint
echo "Testing health endpoint..."
curl -f http://localhost:5000/api/health

if [ $? -eq 0 ]; then
    echo "✅ Backend is healthy!"
else
    echo "❌ Backend health check failed"
    kill $SERVER_PID
    exit 1
fi

# Kill test server
kill $SERVER_PID

echo "✅ All tests passed!"