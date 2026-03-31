#!/bin/bash

# Markom Merchandise System - Stop Script

echo "Stopping Markom Merchandise System..."

pm2 stop markom-merchandise
pm2 delete markom-merchandise

echo "✅ Application stopped"
