"""
Constants for Video Transcript Buddy Service.

All application-wide constants are defined here.
"""

# =============================================================================
# FILE HANDLING
# =============================================================================

# Supported transcript file extensions
SUPPORTED_FILE_EXTENSIONS = [".txt", ".srt", ".vtt", ".json"]

# Maximum file size in MB
MAX_FILE_SIZE_MB = 50

# Maximum file size in bytes
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# =============================================================================
# VECTOR STORE
# =============================================================================

# Default chunk size for text splitting
DEFAULT_CHUNK_SIZE = 1000

# Default chunk overlap
DEFAULT_CHUNK_OVERLAP = 200

# Default number of search results
DEFAULT_SEARCH_RESULTS = 5

# Maximum number of search results
MAX_SEARCH_RESULTS = 20


# =============================================================================
# S3 CONFIGURATION
# =============================================================================

# Default S3 folder names
S3_TRANSCRIPTS_FOLDER = "transcripts"
S3_ARCHIVE_FOLDER = "archive"

# S3 metadata keys
S3_METADATA_INDEXED = "indexed"
S3_METADATA_INDEXED_AT = "indexed_at"
S3_METADATA_CHUNK_COUNT = "chunk_count"


# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

# Agent names
AGENT_QUERY_VALIDATOR = "query-validator-agent"
AGENT_QUERY_RESOLVER = "query-resolver-agent"
AGENT_DATA_ANALYZER = "data-analyzer-agent"

# Tool names
TOOL_CONTENT_SEARCH = "content-search-tool"
TOOL_CONTEXT_ENRICHMENT = "context-enrichment-tool"
TOOL_DATA_EXTRACTION = "data-extraction-tool"


# =============================================================================
# API CONFIGURATION
# =============================================================================

# API versioning
API_VERSION = "v1"
API_PREFIX = f"/api/{API_VERSION}"

# Pagination defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


# =============================================================================
# RATE LIMITING
# =============================================================================

# Requests per minute
RATE_LIMIT_REQUESTS_PER_MINUTE = 60

# Query rate limit (more restrictive for AI calls)
QUERY_RATE_LIMIT_PER_MINUTE = 20


# =============================================================================
# TIMEOUTS (in seconds)
# =============================================================================

# S3 operation timeout
S3_TIMEOUT = 30

# Agent invocation timeout
AGENT_TIMEOUT = 60

# Vector store operation timeout
VECTOR_STORE_TIMEOUT = 30

# OpenAI API timeout
OPENAI_TIMEOUT = 60


# =============================================================================
# ERROR MESSAGES
# =============================================================================

ERROR_MESSAGES = {
    "TRANSCRIPT_NOT_FOUND": "The requested transcript was not found.",
    "S3_CONNECTION_ERROR": "Failed to connect to S3. Please check your AWS credentials.",
    "VECTOR_STORE_ERROR": "An error occurred with the vector store.",
    "AGENT_ERROR": "An error occurred while processing your query.",
    "VALIDATION_ERROR": "The provided data is invalid.",
    "FILE_TOO_LARGE": f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE_MB}MB.",
    "UNSUPPORTED_FILE_TYPE": f"File type not supported. Supported types: {', '.join(SUPPORTED_FILE_EXTENSIONS)}",
}