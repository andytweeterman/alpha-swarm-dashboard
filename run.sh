#!/bin/bash
# Alpha Swarm Startup Script

set -e  # Exit on error

echo "🚀 Starting Alpha Swarm Dashboard..."
echo "=================================="

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

# Install/upgrade dependencies
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt

# Create logs directory if it doesn't exist
mkdir -p logs

# Start Streamlit app
echo "✅ Configuration complete. Starting Streamlit..."
echo "📊 Dashboard available at: http://localhost:8501"
echo ""

streamlit run src/app.py
