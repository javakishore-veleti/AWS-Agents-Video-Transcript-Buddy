"""
Query Validator Agent - Validates and sanitizes user queries.

This agent acts as an input guardrail to:
- Check query validity and format
- Detect potentially harmful or off-topic queries
- Sanitize and normalize queries
- Suggest query improvements
"""

import logging
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from openai import OpenAI
from config import settings
from common.exceptions import AgentException

logger = logging.getLogger(__name__)


class QueryValidationStatus(Enum):
    """Query validation status codes."""
    VALID = "valid"
    INVALID = "invalid"
    NEEDS_CLARIFICATION = "needs_clarification"
    OFF_TOPIC = "off_topic"
    POTENTIALLY_HARMFUL = "potentially_harmful"


@dataclass
class ValidationResult:
    """Result of query validation."""
    status: QueryValidationStatus
    is_valid: bool
    original_query: str
    sanitized_query: Optional[str] = None
    message: str = ""
    suggestions: List[str] = None
    confidence: float = 1.0
    
    def __post_init__(self):
        if self.suggestions is None:
            self.suggestions = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "is_valid": self.is_valid,
            "original_query": self.original_query,
            "sanitized_query": self.sanitized_query,
            "message": self.message,
            "suggestions": self.suggestions,
            "confidence": self.confidence
        }


class QueryValidatorAgent:
    """
    Agent for validating user queries.
    
    Performs:
    - Basic validation (length, format)
    - Content validation (relevance, safety)
    - Query sanitization
    - Improvement suggestions
    """
    
    AGENT_NAME = "query-validator-agent"
    
    # Validation constraints
    MIN_QUERY_LENGTH = 3
    MAX_QUERY_LENGTH = 1000
    
    # Patterns for basic filtering
    HARMFUL_PATTERNS = [
        r'(?i)(hack|exploit|attack|injection)',
        r'(?i)(password|credential|secret).*(?:steal|get|find)',
    ]
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize Query Validator Agent.
        
        Args:
            use_llm: Whether to use LLM for advanced validation
        """
        self.use_llm = use_llm
        self._openai_client = None
    
    @property
    def openai_client(self) -> OpenAI:
        """Lazy-load OpenAI client."""
        if self._openai_client is None:
            if not settings.OPENAI_API_KEY:
                raise AgentException(
                    "OpenAI API key not configured",
                    agent_name=self.AGENT_NAME
                )
            self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._openai_client
    
    async def validate(self, query: str) -> ValidationResult:
        """
        Validate a user query.
        
        Args:
            query: User's query string
            
        Returns:
            ValidationResult with validation details
        """
        logger.info(f"Validating query: {query[:50]}...")
        
        # Step 1: Basic validation
        basic_result = self._basic_validation(query)
        if not basic_result.is_valid:
            return basic_result
        
        # Step 2: Pattern-based safety check
        safety_result = self._safety_check(query)
        if not safety_result.is_valid:
            return safety_result
        
        # Step 3: Sanitize query
        sanitized_query = self._sanitize_query(query)
        
        # Step 4: LLM-based validation (if enabled)
        if self.use_llm:
            try:
                llm_result = await self._llm_validation(sanitized_query)
                if not llm_result.is_valid:
                    llm_result.sanitized_query = sanitized_query
                    return llm_result
            except Exception as e:
                logger.warning(f"LLM validation failed, continuing with basic validation: {e}")
        
        # All checks passed
        return ValidationResult(
            status=QueryValidationStatus.VALID,
            is_valid=True,
            original_query=query,
            sanitized_query=sanitized_query,
            message="Query is valid",
            confidence=1.0
        )
    
    def _basic_validation(self, query: str) -> ValidationResult:
        """Perform basic validation checks."""
        # Check if empty
        if not query or not query.strip():
            return ValidationResult(
                status=QueryValidationStatus.INVALID,
                is_valid=False,
                original_query=query,
                message="Query cannot be empty",
                suggestions=["Please enter a question about the transcripts"]
            )
        
        # Check minimum length
        if len(query.strip()) < self.MIN_QUERY_LENGTH:
            return ValidationResult(
                status=QueryValidationStatus.INVALID,
                is_valid=False,
                original_query=query,
                message=f"Query is too short (minimum {self.MIN_QUERY_LENGTH} characters)",
                suggestions=["Please provide more detail in your question"]
            )
        
        # Check maximum length
        if len(query) > self.MAX_QUERY_LENGTH:
            return ValidationResult(
                status=QueryValidationStatus.INVALID,
                is_valid=False,
                original_query=query,
                message=f"Query is too long (maximum {self.MAX_QUERY_LENGTH} characters)",
                suggestions=["Please shorten your question"]
            )
        
        # Passed basic validation
        return ValidationResult(
            status=QueryValidationStatus.VALID,
            is_valid=True,
            original_query=query,
            message="Basic validation passed"
        )
    
    def _safety_check(self, query: str) -> ValidationResult:
        """Check for potentially harmful queries."""
        for pattern in self.HARMFUL_PATTERNS:
            if re.search(pattern, query):
                logger.warning(f"Potentially harmful query detected: {query[:50]}...")
                return ValidationResult(
                    status=QueryValidationStatus.POTENTIALLY_HARMFUL,
                    is_valid=False,
                    original_query=query,
                    message="Query contains potentially harmful content",
                    suggestions=["Please rephrase your question"]
                )
        
        return ValidationResult(
            status=QueryValidationStatus.VALID,
            is_valid=True,
            original_query=query,
            message="Safety check passed"
        )
    
    def _sanitize_query(self, query: str) -> str:
        """Sanitize and normalize the query."""
        # Strip whitespace
        sanitized = query.strip()
        
        # Normalize multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Remove potentially dangerous characters (but keep punctuation)
        sanitized = re.sub(r'[<>{}|\[\]\\^`]', '', sanitized)
        
        return sanitized
    
    async def _llm_validation(self, query: str) -> ValidationResult:
        """Use LLM to validate query relevance and clarity."""
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a query validator for a video transcript search system.
Evaluate if the query is:
1. Related to video/transcript content (not asking about unrelated topics)
2. Clear and answerable
3. Appropriate (not harmful or offensive)

Respond with JSON only:
{
    "is_valid": true/false,
    "status": "valid" | "off_topic" | "needs_clarification",
    "message": "brief explanation",
    "suggestions": ["suggestion1", "suggestion2"] (if not valid)
}"""
                    },
                    {
                        "role": "user",
                        "content": f"Validate this query: {query}"
                    }
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Try to extract JSON
            import json
            try:
                # Handle potential markdown code blocks
                if "```" in content:
                    content = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
                    content = content.group(1) if content else "{}"
                
                result = json.loads(content)
                
                status_map = {
                    "valid": QueryValidationStatus.VALID,
                    "off_topic": QueryValidationStatus.OFF_TOPIC,
                    "needs_clarification": QueryValidationStatus.NEEDS_CLARIFICATION,
                    "invalid": QueryValidationStatus.INVALID
                }
                
                return ValidationResult(
                    status=status_map.get(result.get("status", "valid"), QueryValidationStatus.VALID),
                    is_valid=result.get("is_valid", True),
                    original_query=query,
                    message=result.get("message", ""),
                    suggestions=result.get("suggestions", []),
                    confidence=0.9
                )
            except json.JSONDecodeError:
                # If JSON parsing fails, assume valid
                logger.warning(f"Failed to parse LLM validation response: {content}")
                return ValidationResult(
                    status=QueryValidationStatus.VALID,
                    is_valid=True,
                    original_query=query,
                    message="LLM validation inconclusive, assuming valid",
                    confidence=0.7
                )
        
        except Exception as e:
            logger.error(f"LLM validation error: {e}")
            raise AgentException(
                f"LLM validation failed: {str(e)}",
                agent_name=self.AGENT_NAME
            )
    
    async def suggest_improvements(self, query: str) -> List[str]:
        """Generate suggestions to improve the query."""
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """You help users improve their search queries for a video transcript system.
Given a query, suggest 2-3 improved versions that are:
- More specific
- Clearer
- More likely to find relevant results

Respond with just the suggestions, one per line."""
                    },
                    {
                        "role": "user",
                        "content": f"Improve this query: {query}"
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            suggestions = [s.strip() for s in content.split('\n') if s.strip()]
            return suggestions[:3]
        
        except Exception as e:
            logger.error(f"Failed to generate suggestions: {e}")
            return []