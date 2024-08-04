#!/usr/bin/env bash

# Define variables
CONTAINER_NAME="podscape"
IMAGE_NAME="podscape:dev"
DOCKERFILE="Dockerfile.dev"

# Stop and remove the container if it already exists
if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
    echo "Stopping and removing existing container..."
    docker stop ${CONTAINER_NAME} || echo "Failed to stop container."
    docker rm ${CONTAINER_NAME} || echo "Failed to remove container."
fi

# Build the Docker image
echo "Building Docker image..."
docker build -t ${IMAGE_NAME} . -f ${DOCKERFILE} || { echo "Failed to build Docker image."; exit 1; }

# Remove the .lib directory on the local OS, if it already exists
# if [ -d "${PWD}/.lib" ]; then
#     echo "Removing existing .lib directory..."
#     rm -rf ${PWD}/.lib || { echo "Failed to remove .lib directory."; exit 1; }
# fi

# Run the Docker container and mount the current host directory in the container
echo "Starting Docker container..."
# docker run -t -d --name ${CONTAINER_NAME} --net=host --volume "${PWD}":/app --volume "${PWD}/.lib":/usr/local/lib/python3.12/site-packages ${IMAGE_NAME} || { echo "Failed to start Docker container."; exit 1; }
docker run -t -d --name ${CONTAINER_NAME} --net=host --volume "${PWD}":/app ${IMAGE_NAME} || { echo "Failed to start Docker container."; exit 1; }

# Copy python libs from container to host
# echo "Copying python libs from container to host..."
# docker cp ${CONTAINER_NAME}:/usr/local/lib/python3.12/site-packages-copy/. ${PWD}/.lib
