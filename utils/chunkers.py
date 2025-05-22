from typing import List
import re

class TextChunker:
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Advanced chunking with sentence awareness"""
        if not text:
            return []
            
        # Split at sentence boundaries when possible
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = []
        current_len = 0
        
        for sentence in sentences:
            sentence_len = len(sentence)
            if current_len + sentence_len > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = current_chunk[-overlap:] if overlap else []
                current_len = sum(len(s) for s in current_chunk)
            current_chunk.append(sentence)
            current_len += sentence_len
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks