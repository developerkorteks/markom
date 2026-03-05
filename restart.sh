#!/bin/bash

# Markom Merchandise System - Restart Script

echo "Restarting Markom Merchandise System..."

# Activate virtual environment
source /root/markom/venv/bin/activate

# Run migrations if any
python manage.py migrate --noinput

# Restart PM2 process
pm2 restart markom-merchandise

echo "✅ Application restarted"
pm2 status
