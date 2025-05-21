from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import faiss
import numpy as np
from typing import List, Dict, Union
from pathlib import Path
import PyPDF2  # For PDF handling
import re

class Retriever:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', chunk_size: int = 512, chunk_overlap: int = 100):
        """
        Initialize the Retriever with a sentence transformer model and chunking parameters.
        
        Args:
            model_name: Name of the SentenceTransformer model to use
            chunk_size: Size of document chunks (in characters)
            chunk_overlap: Overlap between chunks (in characters)
        """
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],  # Prioritize sentence boundaries
            length_function=len,
            is_separator_regex=False
        )
        self.index = None
        self.documents = []
        self.chunks = []
        
    def add_documents(self, documents: List[Union[str, Dict]]):
        """
        Add documents to the retriever. Documents can be either strings or dictionaries.
        If dictionaries, they should have a "text" key.
        
        Args:
            documents: List of documents to add
        """
        # Process documents into chunks
        new_chunks = []
        for doc in documents:
            if isinstance(doc, dict):
                text = doc.get('text', '')
                metadata = {k: v for k, v in doc.items() if k != 'text'}
            else:
                text = str(doc)
                metadata = {}
            
            chunks = self.text_splitter.split_text(text)
            for chunk in chunks:
                self.chunks.append({
                    'text': chunk,
                    'metadata': metadata
                })
                new_chunks.append(chunk)
        
        # Generate embeddings for new chunks
        if new_chunks:
            new_embeddings = self.model.encode(new_chunks, show_progress_bar=True)
            
            # Initialize index if it doesn't exist
            if self.index is None:
                self.index = faiss.IndexFlatL2(self.embedding_dim)
                self.index.add(new_embeddings)
            else:
                self.index.add(new_embeddings)
        
        # Store original documents
        self.documents.extend(documents)
    
    def query(self, query_text: str, k: int = 5) -> List[Dict]:
        """
        Query the retriever for similar documents.
        
        Args:
            query_text: The query text
            k: Number of results to return
            
        Returns:
            List of dictionaries containing 'text', 'metadata', and 'score'
        """
        if self.index is None or len(self.chunks) == 0:
            return []
        
        # Embed the query
        query_embedding = self.model.encode([query_text])
        
        # Search the index
        distances, indices = self.index.search(query_embedding, k)
        
        # Prepare results
        results = []
        for idx, score in zip(indices[0], distances[0]):
            if idx >= 0:  # FAISS may return -1 for invalid indices
                chunk = self.chunks[idx]
                # Convert distance to similarity score (lower distance = higher similarity)
                similarity_score = 1.0 / (1.0 + float(score))
                results.append({
                    'text': chunk['text'],
                    'metadata': chunk['metadata'],
                    'score': similarity_score
                })
        
        # Sort by similarity score (highest first)
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def save_index(self, filepath: str):
        """Save the FAISS index to disk"""
        if self.index is not None:
            faiss.write_index(self.index, filepath)
    
    def load_index(self, filepath: str):
        """Load a FAISS index from disk"""
        self.index = faiss.read_index(filepath)


    def _read_file(self, file_path: Union[str, Path]) -> str:
        """Read different file types and return text content"""
        file_path = Path(file_path)
        text = ""
        
        if file_path.suffix == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
        elif file_path.suffix == '.md':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
        elif file_path.suffix == '.pdf':
            text = ""
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text()
        
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
        return self._preprocess_text(text)

    def _preprocess_text(self, text: str) -> str:
        """Basic text preprocessing"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s.,!?-]', ' ', text)
        # Ensure proper spacing around punctuation
        text = re.sub(r'\s+([.,!?])', r'\1', text)
        return text

    def add_file(self, file_path: Union[str, Path], metadata: dict = None):
        """Add a single file to the retriever"""
        if metadata is None:
            metadata = {}
        
        text = self._read_file(file_path)
        doc = {
            "text": text,
            **metadata,
            "source": str(file_path)
        }
        self.add_documents([doc])

    def add_directory(self, dir_path: Union[str, Path], glob_pattern: str = "*"):
        """Add all matching files in a directory"""
        dir_path = Path(dir_path)
        for file_path in dir_path.glob(glob_pattern):
            if file_path.is_file():
                try:
                    self.add_file(file_path)
                    print(f"Processed: {file_path}")
                except Exception as e:
                    print(f"Failed to process {file_path}: {str(e)}")