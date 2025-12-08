cd C:\DEV\Slice Lemonade
echo "🔧 Building Docker image for Demucs htdemucs..."
cd runpod
docker build -t ghcr.io/discoharam/slice-lemonade:clean-demucs .
echo "🚀 Pushing to GitHub Container Registry..."
docker push ghcr.io/discoharam/slice-lemonade:clean-demucs
echo "✅ Image pushed: ghcr.io/discoharam/slice-lemonade:clean-demucs"
echo ""
echo "📋 MANUAL STEPS REQUIRED:"
echo "1. Go to RunPod Console: https://www.runpod.io/console/serverless"
echo "2. Find 'Slice Lemonade' template"
echo "3. Edit template → Update Docker image to:"
echo "   ghcr.io/discoharam/slice-lemonade:clean-demucs"
echo "4. Save template"
echo "5. Go to Endpoints: https://www.runpod.io/console/endpoints"
echo "6. Find endpoint 8y3bd1tz05fj3p"
echo "7. Click 'Refresh'"
echo "8. Wait 3-5 minutes for workers to update"
