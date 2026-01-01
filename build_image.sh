#!/bin/bash
# Script to build and export the Docker image as a .tar file for your NAS or Server

IMAGE_NAME="snapshot-mirror"
TAG="latest"
OUTPUT_FILE="${IMAGE_NAME}.tar"

echo "🔨 Building Docker image (AMD64 for NAS/Server): ${IMAGE_NAME}:${TAG}..."
docker build --platform linux/amd64 -t "${IMAGE_NAME}:${TAG}" .

if [ $? -eq 0 ]; then
    echo "✅ Build successful."
    echo "📦 Exporting image to ${OUTPUT_FILE}..."
    docker save "${IMAGE_NAME}:${TAG}" > "${OUTPUT_FILE}"
    echo "✨ Done! You can now upload '${OUTPUT_FILE}' to your NAS or target server."
    echo "   Example (Synology): Container Manager -> Image -> Import -> Add -> From file"
else
    echo "❌ Build failed. Please check the errors above."
    exit 1
fi
