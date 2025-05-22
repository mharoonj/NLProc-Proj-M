import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import uuid

class RAGLogger:
    def __init__(self, log_dir: str = "logs", log_prefix: str = ""):
        """
        Initialize the RAG Logger.
        
        Args:
            log_dir (str): Directory to store log files
            log_prefix (str): Prefix for log files
        """
        self.log_dir = Path(log_dir)
        self.log_prefix = log_prefix
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_log_file(self):
        """Get the current log file path with prefix"""
        timestamp = datetime.now().strftime("%Y%m%d")
        return self.log_dir / f"{self.log_prefix}rag_logs_{timestamp}.jsonl"
        
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
        
        log_file = self._get_log_file()
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')
            
    def get_recent_logs(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get the n most recent log entries.
        
        Args:
            n (int): Number of recent entries to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of recent log entries
        """
        if not self._get_log_file().exists():
            return []
            
        logs = []
        with open(self._get_log_file(), 'r') as f:
            for line in f:
                logs.append(json.loads(line))
                
        return logs[-n:] 