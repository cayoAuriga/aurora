#!/bin/bash
# Build script for Aurora shared libraries

echo "🚀 Building Aurora Shared Libraries..."

# Build base Docker image
echo "📦 Building base Docker image..."
docker build -f Dockerfile.base -t aurora/shared:base ..

if [ $? -eq 0 ]; then
    echo "✅ Base Docker image built successfully"
else
    echo "❌ Failed to build base Docker image"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing shared dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Shared dependencies installed successfully"
else
    echo "❌ Failed to install shared dependencies"
    exit 1
fi

# Make scripts executable
chmod +x generate_service.py

echo "✅ Aurora shared libraries built successfully!"
echo ""
echo "Usage examples:"
echo "  Generate new service: python generate_service.py my-service 8005"
echo "  Build service: docker build -t aurora/my-service ."
echo "  Run service: docker run -p 8005:8005 aurora/my-service"