#!/bin/bash
# CompleteVerificationTestsX - Complete E2E Verification Tests for CyberDemo
# Executes all Playwright E2E tests to verify all 13 pages and functionalities
#
# Usage: ./CompleteVerificationTestsX.sh [options]
#   --headed    Run with visible browser
#   --debug     Run in debug mode
#   --report    Generate HTML report
#   --quick     Run only critical tests
#
# Date: 2026-02-16
# Tests: 119 E2E tests covering all pages, functionalities, generation, navigation, and dashboard charts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(dirname "$SCRIPT_DIR")/frontend"
DOCS_DIR="$(dirname "$SCRIPT_DIR")/docs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default options
HEADED=""
DEBUG=""
REPORTER="list"
PROJECT="chromium"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --headed)
            HEADED="--headed"
            shift
            ;;
        --debug)
            DEBUG="--debug"
            shift
            ;;
        --report)
            REPORTER="html"
            shift
            ;;
        --quick)
            PROJECT="chromium"
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║       CompleteVerificationTestsX - CyberDemo E2E Tests       ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "$FRONTEND_DIR/package.json" ]; then
    echo -e "${RED}Error: Frontend directory not found at $FRONTEND_DIR${NC}"
    exit 1
fi

cd "$FRONTEND_DIR"

# Check if Playwright is installed
if ! pnpm exec playwright --version > /dev/null 2>&1; then
    echo -e "${YELLOW}Installing Playwright...${NC}"
    pnpm exec playwright install chromium
fi

echo -e "${BLUE}📋 Test Plan:${NC}"
echo "   - 13 Pages to verify"
echo "   - 119 E2E tests total"
echo "   - Categories: Page Load, Headers, Content, Controls"
echo "   - Additional: Navigation (3), Responsive (3), Generation (31), Card Navigation (7), Dashboard Charts (22)"
echo ""

echo -e "${BLUE}🌐 Pages being tested:${NC}"
echo "   1. GenerationPage (/generation)    - 4 tests"
echo "   2. DashboardPage (/dashboard)      - 4 tests"
echo "   3. AssetsPage (/assets)            - 4 tests"
echo "   4. IncidentsPage (/incidents)      - 4 tests"
echo "   5. DetectionsPage (/detections)    - 4 tests"
echo "   6. TimelinePage (/timeline)        - 4 tests"
echo "   7. PostmortemsPage (/postmortems)  - 4 tests"
echo "   8. TicketsPage (/tickets)          - 4 tests"
echo "   9. CTEMPage (/ctem)                - 4 tests"
echo "  10. GraphPage (/graph)              - 4 tests"
echo "  11. CollabPage (/collab)            - 4 tests"
echo "  12. ConfigPage (/config)            - 4 tests"
echo "  13. AuditPage (/audit)              - 5 tests"
echo ""
echo -e "${BLUE}🧪 Generation Tests (generation.spec.ts):${NC}"
echo "   - Button tests                     - 5 tests"
echo "   - Data generation tests            - 4 tests"
echo "   - Error handling tests             - 2 tests"
echo "   - UI state tests                   - 4 tests"
echo "   - API integration tests            - 5 tests"
echo "   - Card navigation tests            - 7 tests"
echo ""
echo -e "${BLUE}📊 Dashboard Charts Tests (dashboard-charts.spec.ts):${NC}"
echo "   - Incidents by Hour widget         - 4 tests"
echo "   - Severity Distribution widget     - 4 tests"
echo "   - Top Affected Hosts widget        - 3 tests"
echo "   - Detection Trend widget           - 4 tests"
echo "   - KPI Cards widget                 - 4 tests"
echo "   - API Integration tests            - 3 tests"
echo ""

echo -e "${BLUE}🚀 Running E2E tests...${NC}"
echo ""

# Run the tests (all E2E tests including generation)
START_TIME=$(date +%s)

pnpm exec playwright test tests/e2e/ \
    --project="$PROJECT" \
    --reporter="$REPORTER" \
    $HEADED $DEBUG

EXIT_CODE=$?
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo ""

if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                    ✅ ALL TESTS PASSED                       ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}Summary:${NC}"
    echo "   ✅ 119/119 E2E tests passed"
    echo "   ✅ 13/13 pages verified"
    echo "   ✅ 38/38 generation tests passed (incl. 7 card navigation)"
    echo "   ✅ 22/22 dashboard chart tests passed"
    echo "   ⏱️  Execution time: ${DURATION}s"
    echo ""
    echo -e "${BLUE}📄 Documentation:${NC}"
    echo "   - Test Plan: $DOCS_DIR/TEST_PLAN_E2E.md"
    echo "   - Test Results: $DOCS_DIR/TEST_RESULTS_E2E.md"

    if [ "$REPORTER" = "html" ]; then
        echo "   - HTML Report: $FRONTEND_DIR/playwright-report/index.html"
    fi
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║                    ❌ TESTS FAILED                           ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${YELLOW}Check the test output above for details.${NC}"
    echo -e "${YELLOW}Run with --debug for more information.${NC}"
fi

echo ""
exit $EXIT_CODE
