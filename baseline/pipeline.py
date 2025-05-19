from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from baseline.retriever.retriever import Retriever
from baseline.generator.generator import Generator
from utils.logger import RAGLogger

class RAGPipeline:
    def __init__(self, 
                 model_name: str = "google/flan-t5-base",
                 retriever_model: str = 'all-MiniLM-L6-v2',
                 log_dir: str = "logs"):
        """
        Initialize the RAG Pipeline combining retriever and generator.
        
        Args:
            model_name (str): Name of the generator model
            retriever_model (str): Name of the retriever model
            log_dir (str): Directory for storing logs
        """
        self.retriever = Retriever(model_name=retriever_model)
        self.generator = Generator(model_name=model_name, retriever=self.retriever)
        self.logger = RAGLogger(log_dir=log_dir)
        
    def add_documents(self, 
                     documents: Optional[List[str]] = None,
                     directory: Optional[str] = None,
                     glob_pattern: str = "*"):
        """
        Add documents to the retriever.
        
        Args:
            documents (List[str], optional): List of document paths
            directory (str, optional): Directory containing documents
            glob_pattern (str): Pattern for matching files in directory
        """
        if documents:
            for doc in documents:
                self.retriever.add_file(doc)
                
        if directory:
            self.retriever.add_directory(directory, glob_pattern)
            
    def query(self, 
              question: str,
              k: int = 3,
              group_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a question through the RAG pipeline.
        
        Args:
            question (str): The question to answer
            k (int): Number of chunks to retrieve
            group_id (str, optional): Identifier for the query group
            
        Returns:
            Dict containing:
                - answer: Generated answer
                - retrieved_chunks: Retrieved context chunks
                - prompt: Final prompt sent to generator
                - retrieval_scores: Similarity scores for chunks
        """
        # Retrieve relevant chunks
        chunks = self.retriever.query(question, k=k)
        context = "\n".join([chunk['text'] for chunk in chunks])
        
        # Generate answer
        answer = self.generator.generate_answer(question)
        
        # Log the query
        self.logger.log_query(
            question=question,
            retrieved_chunks=[chunk['text'] for chunk in chunks],
            prompt=self.generator.build_prompt(context, question),
            generated_answer=answer,
            retrieval_scores=[chunk['score'] for chunk in chunks],
            group_id=group_id
        )
        
        return {
            "answer": answer,
            "retrieved_chunks": [chunk['text'] for chunk in chunks],
            "prompt": self.generator.build_prompt(context, question),
            "retrieval_scores": [chunk['score'] for chunk in chunks]
        }
        
    def batch_query(self, 
                   questions: List[str],
                   k: int = 3) -> List[Dict[str, Any]]:
        """
        Process multiple questions through the pipeline.
        
        Args:
            questions (List[str]): List of questions to process
            k (int): Number of chunks to retrieve per question
            
        Returns:
            List of results for each question
        """
        results = []
        for question in questions:
            result = self.query(question, k=k)
            results.append(result)
        return results

def main():
    """Example usage of the RAG Pipeline"""
    # Initialize pipeline
    pipeline = RAGPipeline()
    
    # Add documents
    pipeline.add_documents(directory="data")
    
    # Example questions
    questions = [
        "What are the key points about Imran Khan?",
        "What is Imran Khan's background in cricket?",
        "What are Imran Khan's major political achievements?"
    ]
    
    # Process questions
    results = pipeline.batch_query(questions)
    
    # Print results
    for question, result in zip(questions, results):
        print(f"\nQuestion: {question}")
        print(f"Answer: {result['answer']}")
        print("-" * 50)

if __name__ == "__main__":
    main()