#!/bin/bash

# HealthCredX Quick Start Script
# This script sets up and runs the HealthCredX platform

echo "============================================================"
echo "HealthCredX - Quick Start Setup"
echo "============================================================"
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed successfully"
echo ""

# Check for Gemini API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY not set (AI health analysis will not work)"
    echo "   To enable AI features, run:"
    echo "   export GEMINI_API_KEY='your_api_key_here'"
    echo ""
else
    echo "✓ GEMINI_API_KEY configured"
    echo ""
fi

# Create data directory if it doesn't exist
mkdir -p data

echo "============================================================"
echo "🚀 Starting HealthCredX Platform..."
echo "============================================================"
echo ""
echo "Access the application at: http://127.0.0.1:5000"
echo ""
echo "Available routes:"
echo "  - /          AI Health Reader (Patient View)"
echo "  - /verify    Certification Quiz (Staff View)"
echo "  - /dashboard Admin Dashboard (Hospital View)"
echo ""
echo "Press CTRL+C to stop the server"
echo "============================================================"
echo ""

# Run the Flask application
python3 app.py
