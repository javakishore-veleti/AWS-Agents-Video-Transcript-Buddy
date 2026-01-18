#!/bin/bash
# =============================================================================
# Test Health Endpoints
# =============================================================================

BASE_URL="${BASE_URL:-http://localhost:8000}"

echo "=========================================="
echo "🏥 Testing Health Endpoints"
echo "=========================================="

# Test basic health
echo -e "\n📍 GET /health"
curl -s "$BASE_URL/health" | python3 -m json.tool

# Test readiness
echo -e "\n📍 GET /health/ready"
curl -s "$BASE_URL/health/ready" | python3 -m json.tool

# Test liveness
echo -e "\n📍 GET /health/live"
curl -s "$BASE_URL/health/live" | python3 -m json.tool

echo -e "\n✅ Health tests completed!"