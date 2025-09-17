#!/bin/bash

# Zcash Transaction API Launch Script
# This script launches only the backend transaction API server

set -e  # Exit on any error

echo "🚀 Starting Zcash Transaction API..."
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.8+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 is available${NC}"

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/zchat/backend"

# Backend Setup
echo -e "\n${BLUE}Setting up Backend...${NC}"
cd "$BACKEND_DIR"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install backend dependencies
echo -e "${YELLOW}Installing backend dependencies...${NC}"
pip install -r requirements.txt

# Function to cleanup processes on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down server...${NC}"
    
    # Kill backend process
    if [ ! -z "$BACKEND_PID" ] && kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null
        sleep 1
        # Force kill if still running
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill -9 $BACKEND_PID 2>/dev/null
        fi
        echo -e "${GREEN}✅ Backend server stopped${NC}"
    fi
    
    # Kill any remaining processes that might be hanging
    pkill -f "uvicorn app.main_transactions:app" 2>/dev/null || true
    
    echo -e "${GREEN}🏁 Server stopped${NC}"
    exit 0
}

# Trap SIGINT and SIGTERM to cleanup
trap cleanup SIGINT SIGTERM

# Start Backend Server
echo -e "\n${BLUE}🔥 Starting Zcash Transaction API Server...${NC}"
cd "$BACKEND_DIR"
source venv/bin/activate

# Use the new transaction-focused main file
uvicorn app.main_transactions:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Display information
echo -e "\n${GREEN}🎉 Zcash Transaction API is now running!${NC}"
echo -e "=================================="
echo -e "${BLUE}📡 Transaction API:${NC} http://localhost:8000"
echo -e "${BLUE}📚 API Docs:${NC} http://localhost:8000/docs"
echo -e "${BLUE}🏥 Health Check:${NC} http://localhost:8000/health"
echo -e "=================================="
echo -e "${YELLOW}Available Endpoints:${NC}"
echo -e "  • POST /register/ - Register new user"
echo -e "  • POST /login/ - User login"
echo -e "  • GET /users/me/ - Get user info"
echo -e "  • POST /zcash/send/ - Send Zcash"
echo -e "  • GET /zcash/balance/ - Get balance"
echo -e "  • GET /zcash/address/ - Get addresses"
echo -e "  • POST /zcash/validate-address/ - Validate address"
echo -e "=================================="
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"

# Wait for process
while kill -0 $BACKEND_PID 2>/dev/null; do
    sleep 1
done

echo -e "${GREEN}🏁 Process has ended${NC}"
