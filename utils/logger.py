import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

class RAGLogger:
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize the RAG Logger.
        
        Args:
            log_dir (str): Directory to store log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.log_file = self.log_dir / f"rag_logs_{datetime.now().strftime('%Y%m%d')}.jsonl"
        
    def log_query(self, 
                 question: str,
                 retrieved_chunks: List[str],
                 prompt: str,
                 generated_answer: str,
                 group_id: Optional[str] = None,
                 retrieval_scores: Optional[List[float]] = None,
                 chunk_ids: Optional[List[str]] = None) -> None:
        """
        Log a single RAG query and its results.
        
        Args:
            question (str): Input question
            retrieved_chunks (List[str]): Retrieved context chunks
            prompt (str): Final prompt sent to LLM
            generated_answer (str): Generated answer
            group_id (str, optional): Group identifier for the query
            retrieval_scores (List[float], optional): Scores for retrieved chunks
            chunk_ids (List[str], optional): IDs of retrieved chunks
        """
        log_entry = {
            "question": question,
            "retrieved_chunks": retrieved_chunks,
            "prompt": prompt,
            "generated_answer": generated_answer,
            "timestamp": datetime.now().isoformat(),
            "group_id": group_id or str(uuid.uuid4()),
            "retrieval_scores": retrieval_scores,
            "chunk_ids": chunk_ids
        }
        
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    def get_recent_logs(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get the n most recent log entries.
        
        Args:
            n (int): Number of recent entries to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of recent log entries
        """
        if not self.log_file.exists():
            return []
            
        logs = []
        with open(self.log_file, 'r') as f:
            for line in f:
                logs.append(json.loads(line))
                
        return logs[-n:] 