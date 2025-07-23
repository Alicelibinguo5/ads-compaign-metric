#!/bin/bash

# Dashboard Setup Script for Ads Campaign Metrics
# This script helps set up the Apache Superset dashboard

set -e  # Exit on any error

echo "🚀 Setting up Apache Superset Dashboard for Campaign Metrics"
echo "=========================================================="

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if poetry is available
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install poetry first."
    echo "   Install with: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
poetry install

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    exit 1
fi

# Check if docker compose is available
if ! docker compose version &> /dev/null; then
    echo "⚠️  Docker Compose not available, trying docker-compose..."
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Neither 'docker compose' nor 'docker-compose' is available"
        exit 1
    fi
fi

# Stop any existing containers
echo "🛑 Stopping any existing containers..."
if docker compose version &> /dev/null; then
    docker compose down 2>/dev/null || true
else
    docker-compose down 2>/dev/null || true
fi

# Start services
echo "🚀 Starting services with Docker Compose..."
if docker compose version &> /dev/null; then
    docker compose up -d
else
    docker-compose up -d
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if Superset is accessible
echo "🔍 Checking if Superset is accessible..."
for i in {1..30}; do
    if curl -s http://localhost:8088/health &> /dev/null; then
        echo "✅ Superset is accessible!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠️  Superset may still be starting up..."
    fi
    sleep 2
done

# Run dashboard setup
echo "📊 Setting up dashboard..."
poetry run python src/superset/simple_dashboard_setup.py

echo ""
echo "🎉 Dashboard setup completed!"
echo "=========================================================="
echo "📊 Access your dashboard at: http://localhost:8088"
echo "👤 Username: admin"
echo "🔑 Password: admin"
echo ""
echo "📖 For detailed setup instructions, see: docs/superset_dashboard_guide.md"
echo "🔧 If you encounter issues, check the troubleshooting section in the guide"
echo ""
echo "Happy analyzing! 📈" 