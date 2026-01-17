"""
Data Analyzer Agent - Performs complex data analysis on transcripts.

This agent handles:
- Complex analytical queries
- Cross-transcript comparisons
- Pattern and trend identification
- Statistical summaries
- Deep content analysis
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


class AnalysisType(Enum):
    """Types of analysis the agent can perform."""
    COMPARISON = "comparison"
    TREND = "trend"
    SUMMARY = "summary"
    EXTRACTION = "extraction"
    SENTIMENT = "sentiment"
    TOPIC_MODELING = "topic_modeling"
    TIMELINE = "timeline"


@dataclass
class AnalysisResult:
    """Result of data analysis."""
    success: bool
    analysis_type: AnalysisType
    query: str
    result: Dict[str, Any] = field(default_factory=dict)
    insights: List[str] = field(default_factory=list)
    sources_used: int = 0
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "analysis_type": self.analysis_type.value,
            "query": self.query,
            "result": self.result,
            "insights": self.insights,
            "sources_used": self.sources_used,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


class DataAnalyzerAgent:
    """
    Agent for performing complex data analysis on transcripts.
    
    Capabilities:
    - Compare content across multiple transcripts
    - Identify trends and patterns
    - Generate comprehensive summaries
    - Extract specific data points
    - Analyze sentiment and tone
    """
    
    AGENT_NAME = "data-analyzer-agent"
    
    def __init__(
        self,
        vector_store_dao: Optional[VectorStoreDAO] = None,
        max_chunks: int = 10
    ):
        """
        Initialize Data Analyzer Agent.
        
        Args:
            vector_store_dao: Vector store for searching transcripts
            max_chunks: Maximum chunks to analyze at once
        """
        self.vector_store_dao = vector_store_dao or VectorStoreDAO()
        self.max_chunks = max_chunks
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
    
    async def analyze(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        transcript_ids: Optional[List[str]] = None,
        analysis_type: Optional[AnalysisType] = None
    ) -> AnalysisResult:
        """
        Perform analysis on transcript content.
        
        Args:
            query: Analysis query/question
            context: Optional context from handoff
            transcript_ids: Optional filter by transcript IDs
            analysis_type: Optional specific analysis type
            
        Returns:
            AnalysisResult with analysis details
        """
        logger.info(f"Analyzing: {query[:50]}...")
        
        try:
            # Determine analysis type if not specified
            if analysis_type is None:
                analysis_type = await self._determine_analysis_type(query)
            
            # Get context if not provided
            if context is None:
                search_results = self.vector_store_dao.search(
                    query=query,
                    n_results=self.max_chunks,
                    transcript_ids=transcript_ids
                )
                context = {
                    "query": query,
                    "chunks": search_results,
                    "chunk_count": len(search_results)
                }
            
            # Route to appropriate analysis method
            if analysis_type == AnalysisType.COMPARISON:
                return await self._compare_analysis(query, context)
            elif analysis_type == AnalysisType.TREND:
                return await self._trend_analysis(query, context)
            elif analysis_type == AnalysisType.SUMMARY:
                return await self._summary_analysis(query, context)
            elif analysis_type == AnalysisType.EXTRACTION:
                return await self._extraction_analysis(query, context)
            elif analysis_type == AnalysisType.SENTIMENT:
                return await self._sentiment_analysis(query, context)
            else:
                return await self._general_analysis(query, context, analysis_type)
        
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise AgentException(
                f"Analysis failed: {str(e)}",
                agent_name=self.AGENT_NAME
            )
    
    async def _determine_analysis_type(self, query: str) -> AnalysisType:
        """Determine the type of analysis needed."""
        query_lower = query.lower()
        
        if any(w in query_lower for w in ["compare", "difference", "versus", "vs"]):
            return AnalysisType.COMPARISON
        elif any(w in query_lower for w in ["trend", "over time", "change", "evolution"]):
            return AnalysisType.TREND
        elif any(w in query_lower for w in ["summarize", "summary", "overview", "main points"]):
            return AnalysisType.SUMMARY
        elif any(w in query_lower for w in ["extract", "list", "find all", "identify"]):
            return AnalysisType.EXTRACTION
        elif any(w in query_lower for w in ["sentiment", "tone", "feeling", "emotion"]):
            return AnalysisType.SENTIMENT
        elif any(w in query_lower for w in ["topic", "theme", "subject", "about"]):
            return AnalysisType.TOPIC_MODELING
        else:
            return AnalysisType.SUMMARY
    
    async def _compare_analysis(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> AnalysisResult:
        """Perform comparison analysis."""
        chunks = context.get("chunks", [])
        
        if not chunks:
            return AnalysisResult(
                success=False,
                analysis_type=AnalysisType.COMPARISON,
                query=query,
                result={"error": "No content found for comparison"},
                confidence=0.0
            )
        
        # Group chunks by transcript
        by_transcript = {}
        for chunk in chunks:
            tid = chunk.get("metadata", {}).get("transcript_id", "unknown")
            if tid not in by_transcript:
                by_transcript[tid] = []
            by_transcript[tid].append(chunk.get("content", ""))
        
        # Build comparison prompt
        context_text = ""
        for tid, contents in by_transcript.items():
            context_text += f"\n\n=== Transcript: {tid} ===\n"
            context_text += "\n---\n".join(contents[:3])
        
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert analyst performing comparison analysis on video transcripts.

Provide a structured comparison that includes:
1. Key similarities between the sources
2. Notable differences
3. Unique points in each source
4. Overall synthesis

Format your response as clear sections with bullet points."""
                },
                {
                    "role": "user",
                    "content": f"Compare the following transcript content:\n{context_text}\n\nComparison query: {query}"
                }
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content.strip()
        
        return AnalysisResult(
            success=True,
            analysis_type=AnalysisType.COMPARISON,
            query=query,
            result={
                "comparison": answer,
                "transcripts_compared": list(by_transcript.keys())
            },
            insights=self._extract_insights(answer),
            sources_used=len(chunks),
            confidence=0.85,
            metadata={"transcript_count": len(by_transcript)}
        )
    
    async def _trend_analysis(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> AnalysisResult:
        """Perform trend analysis."""
        chunks = context.get("chunks", [])
        
        context_text = self._build_context_text(chunks)
        
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are an analyst identifying trends and patterns in video transcript content.

Analyze for:
1. Recurring themes or topics
2. Changes or evolution in discussion
3. Patterns in how topics are addressed
4. Any temporal progression if evident

Provide specific examples from the content to support your findings."""
                },
                {
                    "role": "user",
                    "content": f"Analyze trends in:\n{context_text}\n\nQuery: {query}"
                }
            ],
            max_tokens=1200,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content.strip()
        
        return AnalysisResult(
            success=True,
            analysis_type=AnalysisType.TREND,
            query=query,
            result={"trend_analysis": answer},
            insights=self._extract_insights(answer),
            sources_used=len(chunks),
            confidence=0.8
        )
    
    async def _summary_analysis(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> AnalysisResult:
        """Generate comprehensive summary."""
        chunks = context.get("chunks", [])
        
        context_text = self._build_context_text(chunks)
        
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert summarizer for video transcript content.

Create a comprehensive summary that includes:
1. Main topics covered
2. Key points and takeaways
3. Important details or facts mentioned
4. Any conclusions or recommendations

Structure the summary with clear headings and bullet points."""
                },
                {
                    "role": "user",
                    "content": f"Summarize the following content:\n{context_text}\n\nFocus on: {query}"
                }
            ],
            max_tokens=1500,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content.strip()
        
        return AnalysisResult(
            success=True,
            analysis_type=AnalysisType.SUMMARY,
            query=query,
            result={"summary": answer},
            insights=self._extract_insights(answer),
            sources_used=len(chunks),
            confidence=0.9
        )
    
    async def _extraction_analysis(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> AnalysisResult:
        """Extract specific information."""
        chunks = context.get("chunks", [])
        
        context_text = self._build_context_text(chunks)
        
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a data extraction specialist.

Extract the requested information from the transcript content.
- Be thorough and find all instances
- Format as a clear list
- Include context for each extracted item
- Note the source when possible"""
                },
                {
                    "role": "user",
                    "content": f"Extract from this content:\n{context_text}\n\nExtraction request: {query}"
                }
            ],
            max_tokens=1200,
            temperature=0.2
        )
        
        answer = response.choices[0].message.content.strip()
        
        # Try to parse into list
        items = [line.strip() for line in answer.split('\n') if line.strip() and line.strip().startswith(('-', '•', '*', '1', '2', '3'))]
        
        return AnalysisResult(
            success=True,
            analysis_type=AnalysisType.EXTRACTION,
            query=query,
            result={
                "extracted_content": answer,
                "items": items if items else [answer]
            },
            sources_used=len(chunks),
            confidence=0.85
        )
    
    async def _sentiment_analysis(
        self,
        query: str,
        context: Dict[str, Any]
    ) -> AnalysisResult:
        """Analyze sentiment and tone."""
        chunks = context.get("chunks", [])
        
        context_text = self._build_context_text(chunks)
        
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are a sentiment and tone analyst.

Analyze the content for:
1. Overall sentiment (positive, negative, neutral, mixed)
2. Emotional tone (enthusiastic, serious, casual, etc.)
3. Speaker attitude toward topics
4. Any notable shifts in sentiment

Provide specific examples to support your analysis."""
                },
                {
                    "role": "user",
                    "content": f"Analyze sentiment in:\n{context_text}\n\nFocus: {query}"
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content.strip()
        
        return AnalysisResult(
            success=True,
            analysis_type=AnalysisType.SENTIMENT,
            query=query,
            result={"sentiment_analysis": answer},
            insights=self._extract_insights(answer),
            sources_used=len(chunks),
            confidence=0.75
        )
    
    async def _general_analysis(
        self,
        query: str,
        context: Dict[str, Any],
        analysis_type: AnalysisType
    ) -> AnalysisResult:
        """Perform general analysis for other types."""
        chunks = context.get("chunks", [])
        
        context_text = self._build_context_text(chunks)
        
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert analyst for video transcript content.
Provide thorough, well-structured analysis based on the content provided.
Support your findings with specific examples from the text."""
                },
                {
                    "role": "user",
                    "content": f"Analyze this content:\n{context_text}\n\nAnalysis request: {query}"
                }
            ],
            max_tokens=1200,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content.strip()
        
        return AnalysisResult(
            success=True,
            analysis_type=analysis_type,
            query=query,
            result={"analysis": answer},
            insights=self._extract_insights(answer),
            sources_used=len(chunks),
            confidence=0.8
        )
    
    def _build_context_text(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context text from chunks."""
        parts = []
        for i, chunk in enumerate(chunks[:self.max_chunks], 1):
            source = chunk.get("metadata", {}).get("transcript_id", "Unknown")
            content = chunk.get("content", "")
            parts.append(f"[Source {i}: {source}]\n{content}")
        return "\n\n---\n\n".join(parts)
    
    def _extract_insights(self, text: str) -> List[str]:
        """Extract key insights from analysis text."""
        insights = []
        
        # Look for bullet points or numbered items
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('-', '•', '*')) or (len(line) > 2 and line[0].isdigit() and line[1] in '.):'):
                # Clean up the insight
                insight = line.lstrip('-•*0123456789.): ').strip()
                if len(insight) > 20:  # Skip very short items
                    insights.append(insight)
        
        return insights[:5]  # Return top 5 insights