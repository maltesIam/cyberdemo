#!/bin/bash
#
# CyberDemo - Start Script
# Usage: ./start.sh [--generate-data] [--seed <number>]
#
# Options:
#   --generate-data    Generate synthetic test data after startup
#   --seed <number>    Seed for reproducible data generation (default: 42)
#   --stop             Stop all running services
#   --help             Show this help message
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GENERATE_DATA=false
SEED=42
STOP_ONLY=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --generate-data|-g)
            GENERATE_DATA=true
            shift
            ;;
        --seed|-s)
            SEED="$2"
            shift 2
            ;;
        --stop)
            STOP_ONLY=true
            shift
            ;;
        --help|-h)
            echo "CyberDemo - SOC Tier-1 Agentic AI Analyst Demo"
            echo ""
            echo "Usage: ./start.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --generate-data, -g    Generate synthetic test data after startup"
            echo "  --seed, -s <number>    Seed for reproducible data (default: 42)"
            echo "  --stop                 Stop all running services"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./start.sh                      # Start services only"
            echo "  ./start.sh --generate-data      # Start and generate data"
            echo "  ./start.sh -g -s 123            # Start with custom seed"
            echo "  ./start.sh --stop               # Stop all services"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Function to print colored status
print_status() {
    echo -e "${CYAN}[CyberDemo]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Function to stop all services
stop_services() {
    print_status "Stopping CyberDemo services..."

    # Stop frontend
    pkill -f "vite.*CyberDemo" 2>/dev/null && print_success "Frontend stopped" || true

    # Stop backend
    pkill -f "uvicorn.*src.main:app" 2>/dev/null && print_success "Backend stopped" || true

    # Stop Docker infrastructure
    cd "$SCRIPT_DIR/docker"
    docker-compose down 2>/dev/null && print_success "Infrastructure stopped" || true

    print_success "All services stopped"
}

# Handle stop command
if [ "$STOP_ONLY" = true ]; then
    stop_services
    exit 0
fi

# Check dependencies
check_dependencies() {
    print_status "Checking dependencies..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi

    if ! command -v uv &> /dev/null; then
        print_error "uv (Python package manager) is not installed"
        print_warning "Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi

    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed"
        exit 1
    fi

    print_success "All dependencies found"
}

# Start infrastructure
start_infrastructure() {
    print_status "Starting infrastructure (OpenSearch + PostgreSQL)..."
    cd "$SCRIPT_DIR/docker"

    # Use docker compose or docker-compose
    if docker compose version &> /dev/null; then
        docker compose up -d opensearch postgres
    else
        docker-compose up -d opensearch postgres
    fi

    print_success "Infrastructure started"

    # Wait for OpenSearch to be ready
    print_status "Waiting for OpenSearch to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
            print_success "OpenSearch is ready"
            return 0
        fi
        sleep 2
    done
    print_warning "OpenSearch may not be fully ready yet"
}

# Start backend
start_backend() {
    print_status "Starting backend (FastAPI)..."
    cd "$SCRIPT_DIR/backend"

    # Install dependencies if needed
    if [ ! -d ".venv" ]; then
        print_status "Installing Python dependencies..."
        uv sync
    fi

    # Start backend in background
    uv run uvicorn src.main:app --reload --port 8000 > /tmp/cyberdemo-backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > /tmp/cyberdemo-backend.pid

    # Wait for backend to be ready
    print_status "Waiting for backend to be ready..."
    for i in {1..20}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend is ready (PID: $BACKEND_PID)"
            return 0
        fi
        sleep 1
    done
    print_warning "Backend may not be fully ready yet (check /tmp/cyberdemo-backend.log)"
}

# Start frontend
start_frontend() {
    print_status "Starting frontend (React + Vite)..."
    cd "$SCRIPT_DIR/frontend"

    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_status "Installing Node dependencies..."
        npm install
    fi

    # Start frontend in background
    npm run dev > /tmp/cyberdemo-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > /tmp/cyberdemo-frontend.pid

    # Wait for frontend to be ready
    print_status "Waiting for frontend to be ready..."
    for i in {1..20}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            print_success "Frontend is ready (PID: $FRONTEND_PID)"
            return 0
        fi
        sleep 1
    done
    print_warning "Frontend may not be fully ready yet (check /tmp/cyberdemo-frontend.log)"
}

# Generate test data
generate_data() {
    print_status "Generating synthetic test data (seed: $SEED)..."

    # Reset indices first
    curl -s -X POST "http://localhost:8000/gen/reset" > /dev/null
    print_success "Indices reset"

    # Generate all data
    RESPONSE=$(curl -s -X POST "http://localhost:8000/gen/all?seed=$SEED")

    if echo "$RESPONSE" | grep -q "success"; then
        print_success "Test data generated successfully"

        # Show counts
        COUNTS=$(curl -s "http://localhost:8000/gen/health")
        echo ""
        print_status "Data counts:"
        echo "$COUNTS" | python3 -c "
import sys, json
data = json.load(sys.stdin)
counts = data.get('counts', {})
for k, v in sorted(counts.items()):
    print(f'  {k}: {v}')
" 2>/dev/null || echo "  (Could not parse counts)"
    else
        print_error "Failed to generate data: $RESPONSE"
    fi
}

# Main execution
main() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}     ${GREEN}CyberDemo${NC} - SOC Tier-1 Agentic AI Analyst Demo      ${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""

    check_dependencies
    echo ""

    start_infrastructure
    echo ""

    start_backend
    echo ""

    start_frontend
    echo ""

    if [ "$GENERATE_DATA" = true ]; then
        # Wait a bit more for services to stabilize
        sleep 2
        generate_data
        echo ""
    fi

    echo -e "${GREEN}╔══════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║${NC}                   CyberDemo is running!                  ${GREEN}║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${CYAN}Frontend:${NC}  http://localhost:5173"
    echo -e "  ${CYAN}Backend:${NC}   http://localhost:8000"
    echo -e "  ${CYAN}API Docs:${NC}  http://localhost:8000/docs"
    echo ""
    echo -e "  ${YELLOW}Logs:${NC}"
    echo -e "    Backend:  tail -f /tmp/cyberdemo-backend.log"
    echo -e "    Frontend: tail -f /tmp/cyberdemo-frontend.log"
    echo ""
    echo -e "  ${YELLOW}To stop:${NC} ./start.sh --stop"
    echo ""
}

main
