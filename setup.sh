al#!/bin/bash

# SME-Pulse AI - Setup Script
# This script sets up the complete development environment

set -e  # Exit on error

echo "🚀 SME-Pulse AI Setup Script"
echo "============================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if command -v python3 &> /dev/null; then
    print_status "Python 3 is installed ($(python3 --version))"
else
    print_error "Python 3 is not installed. Please install Python 3.8+"
    exit 1
fi

# Check pip
if command -v pip3 &> /dev/null; then
    print_status "pip3 is installed"
else
    print_error "pip3 is not installed. Please install pip"
    exit 1
fi

# Check Node.js
if command -v node &> /dev/null; then
    print_status "Node.js is installed ($(node --version))"
else
    print_warning "Node.js is not installed. Frontend setup will be skipped."
fi

# Check Docker
if command -v docker &> /dev/null; then
    print_status "Docker is installed"
else
    print_warning "Docker is not installed. Docker setup will be skipped."
fi

echo ""

# Setup Backend
echo "🐍 Setting up Backend..."
echo "------------------------"

# Create virtual environment
if [ ! -d "backend/venv" ]; then
    python3 -m venv backend/venv
    print_status "Created Python virtual environment"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source backend/venv/bin/activate

# Install backend dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r backend/requirements.txt
print_status "Installed backend dependencies"

deactivate

echo ""

# Setup Frontend
echo "⚛️  Setting up Frontend..."
echo "--------------------------"

if command -v npm &> /dev/null; then
    cd frontend
    npm install
    print_status "Installed frontend dependencies"
    cd ..
else
    print_warning "Skipping frontend setup (npm not available)"
fi

echo ""

# Setup Database
echo "🗄️  Database Setup"
echo "------------------"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    print_status "Created .env file from template"
    print_warning "Please update .env with your configuration"
else
    print_status ".env file already exists"
fi

echo ""

# Final instructions
echo "✅ Setup Complete!"
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Update the .env file with your configuration:"
echo "   nano .env"
echo ""
echo "2. Start the database (if using Docker):"
echo "   docker-compose up -d postgres"
echo ""
echo "3. Start the backend server:"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "4. Start the frontend (in a new terminal):"
echo "   cd frontend && npm run dev"
echo ""
echo "5. Access the application:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Documentation: http://localhost:8000/api/docs"
echo ""
echo "📚 For more information, see README.md"

