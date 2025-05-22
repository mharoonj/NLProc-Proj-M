from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import json
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from baseline.pipeline import RAGPipeline
from utils.logger import RAGLogger

app = FastAPI(
    title="RAG System API",
    description="API for retrieving and generating answers using RAG system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize pipeline and logger
pipeline = RAGPipeline(
    model_name="google/flan-t5-base",
    retriever_model='all-MiniLM-L6-v2',
    log_dir=str(project_root / "logs")
)
logger = RAGLogger(project_root / "logs")

# Add data
data_dir = project_root / "data"
pipeline.add_documents(directory=str(data_dir))

class Question(BaseModel):
    question: str

class BatchQuestions(BaseModel):
    questions: List[str]

class ChunkInfo(BaseModel):
    text: str
    score: float

class QueryResponse(BaseModel):
    question: str
    retrieved_chunks: List[ChunkInfo]
    prompt: str
    generated_answer: str
    group_id: str = "Team Pindi"

class BatchResponse(BaseModel):
    results: List[QueryResponse]

@app.post("/query", response_model=QueryResponse)
async def process_question(question: Question):
    """
    Process a single question and return detailed response.
    
    Args:
        question: The question to process
        
    Returns:
        Response containing retrieved chunks, prompt, and generated answer
    """
    try:
        # Process question using pipeline
        result = pipeline.query(question.question)
        
        # Log the query
        logger.log_query(
            question=question.question,
            retrieved_chunks=result['retrieved_chunks'],
            prompt=result['prompt'],
            generated_answer=result['answer'],
            retrieval_scores=result['retrieval_scores'],
            group_id="Team Pindi"
        )
        
        # Prepare response
        chunk_infos = [
            ChunkInfo(text=chunk, score=score)
            for chunk, score in zip(result['retrieved_chunks'], result['retrieval_scores'])
        ]
        
        return QueryResponse(
            question=question.question,
            retrieved_chunks=chunk_infos,
            prompt=result['prompt'],
            generated_answer=result['answer']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch", response_model=BatchResponse)
async def process_batch(questions: BatchQuestions):
    """
    Process multiple questions in batch and return detailed responses.
    
    Args:
        questions: List of questions to process
        
    Returns:
        List of responses containing retrieved chunks, prompts, and generated answers
    """
    try:
        # Process questions using pipeline
        results = pipeline.batch_query(questions.questions)
        
        # Prepare responses
        responses = []
        for question, result in zip(questions.questions, results):
            # Log each query
            logger.log_query(
                question=question,
                retrieved_chunks=result['retrieved_chunks'],
                prompt=result['prompt'],
                generated_answer=result['answer'],
                retrieval_scores=result['retrieval_scores'],
                group_id="Team Pindi"
            )
            
            # Prepare chunk infos
            chunk_infos = [
                ChunkInfo(text=chunk, score=score)
                for chunk, score in zip(result['retrieved_chunks'], result['retrieval_scores'])
            ]
            
            responses.append(QueryResponse(
                question=question,
                retrieved_chunks=chunk_infos,
                prompt=result['prompt'],
                generated_answer=result['answer']
            ))
        
        return BatchResponse(results=responses)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "Welcome to RAG System API",
        "endpoints": {
            "/query": "POST - Process a single question",
            "/batch": "POST - Process multiple questions",
            "/": "GET - This information page"
        }
    }

@app.get("/api/logs")
async def get_logs():
    """
    Get all test log data from rag_logs files.
    
    Returns:
        List of log entries containing questions, retrieved chunks, and generated answers
    """
    try:
        log_data = []
        logs_dir = project_root / "logs"
        
        # Check if logs directory exists
        if not logs_dir.exists():
            print(f"Logs directory not found at: {logs_dir}")
            return []
            
        # Read only test log files
        log_files = [f for f in os.listdir(logs_dir) if f.startswith("test_rag_logs_") and f.endswith(".jsonl")]
        
        if not log_files:
            print(f"No test log files found in: {logs_dir}")
            return []
            
        for filename in log_files:
            try:
                file_path = logs_dir / filename
                print(f"Reading test log file: {file_path}")
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, 1):
                        if line.strip():
                            try:
                                log_entry = json.loads(line)
                                log_data.append(log_entry)
                            except json.JSONDecodeError as e:
                                print(f"Error parsing JSON in {filename} at line {line_num}: {e}")
                                continue
            except Exception as e:
                print(f"Error reading file {filename}: {e}")
                continue
        
        print(f"Successfully loaded {len(log_data)} test log entries")
        return log_data
        
    except Exception as e:
        print(f"Error in get_logs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error reading test log files: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 



# curl -X POST "http://localhost:8000/query" \
#      -H "Content-Type: application/json" \
#      -d '{"question": "When did Imran Khan start his cricket career?"}'