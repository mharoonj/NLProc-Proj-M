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
        """Build a clearer and more structured prompt."""
        # Remove score tags to avoid confusion
        cleaned_context = "\n".join(
        line.split("] ")[1] if "] " in line else line 
        for line in context.split("\n")
    )
    
        prompt = f"""
        **Task:** Answer the question using ONLY the provided context.  
        **Rules:**  
        - **MUST** include all key details.  
        - If the answer is not in the context, say "cannot find."  
        - Organize information clearly.  

        **Context:**  
        {cleaned_context}  

        **Question:**  
        {question}  

        **Answer (detailed, in complete sentences):**  
        """
        return prompt.strip()

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
            if not retrieved_docs:
                return "I cannot find this information in the provided context."
            
            # Combine retrieved chunks with their scores
            context_parts = []
            for doc in retrieved_docs:
                context_parts.append(doc['text'])  # Remove score from context
            context = "\n\n".join(context_parts)
        
        # If still no context, use empty string
        # print("context : ", context)
        if context is None:
            context = ""
            
        # Build the prompt
        prompt = self.build_prompt(context, question)
        
        # Tokenize the input
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024)
        
        # Generate the answer
        outputs = self.model.generate(
            inputs["input_ids"],
              max_length=1024,  # Increased length
                num_beams=4,
                length_penalty=1.5,  # Slightly lower penalty
                early_stopping=True,
                temperature=0.7,  # Higher temperature for more diversity
                do_sample=True,   # Enable sampling
                top_p=0.95,       # Broader nucleus sampling
                top_k=50         # Larger top-k
                )
        
        # Decode and return the answer
        answer = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # print("context answer : ", answer.strip())
        return answer.strip()

def main():
    """Example usage of the Generator with Retriever"""
    # Initialize retriever
    retriever = Retriever()
    
    # Add documents from data directory
    data_dir = project_root / "data"
    retriever.add_directory(data_dir)
    
    # Initialize generator with retriever
    generator = Generator(retriever=retriever)
    
    # Example questions
    questions = [
        "who is Imran Khan?",
        # "When did Imran Khan start his cricket career?",
        # "What are Imran Khan's major achievements?",
        # "What is Imran Khan's educational background?",
        # "In which country did Imran Khan became prime minister and for what time period?",
        # "What are Imran Khan's views on foreign policy?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        answer = generator.generate_answer(question)
        print(f"Answer: {answer}")

if __name__ == "__main__":
    main()