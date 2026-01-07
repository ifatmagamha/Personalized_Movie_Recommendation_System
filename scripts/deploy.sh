#!/bin/bash
echo "Deploying in Docker..."
docker-compose up -d
echo "Frontend: http://localhost:80"
echo "Backend: http://localhost:8000"
