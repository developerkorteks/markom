#!/bin/bash

# Markom Merchandise System - Start Script
# This script starts the Django application using PM2

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║         Starting Markom Merchandise System                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Change to project directory
cd /root/markom

# Activate virtual environment
source /root/markom/venv/bin/activate

echo "✓ Virtual environment activated"

# Run migrations (if any pending)
echo "✓ Checking for database migrations..."
python manage.py migrate --noinput

# Collect static files (for production)
# echo "✓ Collecting static files..."
# python manage.py collectstatic --noinput

# Create logs directory if not exists
mkdir -p /root/markom/logs

echo "✓ Logs directory ready"

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "❌ PM2 is not installed!"
    echo "   Install with: npm install -g pm2"
    exit 1
fi

echo "✓ PM2 is installed"

# Stop existing instance if running
pm2 stop markom-merchandise 2>/dev/null || true
pm2 delete markom-merchandise 2>/dev/null || true

echo "✓ Cleaned up old instances"

# Start with PM2
echo "✓ Starting application with PM2..."
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Setup PM2 startup (optional, for auto-start on boot)
# pm2 startup

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    ✅ STARTED SUCCESSFULLY                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Status: pm2 status"
echo "📋 Logs: pm2 logs markom-merchandise"
echo "🔄 Restart: pm2 restart markom-merchandise"
echo "⏹️  Stop: pm2 stop markom-merchandise"
echo ""
echo "🌐 Access: http://localhost:50456"
echo ""

# Show status
pm2 status
