#!/bin/bash

# Define the image name and tag
IMAGE_NAME="0x1115/shorten-url"

# Get the image tag from the first argument, default to "latest" if not provided
IMAGE_TAG=${1:-$(date +%s)}

# Build the Docker image
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} -t ${IMAGE_NAME}:latest -f build/applications/shorten-url/Dockerfile .

# Check if the build was successful
if [ $? -eq 0 ]; then
    echo "Docker image ${IMAGE_NAME}:${IMAGE_TAG} built successfully."
else
    echo "Failed to build Docker image ${IMAGE_NAME}:${IMAGE_TAG}."
    exit 1
fi