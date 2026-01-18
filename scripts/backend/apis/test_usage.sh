#!/bin/bash
# =============================================================================
# Test Usage Endpoints
# =============================================================================

BASE_URL="${BASE_URL:-http://localhost:8000}"
ACCESS_TOKEN=$(cat /tmp/test_access_token.txt 2>/dev/null)

echo "=========================================="
echo "📊 Testing Usage Endpoints"
echo "=========================================="

# Test Pricing (public)
echo -e "\n📍 GET /api/usage/pricing (public)"
curl -s "$BASE_URL/api/usage/pricing" | python3 -m json.tool

# Check if token exists
if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "\n⚠️  No access token found. Run test_auth.sh first."
  echo "Skipping authenticated endpoints..."
  exit 0
fi

# Test Usage Summary
echo -e "\n📍 GET /api/usage/summary"
curl -s "$BASE_URL/api/usage/summary" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

# Test Usage Limits
echo -e "\n📍 GET /api/usage/limits"
curl -s "$BASE_URL/api/usage/limits" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

echo -e "\n✅ Usage tests completed!"