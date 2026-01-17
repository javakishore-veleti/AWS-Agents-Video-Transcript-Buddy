"""
Query Service - Business logic for query operations.

Handles user queries by searching vector store and generating answers using LLM.
"""

import logging
from typing import List, Optional, Dict, Any

from openai import OpenAI

from .interfaces.query_service_interface import IQueryService
from dao.vector_store_dao import VectorStoreDAO
from config import settings
from common.exceptions import AgentException, ValidationException
from common.constants import DEFAULT_SEARCH_RESULTS, MAX_SEARCH_RESULTS

logger = logging.getLogger(__name__)


class QueryService(IQueryService):
    """Service for query operations."""
    
    def __init__(self, vector_store_dao: Optional[VectorStoreDAO] = None):
        """
        Initialize query service.
        
        Args:
            vector_store_dao: Vector store data access object
        """
        self.vector_store_dao = vector_store_dao or VectorStoreDAO()
        self._openai_client = None
    
    @property
    def openai_client(self) -> OpenAI:
        """Lazy-load OpenAI client."""
        if self._openai_client is None:
            if not settings.OPENAI_API_KEY:
                raise AgentException(
                    "OpenAI API key not configured",
                    agent_name="query_service"
                )
            self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._openai_client
    
    async def query(
        self,
        question: str,
        transcript_ids: Optional[List[str]] = None,
        max_results: int = DEFAULT_SEARCH_RESULTS
    ) -> Dict[str, Any]:
        """
        Process a user query against transcripts.
        
        Args:
            question: User's question
            transcript_ids: Optional filter by specific transcripts
            max_results: Maximum number of source chunks to consider
            
        Returns:
            Dict with answer and source references
        """
        # Validate query
        validation = await self.validate_query(question)
        if not validation["valid"]:
            raise ValidationException(validation["message"], field="question")
        
        # Search for relevant chunks
        search_results = await self.search(
            query=question,
            transcript_ids=transcript_ids,
            max_results=max_results
        )
        
        if not search_results:
            return {
                "question": question,
                "answer": "I couldn't find any relevant information in the transcripts to answer your question.",
                "sources": [],
                "confidence": 0.0
            }
        
        # Build context from search results
        context = self._build_context(search_results)
        
        # Generate answer using LLM
        answer = await self._generate_answer(question, context)
        
        # Extract source references
        sources = self._extract_sources(search_results)
        
        # Calculate confidence based on search scores
        confidence = self._calculate_confidence(search_results)
        
        return {
            "question": question,
            "answer": answer,
            "sources": sources,
            "confidence": round(confidence, 2),
            "chunks_used": len(search_results)
        }
    
    async def search(
        self,
        query: str,
        transcript_ids: Optional[List[str]] = None,
        max_results: int = DEFAULT_SEARCH_RESULTS
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant transcript chunks without generating an answer.
        
        Args:
            query: Search query
            transcript_ids: Optional filter by specific transcripts
            max_results: Maximum number of results
            
        Returns:
            List of matching chunks with metadata
        """
        max_results = min(max_results, MAX_SEARCH_RESULTS)
        
        results = self.vector_store_dao.search(
            query=query,
            n_results=max_results,
            transcript_ids=transcript_ids
        )
        
        return results
    
    async def validate_query(self, question: str) -> Dict[str, Any]:
        """
        Validate a user query before processing.
        
        Args:
            question: User's question
            
        Returns:
            Dict with validation result and any issues
        """
        # Check if question is empty
        if not question or not question.strip():
            return {
                "valid": False,
                "message": "Question cannot be empty"
            }
        
        # Check minimum length
        if len(question.strip()) < 3:
            return {
                "valid": False,
                "message": "Question is too short"
            }
        
        # Check maximum length
        if len(question) > 1000:
            return {
                "valid": False,
                "message": "Question is too long (max 1000 characters)"
            }
        
        return {
            "valid": True,
            "message": "Query is valid"
        }
    
    async def get_suggested_questions(
        self,
        transcript_ids: Optional[List[str]] = None,
        count: int = 5
    ) -> List[str]:
        """
        Get suggested questions based on transcript content.
        
        Args:
            transcript_ids: Optional filter by specific transcripts
            count: Number of suggestions
            
        Returns:
            List of suggested questions
        """
        # Get sample content from vector store
        sample_results = self.vector_store_dao.search(
            query="main topics discussed",
            n_results=3,
            transcript_ids=transcript_ids
        )
        
        if not sample_results:
            return [
                "What are the main topics discussed?",
                "Can you summarize the key points?",
                "What are the most important takeaways?",
                "Who are the main speakers or participants?",
                "What conclusions were reached?"
            ][:count]
        
        # Build context from samples
        context = "\n\n".join([r["content"] for r in sample_results])
        
        # Generate suggestions using LLM
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that generates relevant questions based on transcript content. Generate questions that would help a user understand the key information in the transcripts."
                    },
                    {
                        "role": "user",
                        "content": f"Based on this transcript content, suggest {count} relevant questions a user might want to ask:\n\n{context}\n\nProvide only the questions, one per line, without numbering."
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            suggestions = response.choices[0].message.content.strip().split("\n")
            suggestions = [q.strip() for q in suggestions if q.strip()]
            return suggestions[:count]
        
        except Exception as e:
            logger.error(f"Failed to generate suggested questions: {e}")
            return [
                "What are the main topics discussed?",
                "Can you summarize the key points?",
                "What are the most important takeaways?"
            ][:count]
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context string from search results."""
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            source = result.get("metadata", {}).get("transcript_id", "Unknown")
            content = result.get("content", "")
            context_parts.append(f"[Source {i}: {source}]\n{content}")
        
        return "\n\n---\n\n".join(context_parts)
    
    async def _generate_answer(self, question: str, context: str) -> str:
        """Generate answer using LLM."""
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a helpful assistant that answers questions based on video transcript content. 
                        
Rules:
- Only answer based on the provided context
- If the context doesn't contain relevant information, say so
- Cite sources when possible (e.g., "According to Source 1...")
- Be concise but thorough
- If you're unsure, express uncertainty"""
                    },
                    {
                        "role": "user",
                        "content": f"Context from transcripts:\n\n{context}\n\n---\n\nQuestion: {question}\n\nAnswer:"
                    }
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            raise AgentException(
                f"Failed to generate answer: {str(e)}",
                agent_name="query_service"
            )
    
    def _extract_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source references from search results."""
        sources = []
        seen_transcripts = set()
        
        for result in search_results:
            metadata = result.get("metadata", {})
            transcript_id = metadata.get("transcript_id", "Unknown")
            
            if transcript_id not in seen_transcripts:
                seen_transcripts.add(transcript_id)
                sources.append({
                    "transcript_id": transcript_id,
                    "chunk_index": metadata.get("chunk_index", 0),
                    "score": result.get("score", 0),
                    "preview": result.get("content", "")[:200] + "..."
                })
        
        return sources
    
    def _calculate_confidence(self, search_results: List[Dict[str, Any]]) -> float:
        """Calculate confidence score based on search results."""
        if not search_results:
            return 0.0
        
        # Average the top scores
        scores = [r.get("score", 0) for r in search_results[:3]]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Normalize to 0-1 range (scores are already similarity scores)
        return min(avg_score, 1.0)