#!/bin/bash
# =============================================================================
# Run All API Tests
# Executes all test scripts in sequential order
# =============================================================================

# Set default base URL if not provided
export BASE_URL="${BASE_URL:-http://localhost:8000}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "=========================================="
echo "🧪 Running All API Tests"
echo "=========================================="
echo "Base URL: $BASE_URL"
echo "=========================================="

# Track test results
FAILED_TESTS=()
TOTAL_TESTS=0
PASSED_TESTS=0

# Function to run a test script
run_test() {
    local test_script=$1
    local test_name=$2
    
    echo -e "\n\n"
    echo "=========================================="
    echo "▶️  Running: $test_name"
    echo "=========================================="
    
    ((TOTAL_TESTS++))
    
    if bash "$SCRIPT_DIR/$test_script"; then
        echo "✅ $test_name - PASSED"
        ((PASSED_TESTS++))
    else
        echo "❌ $test_name - FAILED"
        FAILED_TESTS+=("$test_name")
    fi
}

# Run all test scripts in order
run_test "test_health.sh" "Health Tests"
run_test "test_auth.sh" "Authentication Tests"
run_test "test_transcripts.sh" "Transcript Tests"
run_test "test_query.sh" "Query Tests"
run_test "test_usage.sh" "Usage Tests"

# Print summary
echo -e "\n\n"
echo "=========================================="
echo "📊 Test Summary"
echo "=========================================="
echo "Total Tests: $TOTAL_TESTS"
echo "Passed: $PASSED_TESTS"
echo "Failed: ${#FAILED_TESTS[@]}"
echo "=========================================="

if [ ${#FAILED_TESTS[@]} -eq 0 ]; then
    echo "🎉 All tests passed!"
    echo "=========================================="
    exit 0
else
    echo "❌ Some tests failed:"
    for test in "${FAILED_TESTS[@]}"; do
        echo "  - $test"
    done
    echo "=========================================="
    exit 1
fi
