#!/bin/bash
# =============================================================================
# Setup Test User
# Creates a test user directly in the database for testing
# =============================================================================

DB_PATH="${DB_PATH:-backend/microservices/video_transcript_buddy_service/data/transcriptquery.db}"
TEST_EMAIL="testuser@example.com"
TEST_PASSWORD="Test123!"

echo "=========================================="
echo "🔧 Setting up test user"
echo "=========================================="

# Delete existing test user
echo "Cleaning up old test users..."
sqlite3 "$DB_PATH" "DELETE FROM users WHERE email = '$TEST_EMAIL';" 2>/dev/null

echo "Creating new test user via API..."

# Register new user
curl -s -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\", \"full_name\": \"Test User\"}" | python3 -m json.tool

echo -e "\n✅ Test user setup complete!"
echo "Email: $TEST_EMAIL"
echo "Password: $TEST_PASSWORD"
