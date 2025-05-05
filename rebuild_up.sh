#!/bin/bash

echo "Stopping and removing existing containers..."
docker compose down

echo "Building images without cache..."
docker compose build --no-cache

echo "Starting services in detached mode..."
docker compose up -d

echo "Done!"
