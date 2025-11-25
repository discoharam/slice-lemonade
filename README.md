# 🍋 Slice Lemonade

AI-powered audio separation tool that separates vocals and instruments from any audio file using Demucs and RunPod GPU acceleration.

## Features

- 🎵 Separate audio into vocals, drums, bass, and other instruments
- ⚡ GPU-accelerated processing via RunPod Serverless
- 🎨 Beautiful, responsive React + TypeScript frontend
- 🔄 Real-time progress tracking
- 📥 Direct download of separated tracks
- 💰 Pay-per-use pricing (only pay for processing time)

## Architecture

- **Frontend**: React + TypeScript + Tailwind CSS + Vite
- **Backend**: Flask + Python
- **AI Processing**: Demucs on RunPod Serverless GPU
- **Deployment**: Render.com (backend) + RunPod (AI processing)

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- RunPod account with credits
- Docker (for RunPod deployment)

### Local Development

1. **Clone and setup**:
   ```bash
   git clone <your-repo>
   cd slice-lemonade
   chmod +x scripts/setup.sh
   ./scripts/setup.sh