import React from 'react';
import { Typography, Card, Divider } from 'antd';

const { Title, Paragraph, Text } = Typography;

function GeneratorExplanation() {
  return (
    <Card>
      <Title level={3}>How the Generator Works</Title>
      <Paragraph>
        The generator component processes retrieved information and generates accurate answers using advanced language models. Here's a detailed breakdown of the process:
      </Paragraph>

      <Title level={4}>1. Data Flow in Generator</Title>
      <Paragraph>
        The generator processes data through several stages:
        <ol>
          <li>Receives retrieved chunks and question from retriever</li>
          <li>Formats context and question into a structured prompt</li>
          <li>Processes through language model</li>
          <li>Generates and formats the final answer</li>
        </ol>
      </Paragraph>

      <Card style={{ backgroundColor: '#f5f5f5', marginBottom: 16 }}>
        <pre style={{ margin: 0 }}>
{`// Example of data flow in Generator
{
    "question": "When did Imran Khan start his cricket career?",
    "retrieved_chunks": [
        {
            "text": "He began his international cricket career in a 1971 Test series against England...",
            "score": 0.6027074749852854
        },
        // ... more chunks
    ],
    "prompt": "*Task:* Answer the question using ONLY the provided context...",
    "generated_answer": "1971"
}`}
        </pre>
      </Card>

      <Title level={4}>2. Prompt Engineering</Title>
      <Paragraph>
        The generator uses carefully crafted prompts to ensure accurate answers:
        <ul>
          <li>Clear task instructions</li>
          <li>Context formatting rules</li>
          <li>Answer format specifications</li>
        </ul>
      </Paragraph>
      <Card style={{ backgroundColor: '#f5f5f5', marginBottom: 16 }}>
        <pre style={{ margin: 0 }}>
{`*Task:* Answer the question using ONLY the provided context.
*Rules:*
- MUST include all key details.
- If the answer is not in the context, say "cannot find."
- Organize information clearly.

*Context:*
[Retrieved chunks are inserted here]

*Question:*
[User's question]

*Answer (detailed, in complete sentences):*`}
        </pre>
      </Card>

      <Title level={4}>3. Batch Processing</Title>
      <Paragraph>
        The generator efficiently processes multiple queries using batch processing:
      </Paragraph>
      <Card style={{ backgroundColor: '#f5f5f5', marginBottom: 16 }}>
        <pre style={{ margin: 0 }}>
{`// Batch processing example
def process_batch(questions, batch_size=8):
    batches = [questions[i:i + batch_size] 
              for i in range(0, len(questions), batch_size)]
    
    results = []
    for batch in batches:
        # Process each batch in parallel
        batch_results = process_questions(batch)
        results.extend(batch_results)
    
    return results`}
        </pre>
      </Card>

      <Title level={4}>4. Data Flow Diagram</Title>
      <Card style={{ backgroundColor: '#f5f5f5', marginBottom: 16 }}>
        <pre style={{ margin: 0 }}>
{`
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

`}
        </pre>
      </Card>

      <Title level={4}>5. Real Example</Title>
      <Card style={{ backgroundColor: '#f5f5f5' }}>
        <Paragraph>
          <Text strong>Input Question:</Text> "When did Imran Khan start his cricket career?"
        </Paragraph>
        <Paragraph>
          <Text strong>Retrieved Context:</Text> "He began his international cricket career in a 1971 Test series against England"
        </Paragraph>
        <Paragraph>
          <Text strong>Generated Answer:</Text> "1971"
        </Paragraph>
        <Paragraph>
          <Text strong>Processing Time:</Text> ~0.5 seconds
        </Paragraph>
      </Card>

      <Divider />

      <Title level={4}>Implementation Example</Title>
      <Card style={{ backgroundColor: '#f5f5f5' }}>
        <pre style={{ margin: 0 }}>
{`# Complete example of using the generator
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
        "What was his role in the 1992 World Cup?",
        # ... more questions
    ],
    contexts=retrieved_chunks_list
)`}
        </pre>
      </Card>
    </Card>
  );
}

export default GeneratorExplanation; 