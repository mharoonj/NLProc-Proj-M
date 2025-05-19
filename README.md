# RAG (Retrieval-Augmented Generation) System

This project implements a Retrieval-Augmented Generation (RAG) system that combines document retrieval with language model generation to provide accurate, context-aware answers to questions.

## System Architecture

### Components

1. **Retriever** (`baseline/retriever/retriever.py`)
   - Purpose: Retrieves relevant document chunks based on user queries
   - Key Features:
     - Uses SentenceTransformer for semantic search
     - Implements FAISS for efficient similarity search
     - Supports multiple document formats (PDF, TXT, MD)
     - Handles document chunking with overlap
   - Input: User question
   - Output: Relevant document chunks with similarity scores

2. **Generator** (`baseline/generator/generator.py`)
   - Purpose: Generates answers using retrieved context
   - Key Features:
     - Uses flan-t5-base model for text generation
     - Implements prompt engineering
     - Handles token limits and truncation
   - Input: Retrieved chunks and user question
   - Output: Generated answer

3. **Logger** (`utils/logger.py`)
   - Purpose: Tracks and logs all RAG operations
   - Key Features:
     - Logs queries, retrieved chunks, prompts, and answers
     - Stores timestamps and unique identifiers
     - Maintains retrieval scores and chunk IDs
   - Output: JSONL log files

4. **Testing Framework** (`tests/`)
   - Purpose: Validates system components and integration
   - Components:
     - `test_generator.py`: Unit and integration tests
     - `test_inputs.json`: Test cases with expected answers
   - Features:
     - Tests initialization
     - Validates retrieval
     - Checks answer generation
     - Verifies answer grounding
     - Ensures consistency

## Data Flow

1. **Document Processing**
   ```
   Raw Documents → Chunking → Embedding → FAISS Index
   ```
   - Documents are split into chunks
   - Chunks are embedded using SentenceTransformer
   - Embeddings are stored in FAISS index

2. **Query Processing**
   ```
   User Question → Retriever → Retrieved Chunks → Generator → Answer
   ```
   - Question is processed by retriever
   - Relevant chunks are retrieved
   - Chunks and question are formatted into prompt
   - Generator produces answer

3. **Logging Flow**
   ```
   Query → Logging → JSONL File
   ```
   - All operations are logged
   - Logs include metadata and scores
   - Stored in daily JSONL files

## Testing and Validation

### Test Types

1. **Unit Tests**
   - Generator initialization
   - Model loading
   - Tokenizer functionality

2. **Integration Tests**
   - Retrieval functionality
   - Answer generation
   - Context grounding

3. **Validation Tests**
   - Answer consistency
   - Expected content verification
   - Context relevance

### Running Tests

```bash
# Run all tests
pytest tests/test_generator.py

# Run specific test
pytest tests/test_generator.py::TestGenerator::test_answer_grounding

# Run test suite with logging
python tests/test_generator.py
```

## Project Structure

```
.
├── baseline/
│   ├── generator/
│   │   └── generator.py
│   └── retriever/
│       └── retriever.py
├── data/
│   └── documents/
├── logs/
│   └── rag_logs_YYYYMMDD.jsonl
├── tests/
│   ├── test_generator.py
│   └── test_inputs.json
└── utils/
    └── logger.py
```

## Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- transformers
- torch
- sentence-transformers
- faiss-cpu
- langchain
- PyPDF2
- pytest

## Usage Example

```python
from baseline.generator.generator import Generator
from baseline.retriever.retriever import Retriever

# Initialize components
retriever = Retriever()
generator = Generator(retriever=retriever)

# Add documents
retriever.add_directory("data")

# Generate answer
answer = generator.generate_answer("What are the key points about Imran Khan?")
```

## Logging Format

```json
{
    "question": "What are the key points about Imran Khan?",
    "retrieved_chunks": ["chunk1", "chunk2", "chunk3"],
    "prompt": "Context: ...\nQuestion: ...\nAnswer:",
    "generated_answer": "The answer...",
    "timestamp": "2024-03-15T10:32:00",
    "group_id": "uuid",
    "retrieval_scores": [0.8, 0.7, 0.6],
    "chunk_ids": ["id1", "id2", "id3"]
}
```

## Why This Architecture?

1. **Modularity**
   - Separate retriever and generator for flexibility
   - Easy to swap components (e.g., different models)

2. **Traceability**
   - Comprehensive logging for debugging
   - Performance monitoring
   - Quality assessment

3. **Quality Control**
   - Automated testing
   - Answer grounding verification
   - Consistency checks

4. **Scalability**
   - Efficient document processing
   - FAISS for fast retrieval
   - Modular design for easy extension
