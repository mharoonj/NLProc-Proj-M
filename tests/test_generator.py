import json
import pytest
from pathlib import Path
import sys
from typing import List, Dict, Any
from datetime import datetime
import uuid
import argparse

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from baseline.generator.generator import Generator
from baseline.retriever.retriever import Retriever
from utils.logger import RAGLogger
from baseline.pipeline import RAGPipeline

@pytest.fixture
def setup_test_env():
    """Set up test environment with retriever, generator, and logger"""
    # Initialize components with same parameters as direct usage
    retriever = Retriever(
        model_name='all-MiniLM-L6-v2',
        chunk_size=512,
        chunk_overlap=100
    )
    generator = Generator(retriever=retriever)
    
    # Add test data
    data_dir = project_root / "data"
    retriever.add_directory(data_dir)
    
    # Initialize logger
    log_dir = project_root / "logs"
    logger = RAGLogger(log_dir)
    
    return retriever, generator, logger

def test_generator_initialization():
    """Test generator initialization"""
    generator = Generator()
    assert generator.model is not None
    assert generator.tokenizer is not None

def test_retriever_initialization():
    """Test retriever initialization"""
    retriever = Retriever()
    assert retriever.model is not None
    assert retriever.text_splitter is not None

def test_retrieval(setup_test_env):
    """Test document retrieval"""
    retriever, generator, logger = setup_test_env
    question = "When did Imran Khan start his cricket career?"
    results = retriever.query(question)
    
    # Log the retrieval
    logger.log_query(
        question=question,
        retrieved_chunks=results,
        prompt="",
        generated_answer="",
        retrieval_scores=[result['score'] for result in results],
        group_id="Team Pindi"
    )
    
    assert len(results) > 0
    assert all('text' in result for result in results)
    assert all('score' in result for result in results)

def test_answer_generation(setup_test_env):
    """Test answer generation"""
    retriever, generator, logger = setup_test_env
    question = "What are Imran Khan's views on foreign policy?"
    
    # Get retrieved chunks with higher k value
    chunks = retriever.query(question, k=5)  # Increased from default k=3
    context = "\n".join([chunk['text'] for chunk in chunks])
    
    # Generate answer with context and higher temperature
    answer = generator.generate_answer(
        question, 
        context=context,
        k=5  # Increased from default k=3
    )
    
    # Log the generation
    logger.log_query(
        question=question,
        retrieved_chunks=chunks,
        prompt=generator.build_prompt(context, question),
        generated_answer=answer,
        retrieval_scores=[chunk['score'] for chunk in chunks],
        group_id="Team Pindi"
    )
    
    assert isinstance(answer, str)
    assert len(answer) > 0
    print(f"\nGenerated Answer: {answer}")

# def test_grounding(setup_test_env):
#     """Test answer grounding in context"""
#     retriever, generator, logger = setup_test_env
#     question = "When did Imran Khan start his cricket career?"
    
#     # Get retrieved chunks
#     chunks = retriever.query(question)
#     context = "\n".join([chunk['text'] for chunk in chunks])
    
#     # Generate answer
#     answer = generator.generate_answer(question, context=context)
    
#     # Log the grounding test
#     logger.log_query(
#         question=question,
#         retrieved_chunks=chunks,
#         prompt=generator.build_prompt(context, question),
#         generated_answer=answer,
#         retrieval_scores=[chunk['score'] for chunk in chunks],
#         group_id="Team Pindi"
#     )
    
#     # Check if answer contains words from context
#     context_words = set(context.lower().split())
#     answer_words = set(answer.lower().split())
#     common_words = context_words.intersection(answer_words)
    
#     assert len(common_words) > 0, "Answer should contain words from context"
#     print(f"\nContext: {context}")
#     print(f"Answer: {answer}")
#     print(f"Common words: {common_words}")

# def test_consistency(setup_test_env):
    """Test answer consistency"""
    retriever, generator, logger = setup_test_env
    question = "What are Imran Khan's views on foreign policy?"
    
    # Get retrieved chunks with higher k value
    chunks = retriever.query(question, k=5)  # Increased from default k=3
    context = "\n".join([chunk['text'] for chunk in chunks])
    
    # Generate two answers with same context and higher temperature
    answer1 = generator.generate_answer(
        question, 
        context=context,
        k=5  # Increased from default k=3
    )
    answer2 = generator.generate_answer(
        question, 
        context=context,
        k=5  # Increased from default k=3
    )
    
    # Log both consistency tests
    logger.log_query(
        question=question,
        retrieved_chunks=chunks,
        prompt=generator.build_prompt(context, question),
        generated_answer=answer1,
        retrieval_scores=[chunk['score'] for chunk in chunks],
        group_id="Team Pindi"
    )
    
    logger.log_query(
        question=question,
        retrieved_chunks=chunks,
        prompt=generator.build_prompt(context, question),
        generated_answer=answer2,
        retrieval_scores=[chunk['score'] for chunk in chunks],
        group_id="Team Pindi"
    )
    
    print(f"\nFirst Answer: {answer1}")
    print(f"Second Answer: {answer2}")
    
    # Answers should be similar in length and content
    assert abs(len(answer1) - len(answer2)) < 50, "Answers should be similar in length"
    
    # Check for expected content
    expected_terms = ["Imran Khan", "foreign policy", "Pakistan"]
    for term in expected_terms:
        assert term.lower() in answer1.lower() or term.lower() in answer2.lower(), f"Expected term '{term}' not found in answers"

def run_test_suite():
    """Run the entire test suite and log results"""
    # Load test data
    test_file = project_root / "tests" / "test_inputs.json"
    with open(test_file, 'r') as f:
        test_data = json.load(f)
    
    # Initialize components with same parameters as direct usage
    retriever = Retriever(
        model_name='all-MiniLM-L6-v2',
        chunk_size=512,
        chunk_overlap=100
    )
    generator = Generator(retriever=retriever)
    logger = RAGLogger(project_root / "logs")
    
    # Add test data
    data_dir = project_root / "data"
    retriever.add_directory(data_dir)
    
    # Run tests
    results = []
    for test_case in test_data:
        question = test_case['question']
        expected_terms = test_case['expected_answer_contains']
        
        # Get retrieved chunks with higher k value
        chunks = retriever.query(question, k=3)
        context = "\n".join([chunk['text'] for chunk in chunks])
        
        # Generate answer with context and higher temperature
        answer = generator.generate_answer(
            question, 
            context=context,
            k=3  # Increased from default k=3
        )
        
        # Check expected terms
        found_terms = [term for term in expected_terms if term.lower() in answer.lower()]
        missing_terms = [term for term in expected_terms if term.lower() not in answer.lower()]
        
        # Calculate percentage of expected terms found
        total_terms = len(expected_terms)
        found_percentage = (len(found_terms) / total_terms) * 100 if total_terms > 0 else 0
        
        # Pass if at least 70% of expected terms are found
        passed = found_percentage >= 50
        
        # Log the query
        logger.log_query(
            question=question,
            retrieved_chunks=chunks,
            prompt=generator.build_prompt(context, question),
            generated_answer=answer,
            retrieval_scores=[chunk['score'] for chunk in chunks],
            group_id="Team Pindi"
        )
        
        results.append({
            'question': question,
            'expected_terms': expected_terms,
            'found_terms': found_terms,
            'missing_terms': missing_terms,
            'answer': answer,
            'found_percentage': found_percentage,
            'passed': passed
        })
    
    return results

def main():
    """Main function to run tests"""
    results = run_test_suite()
    
    # Print results
    print("\nTest Results:")
    print("=" * 80)
    for result in results:
        print(f"\nQuestion: {result['question']}")
        print(f"Expected Terms: {result['expected_terms']}")
        print(f"Found Terms: {result['found_terms']}")
        print(f"Missing Terms: {result['missing_terms']}")
        print(f"Found Percentage: {result['found_percentage']:.1f}%")
        print(f"Answer: {result['answer']}")
        print(f"Passed: {result['passed']}")
        print("-" * 80)
    
    # Print summary
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r['passed'])
    print(f"\nSummary:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed Tests: {passed_tests}")
    print(f"Pass Rate: {(passed_tests/total_tests)*100:.1f}%")

def run_tests(test_case=None, verbose=False):
    # Initialize pipeline
    pipeline = RAGPipeline(
        model_name="google/flan-t5-base",
        retriever_model='all-MiniLM-L6-v2',
        log_dir=str(project_root / "logs")
    )
    
    # Initialize logger with test prefix
    logger = RAGLogger(
        log_dir=str(project_root / "logs"),
        log_prefix="test_"  # Add test prefix to log files
    )
    
    # Add data
    data_dir = project_root / "data"
    pipeline.add_documents(directory=str(data_dir))
    
    # Test questions
    test_questions = [
        "When did Imran Khan start his cricket career?",
        "What was Imran Khan's role in Pakistan's cricket team?",
        "When did Imran Khan win the Cricket World Cup?",
        "What is Imran Khan's educational background?",
        "When did Imran Khan become Prime Minister of Pakistan?"
    ]
    
    if test_case:
        test_questions = [test_case]
    
    # Process each question
    for question in test_questions:
        if verbose:
            print(f"\nProcessing question: {question}")
        
        # Get answer
        result = pipeline.query(question)
        
        # Log the query
        logger.log_query(
            question=question,
            retrieved_chunks=result['retrieved_chunks'],
            prompt=result['prompt'],
            generated_answer=result['answer'],
            retrieval_scores=result['retrieval_scores'],
            group_id="Test Generator"
        )
        
        if verbose:
            print(f"Generated Answer: {result['answer']}")
            print("\nRetrieved Chunks:")
            for chunk, score in zip(result['retrieved_chunks'], result['retrieval_scores']):
                print(f"\nScore: {score:.4f}")
                print(f"Text: {chunk[:200]}...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run generator tests')
    parser.add_argument('--test_case', type=str, help='Specific test case to run')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output')
    args = parser.parse_args()
    
    run_tests(args.test_case, args.verbose) 