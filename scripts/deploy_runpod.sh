#!/bin/bash

echo "🚀 Deploying to RunPod..."

cd runpod

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t slice-lemonade-demucs:latest .

# Tag for Docker Hub (replace with your username)
echo "🏷️  Tagging image..."
docker tag slice-lemonade-demucs:latest yourusername/slice-lemonade-demucs:latest

# Push to Docker Hub
echo "📤 Pushing to Docker Hub..."
docker push yourusername/slice-lemonade-demucs:latest

echo "✅ Image pushed to Docker Hub!"
echo ""
echo "Next steps:"
echo "1. Go to https://runpod.io/console/serverless"
echo "2. Create a new template with your Docker image"
echo "3. Deploy an endpoint from the template"
echo "4. Update your backend/.env with the new endpoint ID"