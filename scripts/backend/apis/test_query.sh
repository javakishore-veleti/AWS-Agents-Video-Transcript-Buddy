#!/bin/bash
# =============================================================================
# Test Query Endpoints
# =============================================================================

BASE_URL="${BASE_URL:-http://localhost:8000}"
ACCESS_TOKEN=$(cat /tmp/test_access_token.txt 2>/dev/null)

echo "=========================================="
echo "🔍 Testing Query Endpoints"
echo "=========================================="

# Check if token exists
if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "\n⚠️  No access token found. Run test_auth.sh first."
  exit 1
fi

# Test Query Validation
echo -e "\n📍 POST /api/query/validate"
curl -s -X POST "$BASE_URL/api/query/validate" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main topics discussed?"}' | python3 -m json.tool

# Test Search
echo -e "\n📍 POST /api/query/search"
curl -s -X POST "$BASE_URL/api/query/search" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "AI machine learning", "max_results": 5}' | python3 -m json.tool

# Test Query
echo -e "\n📍 POST /api/query/"
curl -s -X POST "$BASE_URL/api/query/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the main topics discussed?", "max_results": 5}' | python3 -m json.tool

# Test Suggestions
echo -e "\n📍 GET /api/query/suggestions"
curl -s "$BASE_URL/api/query/suggestions?count=3" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

echo -e "\n✅ Query tests completed!"