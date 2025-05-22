# RAG System with React Frontend

## Installation and Setup

### 1. Install Requirements
```bash
# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Run the FastAPI Backend
```bash
# Navigate to the API directory
cd api

# Start the FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
The API will be available at `http://localhost:8000`

### 3. Start the React Frontend
```bash
# Navigate to the frontend directory
cd frontend/pindi-ui

# Install Node.js dependencies
npm install

# Start the development server
npm start
```
The frontend will be available at `http://localhost:3000`

# Document Retrieval System

This project implements a sophisticated document retrieval system that uses advanced techniques for efficient and accurate information retrieval.

## How the Retriever Works

The retriever component is a sophisticated document search system that uses advanced techniques to find relevant information from your documents. Here's a detailed breakdown of how it works:

### 1. Document Chunking with RecursiveCharacterTextSplitter

We use RecursiveCharacterTextSplitter, a smart text splitting algorithm that:
- Intelligently breaks down documents while preserving semantic meaning
- Uses a hierarchical approach to splitting based on natural text boundaries
- Maintains context by using overlapping chunks

```python
# RecursiveCharacterTextSplitter Configuration
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # Maximum size of each chunk
    chunk_overlap=50,      # Number of characters to overlap between chunks
    separators=[           # Priority order of separators
        "\n\n",           # Double newlines (paragraphs)
        "\n",             # Single newlines
        ".",              # Sentences
        "!",              # Exclamations
        "?",              # Questions
        ",",              # Clauses
        " ",              # Words
        ""                # Characters (as last resort)
    ],
    length_function=len,   # Function to measure chunk size
    is_separator_regex=False
)
```

The splitter works by:
1. First attempting to split on paragraph boundaries (double newlines)
2. If chunks are still too large, splitting on single newlines
3. If still too large, splitting on sentence boundaries (., !, ?)
4. Continuing down the separator list until chunks are the right size
5. Maintaining overlap between chunks to preserve context

### 2. FAISS Indexing and Vector Storage

We use FAISS (Facebook AI Similarity Search) for efficient vector storage and similarity search:
- Converts text chunks into high-dimensional vectors using embeddings
- Uses optimized indexing structures for fast similarity search
- Supports both CPU and GPU acceleration

```python
# FAISS Index Configuration
import faiss

# Create index
index = faiss.IndexFlatL2(768)  # L2 distance metric
# or
index = faiss.IndexIVFFlat(768, 100)  # IVF index for larger datasets

# Adding vectors to the index
embeddings = [generate_embedding(chunk.text) for chunk in chunks]
index.add(embeddings)

# Optional: Training the index for better performance
if index.ntotal > 0:
    index.train(embeddings)
```

FAISS provides several indexing options:
- **IndexFlatL2**: Exact search using L2 distance
- **IndexIVFFlat**: Approximate search using inverted file index
- **IndexIVFPQ**: Product quantization for memory efficiency

### 3. FAISS Search Process

The search process in FAISS is highly optimized:
- Converts query into the same vector space as documents
- Uses efficient similarity metrics (L2, cosine, etc.)
- Returns top-k most similar vectors with their distances

```python
# FAISS Search Process
query_embedding = generate_embedding(query)

# Search for similar vectors
k = 3  # number of results to return
distances, indices = index.search(query_embedding, k)

# Convert distances to similarity scores
similarity_scores = [1 / (1 + d) for d in distances]

# Get results with scores
results = [
    {
        'text': chunks[idx].text,
        'score': similarity_scores[i],
        'metadata': chunks[idx].metadata
    }
    for i, idx in enumerate(indices)
]
```

### 4. Real Example

Here's how the system processed a real query about Imran Khan's cricket career:

**Query:** "When did Imran Khan start his cricket career?"

**Top Result:** "He began his international cricket career in a 1971 Test series against England"

**Score:** 0.6027074749852854

### Implementation Example

```python
# Complete example of using the retriever
from retriever import Retriever

retriever = Retriever(
    documents=your_documents,
    text_splitter=RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    ),
    embedding_model='your-embedding-model',
    index_type='IVFFlat',  # FAISS index type
    index_params={
        'dimension': 768,
        'nlist': 100  # number of clusters for IVF index
    }
)

# Initialize the retriever
retriever.initialize()

# Search for information
results = retriever.search(
    "your query here",
    top_k=3,
    score_threshold=0.5
)
```

## Generator Component

The generator component processes retrieved information and generates accurate answers using advanced language models.

### 1. Data Flow in Generator

The generator processes data through several stages:
1. Receives retrieved chunks and question from retriever
2. Formats context and question into a structured prompt
3. Processes through language model
4. Generates and formats the final answer

```python
# Example of data flow in Generator
{
    "question": "When did Imran Khan start his cricket career?",
    "retrieved_chunks": [
        {
            "text": "He began his international cricket career in a 1971 Test series against England...",
            "score": 0.6027074749852854
        }
    ],
    "prompt": "*Task:* Answer the question using ONLY the provided context...",
    "generated_answer": "1971"
}
```

### 2. Prompt Engineering

The generator uses carefully crafted prompts to ensure accurate answers:
- Clear task instructions
- Context formatting rules
- Answer format specifications

```python
*Task:* Answer the question using ONLY the provided context.
*Rules:*
- MUST include all key details.
- If the answer is not in the context, say "cannot find."
- Organize information clearly.

*Context:*
[Retrieved chunks are inserted here]

*Question:*
[User's question]

*Answer (detailed, in complete sentences):*
```

### 3. Batch Processing

The generator efficiently processes multiple queries using batch processing:

```python
def process_batch(questions, batch_size=8):
    batches = [questions[i:i + batch_size] 
              for i in range(0, len(questions), batch_size)]
    
    results = []
    for batch in batches:
        # Process each batch in parallel
        batch_results = process_questions(batch)
        results.extend(batch_results)
    
    return results
```

### 4. Data Flow Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  User Question  │────▶│    Retriever    │────▶│    Generator    │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                              │                         │
                              │                         │
                              ▼                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │                 │     │                 │
                        │  Retrieved      │     │  Generated      │
                        │  Chunks         │     │  Answer         │
                        │                 │     │                 │
                        └─────────────────┘     └─────────────────┘
```

### 5. Implementation Example

```python
from generator import Generator

generator = Generator(
    model_name='flan-t5-base',
    batch_size=8,
    max_length=512,
    temperature=0.7
)

# Process a single question
answer = generator.generate_answer(
    question="When did Imran Khan start his cricket career?",
    context=retrieved_chunks
)

# Process a batch of questions
answers = generator.generate_answers_batch(
    questions=[
        "When did Imran Khan start his cricket career?",
        "What was his role in the 1992 World Cup?"
    ],
    contexts=retrieved_chunks_list
)
```

## Requirements

- Python 3.8+
- FAISS
- Sentence Transformers (for embeddings)
- LangChain

## Installation

```bash
pip install -r requirements.txt
```

## Usage

1. Initialize the retriever with your documents
2. The system will automatically:
   - Split documents into chunks
   - Generate embeddings
   - Create and train the FAISS index
3. Use the search method to find relevant information

## Performance Considerations

- The chunk size and overlap parameters can be adjusted based on your specific needs
- For larger datasets, consider using IndexIVFFlat or IndexIVFPQ
- GPU acceleration is available for both embedding generation and FAISS operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

