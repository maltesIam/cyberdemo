#!/bin/bash
#
# CyberDemo - Quick Start Demo Setup
#
# This script prepares the CyberDemo environment for running demo scenarios.
# It generates synthetic data, verifies services, and displays instructions.
#
# Usage: ./demo-setup.sh [OPTIONS]
#
# Options:
#   --seed <number>    Seed for reproducible data generation (default: 42)
#   --verify-only      Only verify services, don't generate data
#   --help             Show this help message
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CYBERDEMO_DIR="$(dirname "$SCRIPT_DIR")"
SEED=42
VERIFY_ONLY=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --seed|-s)
            SEED="$2"
            shift 2
            ;;
        --verify-only|-v)
            VERIFY_ONLY=true
            shift
            ;;
        --help|-h)
            echo "CyberDemo - Quick Start Demo Setup"
            echo ""
            echo "Usage: ./demo-setup.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --seed, -s <number>    Seed for reproducible data (default: 42)"
            echo "  --verify-only, -v      Only verify services, don't generate data"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "Examples:"
            echo "  ./demo-setup.sh                   # Full setup with default seed"
            echo "  ./demo-setup.sh --seed 123        # Setup with custom seed"
            echo "  ./demo-setup.sh --verify-only     # Just verify services"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Print functions
print_header() {
    echo ""
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}$(printf '=%.0s' {1..60})${NC}"
}

print_status() {
    echo -e "${CYAN}[*]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[+]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[-]${NC} $1"
}

print_step() {
    echo -e "    ${BOLD}$1${NC}"
}

# Service verification
verify_opensearch() {
    print_status "Checking OpenSearch (localhost:9200)..."
    if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
        print_success "OpenSearch is running"
        return 0
    else
        print_error "OpenSearch is not running"
        return 1
    fi
}

verify_backend() {
    print_status "Checking Backend API (localhost:8000)..."
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend API is running"
        return 0
    else
        print_error "Backend API is not running"
        return 1
    fi
}

verify_frontend() {
    print_status "Checking Frontend (localhost:5173)..."
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        print_success "Frontend is running"
        return 0
    else
        print_warning "Frontend is not running (optional for CLI demo)"
        return 0
    fi
}

verify_services() {
    print_header "Verifying Services"

    local all_ok=true

    verify_opensearch || all_ok=false
    verify_backend || all_ok=false
    verify_frontend

    if [ "$all_ok" = false ]; then
        echo ""
        print_error "Some required services are not running."
        print_warning "Run: cd $CYBERDEMO_DIR && ./start.sh"
        exit 1
    fi

    print_success "All required services are running"
}

# Generate synthetic data
generate_data() {
    print_header "Generating Synthetic Data (seed: $SEED)"

    # Step 1: Reset indices
    print_status "Resetting OpenSearch indices..."
    RESET_RESPONSE=$(curl -s -X POST "http://localhost:8000/gen/reset")
    if echo "$RESET_RESPONSE" | grep -q "success\|reset"; then
        print_success "Indices reset successfully"
    else
        print_warning "Reset response: $RESET_RESPONSE"
    fi

    # Step 2: Generate anchor cases
    print_status "Generating anchor cases (3 demo scenarios)..."
    ANCHOR_RESPONSE=$(curl -s -X POST "http://localhost:8000/gen/anchor-cases?seed=$SEED")
    if echo "$ANCHOR_RESPONSE" | grep -q "success\|created"; then
        print_success "Anchor cases generated"
    else
        print_warning "Anchor cases response: $ANCHOR_RESPONSE"
    fi

    # Step 3: Generate all synthetic data
    print_status "Generating full synthetic dataset..."
    GEN_RESPONSE=$(curl -s -X POST "http://localhost:8000/gen/all?seed=$SEED")
    if echo "$GEN_RESPONSE" | grep -q "success"; then
        print_success "Synthetic data generated"
    else
        print_warning "Generation response: $GEN_RESPONSE"
    fi

    # Step 4: Verify data counts
    print_status "Verifying data counts..."
    COUNTS=$(curl -s "http://localhost:8000/gen/health" 2>/dev/null)

    if [ -n "$COUNTS" ]; then
        echo ""
        echo -e "  ${BOLD}Data Counts:${NC}"
        echo "$COUNTS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    counts = data.get('counts', {})
    for k, v in sorted(counts.items()):
        print(f'    {k}: {v}')
except:
    print('    (Could not parse counts)')
" 2>/dev/null || echo "    (Could not parse counts)"
    fi

    print_success "Data generation complete"
}

# Display demo instructions
show_instructions() {
    print_header "Demo Instructions"

    echo ""
    echo -e "  ${BOLD}Available Demo Scenarios:${NC}"
    echo ""
    echo -e "  ${CYAN}1. Auto-Containment (Workstation)${NC}"
    print_step "/demo_case_1 or /investigate INC-ANCHOR-001"
    echo "     - Standard workstation with confirmed malware"
    echo "     - High confidence score (>= 90)"
    echo "     - Auto-containment executed"
    echo ""

    echo -e "  ${CYAN}2. VIP Human-in-the-Loop${NC}"
    print_step "/demo_case_2 or /investigate INC-ANCHOR-002"
    echo "     - Executive laptop (VIP asset)"
    echo "     - Requires manual approval regardless of score"
    echo "     - Shows approval card workflow"
    echo ""

    echo -e "  ${CYAN}3. False Positive${NC}"
    print_step "/demo_case_3 or /investigate INC-ANCHOR-003"
    echo "     - Legitimate software detection"
    echo "     - Low confidence score (< 50)"
    echo "     - Marked as false positive"
    echo ""

    echo -e "  ${BOLD}Other Commands:${NC}"
    echo ""
    print_step "/status"
    echo "     - Show current SOC status and open incidents"
    echo ""
    print_step "/investigate <incident_id>"
    echo "     - Investigate any incident by ID"
    echo ""

    print_header "Access Points"
    echo ""
    echo -e "  ${CYAN}Frontend Dashboard:${NC}  http://localhost:5173"
    echo -e "  ${CYAN}Backend API:${NC}         http://localhost:8000"
    echo -e "  ${CYAN}API Documentation:${NC}   http://localhost:8000/docs"
    echo -e "  ${CYAN}OpenSearch:${NC}          http://localhost:9200"
    echo ""

    print_header "Moltbot Integration"
    echo ""
    echo "  To use the SOC Analyst skill with Moltbot:"
    echo ""
    print_step "1. Ensure moltbot is installed and configured"
    print_step "2. Load the cyberdemo extension:"
    echo "     moltbot extensions load extensions/cyberdemo"
    echo ""
    print_step "3. Start a conversation and use commands:"
    echo "     /demo_case_1"
    echo "     /investigate INC-ANCHOR-001"
    echo ""
}

# Main execution
main() {
    echo ""
    echo -e "${CYAN}+----------------------------------------------------------+${NC}"
    echo -e "${CYAN}|${NC}    ${BOLD}CyberDemo${NC} - SOC Tier-1 Analyst Demo Setup           ${CYAN}|${NC}"
    echo -e "${CYAN}+----------------------------------------------------------+${NC}"
    echo ""

    # Verify services
    verify_services

    # Generate data unless verify-only
    if [ "$VERIFY_ONLY" = false ]; then
        generate_data
    fi

    # Show instructions
    show_instructions

    echo ""
    echo -e "${GREEN}+----------------------------------------------------------+${NC}"
    echo -e "${GREEN}|${NC}              Demo environment is ready!                 ${GREEN}|${NC}"
    echo -e "${GREEN}+----------------------------------------------------------+${NC}"
    echo ""
}

main
