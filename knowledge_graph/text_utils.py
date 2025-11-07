"""
Text processing utilities for the knowledge graph generator.
"""
import re

def chunk_text(text, config):
    """
    Split the input text into a list of chunks separated by markers like [Đoạn i].
    Each chunk corresponds to one paragraph.
    """
    if not config.get("chunking", {}).get("already_chunked", False):
        return default_chunk_text(text, config)
    chunks = re.split(r'\[Đoạn\s*\d+\]\s*', text)
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    return chunks

def default_chunk_text(text, config):
    """
    Split a text into chunks of words with overlap.
    
    Args:
        text: The input text to chunk
        chunk_size: The size of each chunk in words
        overlap: The number of words to overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunk_size = config.get("chunking", {}).get("chunk_size", 500)
    overlap = config.get("chunking", {}).get("overlap", 50)
    
    # Split text into words
    words = text.split()
    
    # If text is smaller than chunk size, return it as a single chunk
    if len(words) <= chunk_size:
        return [text]
    
    # Create chunks with overlap
    chunks = []
    start = 0
    
    while start < len(words):
        # Calculate end position for this chunk
        end = min(start + chunk_size, len(words))
        
        # Join words for this chunk
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        
        # Move start position for next chunk, accounting for overlap
        start = end - overlap
        
        # If we're near the end and the last chunk would be too small, just exit
        if start < len(words) and start + chunk_size - overlap >= len(words):
            # Add remaining words as the final chunk
            final_chunk = ' '.join(words[start:])
            chunks.append(final_chunk)
            break
    
    return chunks 