#!/bin/bash
# =============================================================================
# Test Auth Endpoints
# =============================================================================

BASE_URL="${BASE_URL:-http://localhost:8000}"
TEST_EMAIL="testuser_$(date +%s)@example.com"
TEST_PASSWORD="testpassword123"

echo "=========================================="
echo "🔐 Testing Auth Endpoints"
echo "=========================================="

# Test Register
echo -e "\n📍 POST /api/auth/register"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\", \"full_name\": \"Test User\"}")

echo "$REGISTER_RESPONSE" | python3 -m json.tool

# Extract access token
ACCESS_TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('access_token', ''))" 2>/dev/null)
REFRESH_TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('refresh_token', ''))" 2>/dev/null)

if [ -z "$ACCESS_TOKEN" ]; then
  echo "❌ Registration failed, trying login..."
  
  # Test Login
  echo -e "\n📍 POST /api/auth/login"
  LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\"}")
  
  echo "$LOGIN_RESPONSE" | python3 -m json.tool
  
  ACCESS_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('access_token', ''))" 2>/dev/null)
  REFRESH_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('refresh_token', ''))" 2>/dev/null)
fi

# Test Refresh Token
if [ -n "$REFRESH_TOKEN" ]; then
  echo -e "\n📍 POST /api/auth/refresh"
  curl -s -X POST "$BASE_URL/api/auth/refresh" \
    -H "Content-Type: application/json" \
    -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}" | python3 -m json.tool
fi

# Export token for other scripts
echo -e "\n📝 Access Token (for other tests):"
echo "$ACCESS_TOKEN"

# Save token to temp file for other scripts
echo "$ACCESS_TOKEN" > /tmp/test_access_token.txt
echo "$TEST_EMAIL" > /tmp/test_email.txt

echo -e "\n✅ Auth tests completed!"