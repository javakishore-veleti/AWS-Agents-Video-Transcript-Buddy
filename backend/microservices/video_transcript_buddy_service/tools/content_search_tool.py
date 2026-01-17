"""
Content Search Tool - Searches within transcript content.

This tool provides:
- Single transcript search
- Multi-transcript search
- Cross-file search with source tracking
- Keyword and semantic search
"""

import logging
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from dao.vector_store_dao import VectorStoreDAO
from common.constants import DEFAULT_SEARCH_RESULTS, MAX_SEARCH_RESULTS

logger = logging.getLogger(__name__)


class SearchMode(Enum):
    """Search mode options."""
    SEMANTIC = "semantic"       # Vector similarity search
    KEYWORD = "keyword"         # Exact keyword matching
    HYBRID = "hybrid"           # Combination of both


@dataclass
class SearchResult:
    """Individual search result."""
    content: str
    transcript_id: str
    chunk_index: int
    score: float
    highlights: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "transcript_id": self.transcript_id,
            "chunk_index": self.chunk_index,
            "score": self.score,
            "highlights": self.highlights,
            "metadata": self.metadata
        }


@dataclass
class SearchResponse:
    """Search operation response."""
    success: bool
    query: str
    mode: SearchMode
    results: List[SearchResult] = field(default_factory=list)
    total_results: int = 0
    transcripts_searched: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "query": self.query,
            "mode": self.mode.value,
            "results": [r.to_dict() for r in self.results],
            "total_results": self.total_results,
            "transcripts_searched": self.transcripts_searched,
            "metadata": self.metadata
        }


class ContentSearchTool:
    """
    Tool for searching within transcript content.
    
    Capabilities:
    - Semantic search using vector embeddings
    - Keyword-based exact matching
    - Multi-transcript search with source tracking
    - Result highlighting
    """
    
    TOOL_NAME = "content-search-tool"
    
    def __init__(self, vector_store_dao: Optional[VectorStoreDAO] = None):
        """
        Initialize Content Search Tool.
        
        Args:
            vector_store_dao: Vector store for semantic search
        """
        self.vector_store_dao = vector_store_dao or VectorStoreDAO()
    
    async def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.SEMANTIC,
        transcript_ids: Optional[List[str]] = None,
        max_results: int = DEFAULT_SEARCH_RESULTS,
        min_score: float = 0.0
    ) -> SearchResponse:
        """
        Search for content matching the query.
        
        Args:
            query: Search query
            mode: Search mode (semantic, keyword, hybrid)
            transcript_ids: Optional filter by transcript IDs
            max_results: Maximum number of results
            min_score: Minimum relevance score
            
        Returns:
            SearchResponse with results
        """
        logger.info(f"Searching: '{query[:50]}...' mode={mode.value}")
        
        max_results = min(max_results, MAX_SEARCH_RESULTS)
        
        try:
            if mode == SearchMode.SEMANTIC:
                return await self._semantic_search(
                    query, transcript_ids, max_results, min_score
                )
            elif mode == SearchMode.KEYWORD:
                return await self._keyword_search(
                    query, transcript_ids, max_results
                )
            else:  # HYBRID
                return await self._hybrid_search(
                    query, transcript_ids, max_results, min_score
                )
        
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return SearchResponse(
                success=False,
                query=query,
                mode=mode,
                metadata={"error": str(e)}
            )
    
    async def _semantic_search(
        self,
        query: str,
        transcript_ids: Optional[List[str]],
        max_results: int,
        min_score: float
    ) -> SearchResponse:
        """Perform semantic vector search."""
        results = self.vector_store_dao.search(
            query=query,
            n_results=max_results,
            transcript_ids=transcript_ids,
            min_score=min_score
        )
        
        search_results = []
        transcripts_found = set()
        
        for result in results:
            metadata = result.get("metadata", {})
            transcript_id = metadata.get("transcript_id", "unknown")
            transcripts_found.add(transcript_id)
            
            search_results.append(SearchResult(
                content=result.get("content", ""),
                transcript_id=transcript_id,
                chunk_index=metadata.get("chunk_index", 0),
                score=result.get("score", 0),
                highlights=self._extract_highlights(result.get("content", ""), query),
                metadata=metadata
            ))
        
        return SearchResponse(
            success=True,
            query=query,
            mode=SearchMode.SEMANTIC,
            results=search_results,
            total_results=len(search_results),
            transcripts_searched=len(transcripts_found)
        )
    
    async def _keyword_search(
        self,
        query: str,
        transcript_ids: Optional[List[str]],
        max_results: int
    ) -> SearchResponse:
        """Perform keyword-based search."""
        # Get all indexed transcripts
        indexed = self.vector_store_dao.list_indexed_transcripts()
        
        # Filter by transcript_ids if specified
        if transcript_ids:
            indexed = [t for t in indexed if t["transcript_id"] in transcript_ids]
        
        search_results = []
        keywords = self._extract_keywords(query)
        
        # Search through each transcript's chunks
        for transcript in indexed:
            tid = transcript["transcript_id"]
            
            # Get all chunks for this transcript
            chunks = self.vector_store_dao.collection.get(
                where={"transcript_id": tid},
                include=["documents", "metadatas"]
            )
            
            if not chunks or not chunks.get("documents"):
                continue
            
            for i, doc in enumerate(chunks["documents"]):
                # Calculate keyword match score
                score = self._calculate_keyword_score(doc, keywords)
                
                if score > 0:
                    metadata = chunks["metadatas"][i] if chunks.get("metadatas") else {}
                    
                    search_results.append(SearchResult(
                        content=doc,
                        transcript_id=tid,
                        chunk_index=metadata.get("chunk_index", i),
                        score=score,
                        highlights=self._extract_highlights(doc, query),
                        metadata=metadata
                    ))
        
        # Sort by score and limit results
        search_results.sort(key=lambda x: x.score, reverse=True)
        search_results = search_results[:max_results]
        
        transcripts_found = set(r.transcript_id for r in search_results)
        
        return SearchResponse(
            success=True,
            query=query,
            mode=SearchMode.KEYWORD,
            results=search_results,
            total_results=len(search_results),
            transcripts_searched=len(indexed)
        )
    
    async def _hybrid_search(
        self,
        query: str,
        transcript_ids: Optional[List[str]],
        max_results: int,
        min_score: float
    ) -> SearchResponse:
        """Perform hybrid search combining semantic and keyword."""
        # Get semantic results
        semantic_response = await self._semantic_search(
            query, transcript_ids, max_results * 2, min_score
        )
        
        # Get keyword results
        keyword_response = await self._keyword_search(
            query, transcript_ids, max_results * 2
        )
        
        # Merge results
        merged = {}
        
        # Add semantic results
        for result in semantic_response.results:
            key = f"{result.transcript_id}_{result.chunk_index}"
            merged[key] = result
            # Boost score slightly for semantic matches
            merged[key].score *= 1.1
        
        # Merge keyword results
        for result in keyword_response.results:
            key = f"{result.transcript_id}_{result.chunk_index}"
            if key in merged:
                # Boost score for items found by both methods
                merged[key].score += result.score * 0.5
            else:
                merged[key] = result
        
        # Sort and limit
        combined_results = list(merged.values())
        combined_results.sort(key=lambda x: x.score, reverse=True)
        combined_results = combined_results[:max_results]
        
        transcripts_found = set(r.transcript_id for r in combined_results)
        
        return SearchResponse(
            success=True,
            query=query,
            mode=SearchMode.HYBRID,
            results=combined_results,
            total_results=len(combined_results),
            transcripts_searched=len(transcripts_found),
            metadata={
                "semantic_results": len(semantic_response.results),
                "keyword_results": len(keyword_response.results)
            }
        )
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query."""
        # Simple keyword extraction
        words = re.findall(r'\b\w{3,}\b', query.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all',
            'can', 'had', 'her', 'was', 'one', 'our', 'out', 'has',
            'what', 'when', 'where', 'which', 'who', 'how', 'this',
            'that', 'these', 'those', 'with', 'from', 'they', 'been'
        }
        
        return [w for w in words if w not in stop_words]
    
    def _calculate_keyword_score(self, text: str, keywords: List[str]) -> float:
        """Calculate keyword match score."""
        if not keywords:
            return 0.0
        
        text_lower = text.lower()
        matches = sum(1 for kw in keywords if kw in text_lower)
        
        return matches / len(keywords)
    
    def _extract_highlights(self, text: str, query: str, context_chars: int = 50) -> List[str]:
        """Extract highlighted snippets around query matches."""
        highlights = []
        keywords = self._extract_keywords(query)
        text_lower = text.lower()
        
        for keyword in keywords[:3]:  # Limit to 3 keywords
            idx = text_lower.find(keyword)
            if idx != -1:
                start = max(0, idx - context_chars)
                end = min(len(text), idx + len(keyword) + context_chars)
                
                snippet = text[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(text):
                    snippet = snippet + "..."
                
                highlights.append(snippet)
        
        return highlights[:3]
    
    async def search_single_transcript(
        self,
        query: str,
        transcript_id: str,
        max_results: int = DEFAULT_SEARCH_RESULTS
    ) -> SearchResponse:
        """Search within a single transcript."""
        return await self.search(
            query=query,
            mode=SearchMode.SEMANTIC,
            transcript_ids=[transcript_id],
            max_results=max_results
        )
    
    async def search_across_transcripts(
        self,
        query: str,
        max_results_per_transcript: int = 3
    ) -> SearchResponse:
        """Search across all transcripts, returning top results from each."""
        indexed = self.vector_store_dao.list_indexed_transcripts()
        
        all_results = []
        
        for transcript in indexed:
            response = await self.search_single_transcript(
                query=query,
                transcript_id=transcript["transcript_id"],
                max_results=max_results_per_transcript
            )
            all_results.extend(response.results)
        
        # Sort all results by score
        all_results.sort(key=lambda x: x.score, reverse=True)
        
        return SearchResponse(
            success=True,
            query=query,
            mode=SearchMode.SEMANTIC,
            results=all_results,
            total_results=len(all_results),
            transcripts_searched=len(indexed)
        )