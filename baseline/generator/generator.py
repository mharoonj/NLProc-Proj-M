from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from typing import Optional, List, Dict
from pathlib import Path
import sys
import os

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from baseline.retriever.retriever import Retriever

class Generator:
    def __init__(self, model_name: str = "google/flan-t5-base", retriever: Optional[Retriever] = None):
        """
        Initialize the Generator with a specific model and optional retriever.
        
        Args:
            model_name (str): Name of the model to use. Defaults to flan-t5-base.
            retriever (Retriever, optional): Retriever instance for context retrieval
        """
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.retriever = retriever
        self.load_model()
        
    def load_model(self):
        """Load the model and tokenizer."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        
    def build_prompt(self, context: str, question: str) -> str:
        """
        Build the prompt by combining context and question.
        
        Args:
            context (str): The context text
            question (str): The question to answer
            
        Returns:
            str: Formatted prompt
        """
        prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"
        return prompt
    
    def generate_answer(self, question: str, context: Optional[str] = None, k: int = 3) -> str:
        """
        Generate an answer for the given question, optionally using retrieved context.
        
        Args:
            question (str): The question to answer
            context (str, optional): Direct context to use. If None, will use retriever
            k (int): Number of context chunks to retrieve if using retriever
            
        Returns:
            str: Generated answer
        """
        # If no direct context provided and retriever is available, use retriever
        if context is None and self.retriever is not None:
            retrieved_docs = self.retriever.query(question, k=k)
            context = "\n".join([doc['text'] for doc in retrieved_docs])
        
        # If still no context, use empty string
        if context is None:
            context = ""
            
        # Build the prompt
        prompt = self.build_prompt(context, question)
        
        # Tokenize the input
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        
        # Generate the answer
        outputs = self.model.generate(
            inputs["input_ids"],
            max_length=128,
            num_beams=4,
            length_penalty=2.0,
            early_stopping=True
        )
        
        # Decode and return the answer
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return answer

def main():
    """Example usage of the Generator with Retriever"""
    # Initialize retriever
    retriever = Retriever()
    
    # Add documents from data directory
    data_dir = project_root / "data"
    retriever.add_directory(data_dir)
    
    # Initialize generator with retriever
    generator = Generator(retriever=retriever)
    
    # Example question
    question = "What are the key points about Imran Khan?"
    answer = generator.generate_answer(question)
    print(f"Question: {question}")
    print(f"Answer: {answer}")

if __name__ == "__main__":
    main()