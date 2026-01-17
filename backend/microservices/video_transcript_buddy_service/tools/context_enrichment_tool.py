"""
Context Enrichment Tool - Enriches context with additional information.

This tool provides:
- Related content discovery
- Context expansion from surrounding chunks
- Cross-reference identification
- Metadata enrichment
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from dao.vector_store_dao import VectorStoreDAO
from dao.s3_dao import S3DAO

logger = logging.getLogger(__name__)


@dataclass
class EnrichedContext:
    """Enriched context with additional information."""
    original_content: str
    transcript_id: str
    enrichments: Dict[str, Any] = field(default_factory=dict)
    related_chunks: List[Dict[str, Any]] = field(default_factory=list)
    surrounding_context: Dict[str, str] = field(default_factory=dict)
    cross_references: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "original_content": self.original_content,
            "transcript_id": self.transcript_id,
            "enrichments": self.enrichments,
            "related_chunks": self.related_chunks,
            "surrounding_context": self.surrounding_context,
            "cross_references": self.cross_references,
            "metadata": self.metadata
        }


@dataclass
class EnrichmentResponse:
    """Response from enrichment operation."""
    success: bool
    contexts: List[EnrichedContext] = field(default_factory=list)
    total_enrichments: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "contexts": [c.to_dict() for c in self.contexts],
            "total_enrichments": self.total_enrichments,
            "metadata": self.metadata
        }


class ContextEnrichmentTool:
    """
    Tool for enriching context with additional information.
    
    Capabilities:
    - Find related content in other parts of transcripts
    - Expand context with surrounding chunks
    - Identify cross-references between transcripts
    - Add metadata and annotations
    """
    
    TOOL_NAME = "context-enrichment-tool"
    
    def __init__(
        self,
        vector_store_dao: Optional[VectorStoreDAO] = None,
        s3_dao: Optional[S3DAO] = None
    ):
        """
        Initialize Context Enrichment Tool.
        
        Args:
            vector_store_dao: Vector store for finding related content
            s3_dao: S3 DAO for accessing transcript metadata
        """
        self.vector_store_dao = vector_store_dao or VectorStoreDAO()
        self.s3_dao = s3_dao or S3DAO()
    
    async def enrich(
        self,
        content: str,
        transcript_id: str,
        chunk_index: Optional[int] = None,
        include_related: bool = True,
        include_surrounding: bool = True,
        include_cross_refs: bool = True,
        max_related: int = 3
    ) -> EnrichedContext:
        """
        Enrich a piece of content with additional context.
        
        Args:
            content: Content to enrich
            transcript_id: Source transcript ID
            chunk_index: Optional chunk index for surrounding context
            include_related: Include related content
            include_surrounding: Include surrounding chunks
            include_cross_refs: Include cross-references
            max_related: Maximum related items to include
            
        Returns:
            EnrichedContext with enrichments
        """
        logger.info(f"Enriching content from {transcript_id}")
        
        enriched = EnrichedContext(
            original_content=content,
            transcript_id=transcript_id
        )
        
        try:
            # Get related content
            if include_related:
                related = await self._find_related_content(
                    content, transcript_id, max_related
                )
                enriched.related_chunks = related
                enriched.enrichments["related_count"] = len(related)
            
            # Get surrounding context
            if include_surrounding and chunk_index is not None:
                surrounding = await self._get_surrounding_context(
                    transcript_id, chunk_index
                )
                enriched.surrounding_context = surrounding
                enriched.enrichments["has_surrounding"] = bool(surrounding)
            
            # Find cross-references
            if include_cross_refs:
                cross_refs = await self._find_cross_references(
                    content, transcript_id
                )
                enriched.cross_references = cross_refs
                enriched.enrichments["cross_ref_count"] = len(cross_refs)
            
            # Add transcript metadata
            enriched.metadata = await self._get_transcript_metadata(transcript_id)
            
            return enriched
        
        except Exception as e:
            logger.error(f"Enrichment failed: {e}")
            enriched.enrichments["error"] = str(e)
            return enriched
    
    async def enrich_multiple(
        self,
        items: List[Dict[str, Any]],
        include_related: bool = True,
        include_surrounding: bool = True,
        include_cross_refs: bool = False  # Disabled by default for performance
    ) -> EnrichmentResponse:
        """
        Enrich multiple content items.
        
        Args:
            items: List of items with content, transcript_id, chunk_index
            include_related: Include related content
            include_surrounding: Include surrounding chunks
            include_cross_refs: Include cross-references
            
        Returns:
            EnrichmentResponse with all enriched contexts
        """
        logger.info(f"Enriching {len(items)} items")
        
        enriched_contexts = []
        
        for item in items:
            enriched = await self.enrich(
                content=item.get("content", ""),
                transcript_id=item.get("transcript_id", "unknown"),
                chunk_index=item.get("chunk_index"),
                include_related=include_related,
                include_surrounding=include_surrounding,
                include_cross_refs=include_cross_refs
            )
            enriched_contexts.append(enriched)
        
        total_enrichments = sum(
            len(c.related_chunks) + len(c.cross_references) + 
            (1 if c.surrounding_context else 0)
            for c in enriched_contexts
        )
        
        return EnrichmentResponse(
            success=True,
            contexts=enriched_contexts,
            total_enrichments=total_enrichments,
            metadata={"items_processed": len(items)}
        )
    
    async def _find_related_content(
        self,
        content: str,
        exclude_transcript_id: str,
        max_results: int
    ) -> List[Dict[str, Any]]:
        """Find related content in other transcripts."""
        # Search for similar content
        results = self.vector_store_dao.search(
            query=content[:500],  # Use first 500 chars as query
            n_results=max_results + 5  # Get extra to filter
        )
        
        # Filter out content from same transcript
        related = []
        for result in results:
            tid = result.get("metadata", {}).get("transcript_id", "")
            if tid != exclude_transcript_id:
                related.append({
                    "content": result.get("content", "")[:300] + "...",
                    "transcript_id": tid,
                    "score": result.get("score", 0),
                    "chunk_index": result.get("metadata", {}).get("chunk_index", 0)
                })
                
                if len(related) >= max_results:
                    break
        
        return related
    
    async def _get_surrounding_context(
        self,
        transcript_id: str,
        chunk_index: int
    ) -> Dict[str, str]:
        """Get surrounding chunks for context."""
        surrounding = {}
        
        try:
            # Get previous chunk
            if chunk_index > 0:
                prev_results = self.vector_store_dao.collection.get(
                    where={
                        "$and": [
                            {"transcript_id": transcript_id},
                            {"chunk_index": chunk_index - 1}
                        ]
                    },
                    include=["documents"]
                )
                if prev_results and prev_results.get("documents"):
                    surrounding["previous"] = prev_results["documents"][0]
            
            # Get next chunk
            next_results = self.vector_store_dao.collection.get(
                where={
                    "$and": [
                        {"transcript_id": transcript_id},
                        {"chunk_index": chunk_index + 1}
                    ]
                },
                include=["documents"]
            )
            if next_results and next_results.get("documents"):
                surrounding["next"] = next_results["documents"][0]
        
        except Exception as e:
            logger.warning(f"Failed to get surrounding context: {e}")
        
        return surrounding
    
    async def _find_cross_references(
        self,
        content: str,
        source_transcript_id: str
    ) -> List[Dict[str, Any]]:
        """Find cross-references to other transcripts."""
        cross_refs = []
        
        # Extract potential reference terms (names, topics, etc.)
        # This is a simplified implementation
        import re
        
        # Look for capitalized phrases (potential names/topics)
        patterns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', content)
        unique_patterns = list(set(patterns))[:5]  # Limit to 5
        
        for pattern in unique_patterns:
            if len(pattern) < 3:
                continue
            
            # Search for this pattern in other transcripts
            results = self.vector_store_dao.search(
                query=pattern,
                n_results=3
            )
            
            for result in results:
                tid = result.get("metadata", {}).get("transcript_id", "")
                if tid != source_transcript_id and result.get("score", 0) > 0.5:
                    cross_refs.append({
                        "reference_term": pattern,
                        "transcript_id": tid,
                        "score": result.get("score", 0),
                        "preview": result.get("content", "")[:150] + "..."
                    })
        
        # Deduplicate by transcript
        seen = set()
        unique_refs = []
        for ref in cross_refs:
            if ref["transcript_id"] not in seen:
                seen.add(ref["transcript_id"])
                unique_refs.append(ref)
        
        return unique_refs[:5]  # Limit to 5 cross-references
    
    async def _get_transcript_metadata(self, transcript_id: str) -> Dict[str, Any]:
        """Get metadata for a transcript."""
        try:
            # Try to get from vector store first
            info = self.vector_store_dao.get_transcript_info(transcript_id)
            if info:
                return {
                    "chunk_count": info.get("chunk_count", 0),
                    "indexed_at": info.get("indexed_at", ""),
                    "source": "vector_store"
                }
            
            # Fall back to S3 if available
            if self.s3_dao.transcript_exists(transcript_id):
                return {
                    "exists_in_s3": True,
                    "source": "s3"
                }
            
            return {}
        
        except Exception as e:
            logger.warning(f"Failed to get transcript metadata: {e}")
            return {}
    
    async def expand_context(
        self,
        content: str,
        transcript_id: str,
        expansion_size: int = 2
    ) -> str:
        """
        Expand content with surrounding context.
        
        Args:
            content: Original content
            transcript_id: Source transcript
            expansion_size: Number of chunks to include before/after
            
        Returns:
            Expanded content string
        """
        # Find the chunk index for this content
        results = self.vector_store_dao.search(
            query=content[:200],
            n_results=1,
            transcript_ids=[transcript_id]
        )
        
        if not results:
            return content
        
        chunk_index = results[0].get("metadata", {}).get("chunk_index", 0)
        
        # Collect surrounding chunks
        chunks = []
        
        for i in range(chunk_index - expansion_size, chunk_index + expansion_size + 1):
            if i < 0:
                continue
            
            try:
                chunk_results = self.vector_store_dao.collection.get(
                    where={
                        "$and": [
                            {"transcript_id": transcript_id},
                            {"chunk_index": i}
                        ]
                    },
                    include=["documents"]
                )
                if chunk_results and chunk_results.get("documents"):
                    chunks.append((i, chunk_results["documents"][0]))
            except:
                pass
        
        # Sort by chunk index and join
        chunks.sort(key=lambda x: x[0])
        expanded = "\n\n".join(chunk[1] for chunk in chunks)
        
        return expanded