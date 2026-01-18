#!/bin/bash
# =============================================================================
# Test Transcript Endpoints
# =============================================================================

BASE_URL="${BASE_URL:-http://localhost:8000}"
ACCESS_TOKEN=$(cat /tmp/test_access_token.txt 2>/dev/null)

echo "=========================================="
echo "📁 Testing Transcript Endpoints"
echo "=========================================="

# Check if token exists
if [ -z "$ACCESS_TOKEN" ]; then
  echo -e "\n⚠️  No access token found. Run test_auth.sh first."
  exit 1
fi

# Create a test transcript file
TEST_FILE="/tmp/test_transcript.txt"
echo "This is a test transcript content.
It contains multiple lines of text.
We will use this to test the upload functionality.
The video discusses AI and machine learning topics." > "$TEST_FILE"

# Test Upload
echo -e "\n📍 POST /api/transcripts/upload"
UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/api/transcripts/upload" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -F "file=@$TEST_FILE" \
  -F "auto_index=true")

echo "$UPLOAD_RESPONSE" | python3 -m json.tool

# Test List Transcripts
echo -e "\n📍 GET /api/transcripts/"
curl -s "$BASE_URL/api/transcripts/" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

# Test Get Single Transcript
echo -e "\n📍 GET /api/transcripts/test_transcript.txt"
curl -s "$BASE_URL/api/transcripts/test_transcript.txt" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | python3 -m json.tool

# Test Check Exists
echo -e "\n📍 HEAD /api/transcripts/test_transcript.txt"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X HEAD "$BASE_URL/api/transcripts/test_transcript.txt" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "Response code: $HTTP_CODE"

# Cleanup test file
rm -f "$TEST_FILE"

echo -e "\n✅ Transcript tests completed!"