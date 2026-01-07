#!/bin/bash
echo "Cleaning up Docker resources..."
docker-compose down --rmi all --volumes --remove-orphans
