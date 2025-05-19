import json
import pytest
from pathlib import Path
import sys
from typing import List, Dict, Any
from datetime import datetime
import uuid

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from baseline.generator.generator import Generator
from baseline.retriever.retriever import Retriever
from utils.logger import RAGLogger

class TestGenerator:
    @pytest.fixture
    def setup(self):
        """Setup test environment with retriever and generator"""
        self.retriever = Retriever()
        self.generator = Generator(retriever=self.retriever)
        self.logger = RAGLogger(log_dir="logs")
        
        # Load test data
        data_dir = project_root / "data"
        self.retriever.add_directory(data_dir)
        
        # Load test cases
        test_file = project_root / "tests" / "test_inputs.json"
        if test_file.exists():
            with open(test_file, 'r') as f:
                self.test_cases = json.load(f)
        else:
            self.test_cases = []
            
    def test_generator_initialization(self, setup):
        """Test if generator initializes correctly"""
        assert self.generator is not None
        assert self.generator.model is not None
        assert self.generator.tokenizer is not None
        
    def test_retrieval(self, setup):
        """Test if retriever returns relevant chunks"""
        question = "What are the key points about Imran Khan?"
        chunks = self.retriever.query(question, k=3)
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('score' in chunk for chunk in chunks)
        
    def test_answer_generation(self, setup):
        """Test if generator produces non-empty answers"""
        for test_case in self.test_cases:
            answer = self.generator.generate_answer(test_case["question"])
            assert answer is not None
            assert len(answer) > 0
            assert isinstance(answer, str)
            
    def test_answer_grounding(self, setup):
        """Test if answers are grounded in retrieved context"""
        for test_case in self.test_cases:
            question = test_case["question"]
            
            # Get retrieved chunks
            chunks = self.retriever.query(question, k=3)
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
                group_id=str(uuid.uuid4())
            )
            
            # Basic grounding check - answer should contain some words from context
            context_words = set(context.lower().split())
            answer_words = set(answer.lower().split())
            common_words = context_words.intersection(answer_words)
            
            assert len(common_words) > 0, f"Answer should contain words from the context for question: {question}"
            
    def test_consistency(self, setup):
        """Test if same question produces consistent results"""
        for test_case in self.test_cases:
            question = test_case["question"]
            
            # Generate two answers
            answer1 = self.generator.generate_answer(question)
            answer2 = self.generator.generate_answer(question)
            
            # Answers should be similar in length and content
            assert abs(len(answer1) - len(answer2)) < 50, f"Answers should be similar in length for question: {question}"
            
            # Check for expected content
            for expected in test_case["expected_answer_contains"]:
                assert expected.lower() in answer1.lower() or expected.lower() in answer2.lower(), \
                    f"Expected content '{expected}' not found in answers for question: {question}"
        
    def run_test_suite(self, setup):
        """Run all test cases from test_inputs.json"""
        results = []
        
        for test_case in self.test_cases:
            question = test_case["question"]
            expected_terms = test_case["expected_answer_contains"]
            
            # Generate answer
            answer = self.generator.generate_answer(question)
            
            # Get retrieved chunks
            chunks = self.retriever.query(question, k=3)
            context = "\n".join([chunk['text'] for chunk in chunks])
            
            # Check if answer contains expected content
            contains_expected = all(
                term.lower() in answer.lower() 
                for term in expected_terms
            )
            
            # Log the query
            self.logger.log_query(
                question=question,
                retrieved_chunks=[chunk['text'] for chunk in chunks],
                prompt=self.generator.build_prompt(context, question),
                generated_answer=answer,
                retrieval_scores=[chunk['score'] for chunk in chunks],
                group_id=str(uuid.uuid4())
            )
            
            results.append({
                "question": question,
                "expected_terms": expected_terms,
                "answer": answer,
                "contains_expected": contains_expected,
                "description": test_case["description"]
            })
            
        return results

def main():
    """Run the test suite and print results"""
    test = TestGenerator()
    test.setup()
    results = test.run_test_suite(test.setup())
    
    print("\nTest Results:")
    print("-" * 50)
    for result in results:
        print(f"\nQuestion: {result['question']}")
        print(f"Description: {result['description']}")
        print(f"Expected terms: {', '.join(result['expected_terms'])}")
        print(f"Generated answer: {result['answer']}")
        print(f"Test passed: {result['contains_expected']}")
        print("-" * 50)

if __name__ == "__main__":
    main() 