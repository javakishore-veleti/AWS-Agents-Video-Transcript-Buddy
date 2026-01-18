#!/bin/bash
# =============================================================================
# Test Usage Endpoints
# =============================================================================

BASE_URL="${BASE_URL:-http://localhost:8000}"
ACCESS_TOKEN=$(cat /tmp/test_access_token.txt 2>/dev/null)

echo "=========================================="
echo "📊 Testing Usage Endpoints"
echo "=========================================="

# Test Pricing (public - may not be implemented)
echo -e "\n📍 GET /api/usage/pricing (public)"
PRICING_RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/api/usage/pricing")
HTTP_CODE=$(echo "$PRICING_RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$PRICING_RESPONSE" | sed '$d')
if [ "$HTTP_CODE" = "200" ]; then
  echo "$RESPONSE_BODY" | python3 -m json.tool
else
  echo "⚠️  Endpoint not implemented (HTTP $HTTP_CODE)"
fi

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