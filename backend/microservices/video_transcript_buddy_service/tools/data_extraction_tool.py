"""
Data Extraction Tool - Extracts patterns and entities from content.

This tool provides:
- Named entity extraction (people, places, organizations)
- Pattern matching and extraction
- Key phrase extraction
- Structured data extraction
- Summarization
"""

import logging
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

from openai import OpenAI
from config import settings
from common.exceptions import AgentException

logger = logging.getLogger(__name__)


class ExtractionType(Enum):
    """Types of extraction available."""
    ENTITIES = "entities"           # Named entities
    KEY_PHRASES = "key_phrases"     # Important phrases
    TOPICS = "topics"               # Main topics
    FACTS = "facts"                 # Factual statements
    QUOTES = "quotes"               # Direct quotes
    NUMBERS = "numbers"             # Numerical data
    DATES = "dates"                 # Date references
    ACTIONS = "actions"             # Action items
    QUESTIONS = "questions"         # Questions asked
    CUSTOM = "custom"               # Custom pattern


@dataclass
class ExtractedItem:
    """Individual extracted item."""
    item_type: str
    value: str
    context: str = ""
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.item_type,
            "value": self.value,
            "context": self.context,
            "confidence": self.confidence,
            "metadata": self.metadata
        }


@dataclass
class ExtractionResult:
    """Result of extraction operation."""
    success: bool
    extraction_type: ExtractionType
    items: List[ExtractedItem] = field(default_factory=list)
    summary: str = ""
    total_items: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "extraction_type": self.extraction_type.value,
            "items": [item.to_dict() for item in self.items],
            "summary": self.summary,
            "total_items": self.total_items,
            "metadata": self.metadata
        }


class DataExtractionTool:
    """
    Tool for extracting patterns and entities from transcript content.
    
    Capabilities:
    - Named entity recognition
    - Key phrase extraction
    - Topic identification
    - Fact extraction
    - Quote extraction
    - Custom pattern matching
    """
    
    TOOL_NAME = "data-extraction-tool"
    
    # Common patterns for rule-based extraction
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "url": r'https?://[^\s]+',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "date": r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4})\b',
        "time": r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b',
        "percentage": r'\b\d+(?:\.\d+)?%\b',
        "money": r'\$\d+(?:,\d{3})*(?:\.\d{2})?(?:\s*(?:million|billion|M|B|K))?\b',
        "number": r'\b\d+(?:,\d{3})*(?:\.\d+)?\b',
    }
    
    def __init__(self, use_llm: bool = True):
        """
        Initialize Data Extraction Tool.
        
        Args:
            use_llm: Whether to use LLM for advanced extraction
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
                    agent_name=self.TOOL_NAME
                )
            self._openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self._openai_client
    
    async def extract(
        self,
        content: str,
        extraction_type: ExtractionType,
        custom_pattern: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> ExtractionResult:
        """
        Extract information from content.
        
        Args:
            content: Text content to extract from
            extraction_type: Type of extraction to perform
            custom_pattern: Regex pattern for custom extraction
            custom_prompt: Custom prompt for LLM extraction
            
        Returns:
            ExtractionResult with extracted items
        """
        logger.info(f"Extracting {extraction_type.value} from content")
        
        try:
            if extraction_type == ExtractionType.ENTITIES:
                return await self._extract_entities(content)
            elif extraction_type == ExtractionType.KEY_PHRASES:
                return await self._extract_key_phrases(content)
            elif extraction_type == ExtractionType.TOPICS:
                return await self._extract_topics(content)
            elif extraction_type == ExtractionType.FACTS:
                return await self._extract_facts(content)
            elif extraction_type == ExtractionType.QUOTES:
                return await self._extract_quotes(content)
            elif extraction_type == ExtractionType.NUMBERS:
                return self._extract_numbers(content)
            elif extraction_type == ExtractionType.DATES:
                return self._extract_dates(content)
            elif extraction_type == ExtractionType.ACTIONS:
                return await self._extract_actions(content)
            elif extraction_type == ExtractionType.QUESTIONS:
                return self._extract_questions(content)
            elif extraction_type == ExtractionType.CUSTOM:
                if custom_pattern:
                    return self._extract_custom_pattern(content, custom_pattern)
                elif custom_prompt:
                    return await self._extract_custom_llm(content, custom_prompt)
                else:
                    return ExtractionResult(
                        success=False,
                        extraction_type=extraction_type,
                        metadata={"error": "Custom extraction requires pattern or prompt"}
                    )
            else:
                return ExtractionResult(
                    success=False,
                    extraction_type=extraction_type,
                    metadata={"error": f"Unknown extraction type: {extraction_type}"}
                )
        
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            return ExtractionResult(
                success=False,
                extraction_type=extraction_type,
                metadata={"error": str(e)}
            )
    
    async def _extract_entities(self, content: str) -> ExtractionResult:
        """Extract named entities using LLM."""
        if not self.use_llm:
            return self._extract_entities_simple(content)
        
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """Extract named entities from the text. Identify:
- PERSON: Names of people
- ORG: Organizations, companies
- PLACE: Locations, cities, countries
- PRODUCT: Products, technologies
- EVENT: Events, conferences

Return as JSON array:
[{"type": "PERSON", "value": "John Smith", "context": "brief context"}]"""
                },
                {
                    "role": "user",
                    "content": f"Extract entities from:\n\n{content[:3000]}"
                }
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        items = self._parse_llm_response(response.choices[0].message.content, "entity")
        
        return ExtractionResult(
            success=True,
            extraction_type=ExtractionType.ENTITIES,
            items=items,
            total_items=len(items),
            summary=f"Found {len(items)} named entities"
        )
    
    def _extract_entities_simple(self, content: str) -> ExtractionResult:
        """Simple entity extraction using patterns."""
        items = []
        
        patterns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', content)
        
        for pattern in set(patterns):
            items.append(ExtractedItem(
                item_type="ENTITY",
                value=pattern,
                confidence=0.6
            ))
        
        return ExtractionResult(
            success=True,
            extraction_type=ExtractionType.ENTITIES,
            items=items[:20],
            total_items=len(items)
        )
    
    async def _extract_key_phrases(self, content: str) -> ExtractionResult:
        """Extract key phrases using LLM."""
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """Extract the most important key phrases from the text.
Focus on:
- Main concepts and ideas
- Technical terms
- Important statements

Return as JSON array:
[{"value": "key phrase", "importance": "high/medium/low"}]"""
                },
                {
                    "role": "user",
                    "content": f"Extract key phrases from:\n\n{content[:3000]}"
                }
            ],
            max_tokens=800,
            temperature=0.2
        )
        
        items = self._parse_llm_response(response.choices[0].message.content, "key_phrase")
        
        return ExtractionResult(
            success=True,
            extraction_type=ExtractionType.KEY_PHRASES,
            items=items,
            total_items=len(items),
            summary=f"Found {len(items)} key phrases"
        )
    
    async def _extract_topics(self, content: str) -> ExtractionResult:
        """Extract main topics using LLM."""
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """Identify the main topics discussed in the text.
For each topic provide:
- Topic name
- Brief description
- Relevance (how central to the content)

Return as JSON array:
[{"value": "topic name", "description": "brief description", "relevance": "primary/secondary"}]"""
                },
                {
                    "role": "user",
                    "content": f"Identify topics in:\n\n{content[:3000]}"
                }
            ],
            max_tokens=800,
            temperature=0.2
        )
        
        items = self._parse_llm_response(response.choices[0].message.content, "topic")
        
        return ExtractionResult(
            success=True,
            extraction_type=ExtractionType.TOPICS,
            items=items,
            total_items=len(items),
            summary=f"Found {len(items)} topics"
        )
    
    async def _extract_facts(self, content: str) -> ExtractionResult:
        """Extract factual statements using LLM."""
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """Extract factual statements from the text.
Focus on:
- Verifiable facts
- Statistics and data points
- Definitions
- Claims with evidence

Return as JSON array:
[{"value": "factual statement", "type": "statistic/claim/definition"}]"""
                },
                {
                    "role": "user",
                    "content": f"Extract facts from:\n\n{content[:3000]}"
                }
            ],
            max_tokens=1000,
            temperature=0.1
        )
        
        items = self._parse_llm_response(response.choices[0].message.content, "fact")
        
        return ExtractionResult(
            success=True,
            extraction_type=ExtractionType.FACTS,
            items=items,
            total_items=len(items),
            summary=f"Found {len(items)} factual statements"
        )
    
    async def _extract_quotes(self, content: str) -> ExtractionResult:
        """Extract direct quotes."""
        items = []
        
        quote_patterns = [
            r'"([^"]+)"',
            r"'([^']+)'",
            r'"([^"]+)"',
            r''([^']+)''
        ]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 10:
                    items.append(ExtractedItem(
                        item_type="quote",
                        value=match,
                        confidence=0.9
                    ))
        
        seen = set()
        unique_items = []
        for item in items:
            if item.value not in seen:
                seen.add(item.value)
                unique_items.append(item)
        
        return ExtractionResult(
            success=True,
            extraction_type=ExtractionType.QUOTES,
            items=unique_items[:15],
            total_items=len(unique_items),
            summary=f"Found {len(unique_items)} quotes"
        )
    
    def _extract_numbers(self, content: str) -> ExtractionResult:
        """Extract numerical data."""
        items = []
        
        for match in re.finditer(self.PATTERNS["percentage"], content):
            context_start = max(0, match.start() - 30)
            context_end = min(len(content), match.end() + 30)
            items.append(ExtractedItem(
                item_type="percentage",
                value=match.group(),
                context=content[context_start:context_end],
                confidence=0.95
            ))
        
        for match in re.finditer(self.PATTERNS["money"], content):
            context_start = max(0, match.start() - 30)
            context_end = min(len(content), match.end() + 30)
            items.append(ExtractedItem(
                item_type="money",
                value=match.group(),
                context=content[context_start:context_end],
                confidence=0.95
            ))
        
        return ExtractionResult(
            success=True,
            extraction_type=ExtractionType.NUMBERS,
            items=items[:20],
            total_items=len(items),
            summary=f"Found {len(items)} numerical values"
        )
    
    def _extract_dates(self, content: str) -> ExtractionResult:
        """Extract date references."""
        items = []
        
        for match in re.finditer(self.PATTERNS["date"], content, re.IGNORECASE):
            context_start = max(0, match.start() - 30)
            context_end = min(len(content), match.end() + 30)
            items.append(ExtractedItem(
                item_type="date",
                value=match.group(),
                context=content[context_start:context_end],
                confidence=0.9
            ))
        
        return ExtractionResult(
            success=True,
            extraction_type=ExtractionType.DATES,
            items=items[:15],
            total_items=len(items),
            summary=f"Found {len(items)} date references"
        )
    
    async def _extract_actions(self, content: str) -> ExtractionResult:
        """Extract action items using LLM."""
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """Extract action items and to-dos from the text.
Look for:
- Tasks mentioned
- Commitments made
- Next steps discussed
- Recommendations

Return as JSON array:
[{"value": "action item", "priority": "high/medium/low", "assignee": "person if mentioned"}]"""
                },
                {
                    "role": "user",
                    "content": f"Extract action items from:\n\n{content[:3000]}"
                }
            ],
            max_tokens=800,
            temperature=0.2
        )
        
        items = self._parse_llm_response(response.choices[0].message.content, "action")
        
        return ExtractionResult(
            success=True,
            extraction_type=ExtractionType.ACTIONS,
            items=items,
            total_items=len(items),
            summary=f"Found {len(items)} action items"
        )
    
    def _extract_questions(self, content: str) -> ExtractionResult:
        """Extract questions from content."""
        items = []
        
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if '?' in sentence or (len(sentence) > 10 and sentence.lower().startswith(
                ('who', 'what', 'where', 'when', 'why', 'how', 'is', 'are', 'do', 'does', 'can', 'could', 'would', 'should')
            )):
                items.append(ExtractedItem(
                    item_type="question",
                    value=sentence,
                    confidence=0.8
                ))
        
        return ExtractionResult(
            success=True,
            extraction_type=ExtractionType.QUESTIONS,
            items=items[:15],
            total_items=len(items),
            summary=f"Found {len(items)} questions"
        )
    
    def _extract_custom_pattern(self, content: str, pattern: str) -> ExtractionResult:
        """Extract using custom regex pattern."""
        items = []
        
        try:
            for match in re.finditer(pattern, content):
                context_start = max(0, match.start() - 30)
                context_end = min(len(content), match.end() + 30)
                items.append(ExtractedItem(
                    item_type="custom",
                    value=match.group(),
                    context=content[context_start:context_end],
                    confidence=0.85
                ))
        except re.error as e:
            return ExtractionResult(
                success=False,
                extraction_type=ExtractionType.CUSTOM,
                metadata={"error": f"Invalid regex pattern: {e}"}
            )
        
        return ExtractionResult(
            success=True,
            extraction_type=ExtractionType.CUSTOM,
            items=items[:20],
            total_items=len(items),
            summary=f"Found {len(items)} matches"
        )
    
    async def _extract_custom_llm(self, content: str, prompt: str) -> ExtractionResult:
        """Extract using custom LLM prompt."""
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"""You are a data extraction assistant.
{prompt}

Return results as JSON array:
[{{"value": "extracted item", "context": "relevant context"}}]"""
                },
                {
                    "role": "user",
                    "content": f"Extract from:\n\n{content[:3000]}"
                }
            ],
            max_tokens=1000,
            temperature=0.2
        )
        
        items = self._parse_llm_response(response.choices[0].message.content, "custom")
        
        return ExtractionResult(
            success=True,
            extraction_type=ExtractionType.CUSTOM,
            items=items,
            total_items=len(items),
            summary=f"Found {len(items)} items"
        )
    
    def _parse_llm_response(self, response: str, item_type: str) -> List[ExtractedItem]:
        """Parse LLM JSON response into ExtractedItem list."""
        import json
        
        items = []
        
        try:
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                
                for entry in data:
                    if isinstance(entry, dict):
                        items.append(ExtractedItem(
                            item_type=entry.get("type", item_type),
                            value=entry.get("value", str(entry)),
                            context=entry.get("context", ""),
                            confidence=0.85,
                            metadata={k: v for k, v in entry.items() if k not in ["type", "value", "context"]}
                        ))
                    else:
                        items.append(ExtractedItem(
                            item_type=item_type,
                            value=str(entry),
                            confidence=0.8
                        ))
        except json.JSONDecodeError:
            lines = response.strip().split('\n')
            for line in lines:
                line = line.strip().lstrip('-•*')
                if line and len(line) > 5:
                    items.append(ExtractedItem(
                        item_type=item_type,
                        value=line,
                        confidence=0.7
                    ))
        
        return items[:20]
    
    async def summarize(self, content: str, max_length: int = 200) -> str:
        """Generate a brief summary of content."""
        response = self.openai_client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": f"Summarize the following content in {max_length} words or less. Be concise and capture the main points."
                },
                {
                    "role": "user",
                    "content": content[:3000]
                }
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()