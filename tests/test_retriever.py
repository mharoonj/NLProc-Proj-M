import pytest
from baseline.retriever.retriever import Retriever
import os

# Test file path - adjust as needed
TEST_PDF_PATH = "../data/ImranKhan.pdf"

def test_pdf_retrieval_with_expected_results():
    """Test PDF file loading and query with expected results"""
    
    # 1. Initialize retriever
    retriever = Retriever(
        model_name='all-MiniLM-L6-v2',
        chunk_size=500,
        chunk_overlap=50
    )
    
    # 2. Add the PDF file
    assert os.path.exists(TEST_PDF_PATH), f"Test PDF not found at {TEST_PDF_PATH}"
    retriever.add_file(TEST_PDF_PATH)
    
    # 3. Verify documents were loaded
    assert len(retriever.documents) == 1
    assert "ImranKhan.pdf" in retriever.documents[0].get('source', '')
    assert len(retriever.chunks) > 1  # Should have multiple chunks
    
    # 4. Query for specific information
    query = "reverse swing"
    results = retriever.query(query, k=3)
    
    # 5. Print actual results (for debugging)
    print(f"\nActual results for query: '{query}'")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Source: {result['metadata'].get('source', 'Unknown')}")
        print(f"Text: {result['text'][:200]}...")
        print("-" * 50)
    
    # 6. Verify expected content in results
    expected_phrases = [
        "reverse swing",
        "Sarfraz Nawaz",
        "Wasim Akram",
        "Waqar Younis"
    ]
    
    found_phrases = 0
    for result in results:
        text = result['text']
        for phrase in expected_phrases:
            if phrase.lower() in text.lower():
                found_phrases += 1
    
    assert found_phrases >= 2, f"Expected at least 2 cricket terms in results, found {found_phrases}"
    
    # 7. Verify metadata and structure
    for result in results:
        assert 'text' in result
        assert 'score' in result
        assert 'metadata' in result
        assert isinstance(result['metadata'], dict)
        assert TEST_PDF_PATH in result['metadata'].get('source', '')