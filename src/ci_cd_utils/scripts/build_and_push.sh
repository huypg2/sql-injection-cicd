#!/bin/bash
IMAGE_NAME="yourdockerhub/detection-api:latest"

echo "Building docker image..."
docker build -t $IMAGE_NAME ../../src/detection_api

echo "Pushing to DockerHub..."
docker push $IMAGE_NAME
