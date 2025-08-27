#!/bin/bash

# Installation script for Proxmox LXC
# Run as: bash install-altaiclockin.sh

set -e

echo "🚀 Installing Altaiclockin API on LXC..."

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl enable docker
    systemctl start docker
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Installing..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

echo "✅ Docker and Docker Compose are ready"

# Create directory for the application
mkdir -p /opt/altaiclockin
cd /opt/altaiclockin

echo "📦 Loading Docker image..."
if [ -f "altaiclockin-api-slim.tar" ]; then
    docker load -i altaiclockin-api-slim.tar
    echo "✅ Image loaded successfully"
else
    echo "❌ altaiclockin-api-slim.tar file not found"
    echo "   Make sure it's in the current directory"
    exit 1
fi

echo "🐳 Starting services..."
docker-compose up -d

echo "⏳ Waiting for the service to be ready..."
sleep 10

# Check if it works
if curl -f http://localhost:8990/status > /dev/null 2>&1; then
    echo "✅ Altaiclockin API is working correctly!"
    echo "🌐 Accessible at: http://$(hostname -I | awk '{print $1}'):8990"
    echo ""
    echo "📋 Useful commands:"
    echo "   View logs: docker-compose logs -f"
    echo "   Stop: docker-compose down"
    echo "   Restart: docker-compose restart"
    echo "   Status: docker-compose ps"
else
    echo "❌ Error: The service is not responding"
    echo "   Check the logs: docker-compose logs"
fi
