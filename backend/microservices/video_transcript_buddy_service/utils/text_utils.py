"""
Text Utilities - Helper functions for text processing.
"""

import re
import os
from typing import List, Optional
from common.constants import (
    SUPPORTED_FILE_EXTENSIONS,
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    MAX_FILE_SIZE_BYTES,
)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing unsafe characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Sanitized filename
    """
    # Remove path separators
    filename = os.path.basename(filename)
    
    # Replace unsafe characters with underscores
    filename = re.sub(r'[^\w\-_\.]', '_', filename)
    
    # Remove multiple consecutive underscores
    filename = re.sub(r'_+', '_', filename)
    
    # Remove leading/trailing underscores
    filename = filename.strip('_')
    
    return filename


def get_file_extension(filename: str) -> str:
    """
    Get file extension in lowercase.
    
    Args:
        filename: Filename with extension
        
    Returns:
        str: File extension (e.g., '.txt')
    """
    _, ext = os.path.splitext(filename)
    return ext.lower()


def is_supported_file(filename: str) -> bool:
    """
    Check if file type is supported.
    
    Args:
        filename: Filename to check
        
    Returns:
        bool: True if supported
    """
    ext = get_file_extension(filename)
    return ext in SUPPORTED_FILE_EXTENSIONS


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size (e.g., '2.5 MB')
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def validate_file_size(size_bytes: int) -> bool:
    """
    Check if file size is within allowed limits.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        bool: True if within limits
    """
    return size_bytes <= MAX_FILE_SIZE_BYTES


def chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
) -> List[str]:
    """
    Split text into overlapping chunks for vector store indexing.
    
    Args:
        text: Text to split
        chunk_size: Maximum characters per chunk
        chunk_overlap: Overlap between consecutive chunks
        
    Returns:
        List[str]: List of text chunks
    """
    if not text or not text.strip():
        return []
    
    # Clean the text
    text = text.strip()
    
    # If text is smaller than chunk size, return as single chunk
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        # Get chunk
        end = start + chunk_size
        chunk = text[start:end]
        
        # Try to break at sentence boundary if not at end
        if end < len(text):
            # Look for last sentence boundary in chunk
            last_period = chunk.rfind('. ')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size // 2:
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunks.append(chunk.strip())
        
        # Move start position with overlap
        start = end - chunk_overlap
        
        # Prevent infinite loop
        if start >= len(text):
            break
    
    return chunks


def clean_transcript_text(text: str) -> str:
    """
    Clean transcript text by removing timestamps and formatting.
    
    Args:
        text: Raw transcript text
        
    Returns:
        str: Cleaned text
    """
    # Remove SRT timestamps (00:00:00,000 --> 00:00:00,000)
    text = re.sub(r'\d{2}:\d{2}:\d{2}[,\.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,\.]\d{3}', '', text)
    
    # Remove VTT timestamps (00:00:00.000 --> 00:00:00.000)
    text = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}', '', text)
    
    # Remove sequence numbers (standalone numbers on a line)
    text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
    
    # Remove VTT header
    text = re.sub(r'^WEBVTT\s*', '', text, flags=re.MULTILINE)
    
    # Remove multiple blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract simple keywords from text.
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords
        
    Returns:
        List[str]: List of keywords
    """
    # Simple keyword extraction (can be enhanced with NLP)
    # Remove common stop words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'this',
        'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
        'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
        'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
        'not', 'only', 'same', 'so', 'than', 'too', 'very', 'just', 'also'
    }
    
    # Extract words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    
    # Count word frequency
    word_counts = {}
    for word in words:
        if word not in stop_words:
            word_counts[word] = word_counts.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, count in sorted_words[:max_keywords]]


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    truncated = text[:max_length - len(suffix)]
    
    # Try to break at word boundary
    last_space = truncated.rfind(' ')
    if last_space > max_length // 2:
        truncated = truncated[:last_space]
    
    return truncated + suffix