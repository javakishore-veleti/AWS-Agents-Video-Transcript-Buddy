"""
Query Resolver Agent - Main orchestrator for resolving user queries.

This agent:
- Orchestrates the query resolution process
- Coordinates with other agents and tools
- Generates comprehensive answers from transcript content
- Handles multi-step reasoning and handoffs
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from openai import OpenAI
from config import settings
from common.exceptions import AgentException
from dao.vector_store_dao import VectorStoreDAO

logger = logging.getLogger(__name__)


class QueryComplexity(Enum):
    """Query complexity levels."""
    SIMPLE = "simple"           # Single fact lookup
    MODERATE = "moderate"       # Multi-fact synthesis
    COMPLEX = "complex"         # Requires analysis/reasoning
    MULTI_TRANSCRIPT = "multi_transcript"  # Cross-transcript analysis


@dataclass
class ResolverResult:
    """Result of query resolution."""
    success: bool
    query: str
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    complexity: QueryComplexity = QueryComplexity.SIMPLE
    reasoning_steps: List[str] = field(default_factory=list)
    handoff_to: Optional[str] = None  # Agent to hand off to
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "query": self.query,
            "answer": self.answer,
            "sources": self.sources,
            "confidence": self.confidence,
            "complexity": self.complexity.value,
            "reasoning_steps": self.reasoning_steps,
            "handoff_to": self.handoff_to,
            "metadata": self.metadata
        }


class QueryResolverAgent:
    """
    Main agent for resolving user queries against transcripts.
    
    Responsibilities:
    - Analyze query complexity
    - Search relevant transcript chunks
    - Synthesize answers from multiple sources
    - Hand off to specialized agents when needed
    """
    
    AGENT_NAME = "query-resolver-agent"
    
    # Thresholds
    MIN_CONFIDENCE_THRESHOLD = 0.3
    HANDOFF_COMPLEXITY_THRESHOLD = QueryComplexity.COMPLEX
    
    def __init__(
        self,
        vector_store_dao: Optional[VectorStoreDAO] = None,
        max_sources: int = 5
    ):
        """
        Initialize Query Resolver Agent.
        
        Args:
            vector_store_dao: Vector store for searching transcripts
            max_sources: Maximum number of source chunks to use
        """
        self.vector_store_dao = vector_store_dao or VectorStoreDAO()
        self.max_sources = max_sources
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
    
    async def resolve(
        self,
        query: str,
        transcript_ids: Optional[List[str]] = None,
        include_reasoning: bool = False
    ) -> ResolverResult:
        """
        Resolve a user query.
        
        Args:
            query: User's question
            transcript_ids: Optional filter by transcript IDs
            include_reasoning: Whether to include reasoning steps
            
        Returns:
            ResolverResult with answer and sources
        """
        logger.info(f"Resolving query: {query[:50]}...")
        reasoning_steps = []
        
        try:
            # Step 1: Analyze query complexity
            complexity = await self._analyze_complexity(query)
            reasoning_steps.append(f"Query complexity: {complexity.value}")
            
            # Step 2: Check if handoff is needed
            if complexity == QueryComplexity.COMPLEX:
                reasoning_steps.append("Complex query detected, may need data analyzer")
            
            # Step 3: Search for relevant content
            search_results = self.vector_store_dao.search(
                query=query,
                n_results=self.max_sources,
                transcript_ids=transcript_ids
            )
            reasoning_steps.append(f"Found {len(search_results)} relevant chunks")
            
            # Step 4: Check if we have enough content
            if not search_results:
                return ResolverResult(
                    success=False,
                    query=query,
                    answer="I couldn't find any relevant information in the transcripts to answer your question.",
                    confidence=0.0,
                    complexity=complexity,
                    reasoning_steps=reasoning_steps if include_reasoning else []
                )
            
            # Step 5: Calculate average relevance score
            avg_score = sum(r.get("score", 0) for r in search_results) / len(search_results)
            reasoning_steps.append(f"Average relevance score: {avg_score:.2f}")
            
            # Step 6: Check if handoff to data analyzer is needed
            if complexity == QueryComplexity.COMPLEX and avg_score < 0.5:
                reasoning_steps.append("Handing off to Data Analyzer Agent")
                return ResolverResult(
                    success=True,
                    query=query,
                    answer="",
                    sources=self._format_sources(search_results),
                    confidence=avg_score,
                    complexity=complexity,
                    reasoning_steps=reasoning_steps if include_reasoning else [],
                    handoff_to="data-analyzer-agent"
                )
            
            # Step 7: Generate answer
            context = self._build_context(search_results)
            answer = await self._generate_answer(query, context, complexity)
            reasoning_steps.append("Generated answer from context")
            
            # Step 8: Format sources
            sources = self._format_sources(search_results)
            
            return ResolverResult(
                success=True,
                query=query,
                answer=answer,
                sources=sources,
                confidence=avg_score,
                complexity=complexity,
                reasoning_steps=reasoning_steps if include_reasoning else [],
                metadata={
                    "chunks_used": len(search_results),
                    "transcript_count": len(set(s.get("transcript_id") for s in sources))
                }
            )
        
        except Exception as e:
            logger.error(f"Query resolution failed: {e}")
            raise AgentException(
                f"Failed to resolve query: {str(e)}",
                agent_name=self.AGENT_NAME
            )
    
    async def _analyze_complexity(self, query: str) -> QueryComplexity:
        """Analyze the complexity of the query."""
        query_lower = query.lower()
        
        # Simple heuristics first
        complex_indicators = [
            "compare", "contrast", "analyze", "relationship",
            "trend", "pattern", "correlation", "difference",
            "how does", "why does", "explain why"
        ]
        
        multi_transcript_indicators = [
            "all videos", "across", "throughout", "every transcript",
            "multiple", "different videos"
        ]
        
        # Check for multi-transcript queries
        if any(indicator in query_lower for indicator in multi_transcript_indicators):
            return QueryComplexity.MULTI_TRANSCRIPT
        
        # Check for complex queries
        if any(indicator in query_lower for indicator in complex_indicators):
            return QueryComplexity.COMPLEX
        
        # Check for moderate complexity (questions with multiple parts)
        if query.count("?") > 1 or " and " in query_lower:
            return QueryComplexity.MODERATE
        
        return QueryComplexity.SIMPLE
    
    def _build_context(self, search_results: List[Dict[str, Any]]) -> str:
        """Build context string from search results."""
        context_parts = []
        
        for i, result in enumerate(search_results, 1):
            source = result.get("metadata", {}).get("transcript_id", "Unknown")
            content = result.get("content", "")
            score = result.get("score", 0)
            
            context_parts.append(
                f"[Source {i}: {source} (relevance: {score:.2f})]\n{content}"
            )
        
        return "\n\n---\n\n".join(context_parts)
    
    async def _generate_answer(
        self,
        query: str,
        context: str,
        complexity: QueryComplexity
    ) -> str:
        """Generate answer using LLM."""
        
        # Adjust prompt based on complexity
        if complexity == QueryComplexity.COMPLEX:
            system_prompt = """You are an expert analyst answering questions based on video transcript content.

For complex questions:
- Analyze the information thoroughly
- Consider multiple perspectives
- Draw connections between different parts of the content
- Provide structured, detailed answers
- Cite sources when making claims

If information is insufficient, explain what's missing."""
        
        elif complexity == QueryComplexity.MULTI_TRANSCRIPT:
            system_prompt = """You are an assistant answering questions across multiple video transcripts.

- Synthesize information from all provided sources
- Note any differences or contradictions between sources
- Clearly attribute information to specific transcripts
- Provide a comprehensive overview"""
        
        else:
            system_prompt = """You are a helpful assistant answering questions based on video transcript content.

Rules:
- Only answer based on the provided context
- If the context doesn't contain relevant information, say so
- Cite sources when possible (e.g., "According to Source 1...")
- Be concise but thorough"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Context from transcripts:\n\n{context}\n\n---\n\nQuestion: {query}\n\nAnswer:"
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
                agent_name=self.AGENT_NAME
            )
    
    def _format_sources(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format search results as source references."""
        sources = []
        seen_transcripts = set()
        
        for result in search_results:
            metadata = result.get("metadata", {})
            transcript_id = metadata.get("transcript_id", "Unknown")
            
            source = {
                "transcript_id": transcript_id,
                "chunk_index": metadata.get("chunk_index", 0),
                "score": round(result.get("score", 0), 4),
                "preview": result.get("content", "")[:200] + "..." if result.get("content") else ""
            }
            
            sources.append(source)
            seen_transcripts.add(transcript_id)
        
        return sources
    
    async def get_context_for_handoff(
        self,
        query: str,
        transcript_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get context for handing off to another agent.
        
        Args:
            query: User's question
            transcript_ids: Optional filter by transcript IDs
            
        Returns:
            Context dict for handoff
        """
        search_results = self.vector_store_dao.search(
            query=query,
            n_results=self.max_sources * 2,  # Get more for handoff
            transcript_ids=transcript_ids
        )
        
        return {
            "query": query,
            "context": self._build_context(search_results),
            "sources": self._format_sources(search_results),
            "chunk_count": len(search_results)
        }