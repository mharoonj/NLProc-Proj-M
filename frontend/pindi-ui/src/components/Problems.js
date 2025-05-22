import React from 'react';
import { Typography, Card, Divider } from 'antd';

const { Title, Paragraph, Text } = Typography;

function Problems() {
  return (
    <Card>
      <Title level={3}>Problems and Alternatives</Title>

      <Title level={4}>1. RecursiveCharacterTextSplitter Issues</Title>
      <Card style={{ backgroundColor: '#f5f5f5', marginBottom: 16 }}>
        <Title level={5}>Problems:</Title>
        <ul>
          <li>May split sentences in the middle, breaking semantic meaning</li>
          <li>Fixed chunk size might not align with natural text boundaries</li>
          <li>Overlap can lead to redundant information</li>
          <li>Doesn't consider semantic coherence</li>
        </ul>

        <Title level={5}>Alternatives:</Title>
        <ul>
          <li>
            <Text strong>Semantic Text Splitter:</Text>
            <ul>
              <li>Uses embeddings to maintain semantic coherence</li>
              <li>More intelligent splitting based on meaning</li>
              <li>Better for maintaining context</li>
            </ul>
          </li>
          <li>
            <Text strong>Markdown Header Text Splitter:</Text>
            <ul>
              <li>Respects document structure</li>
              <li>Better for structured documents</li>
              <li>Maintains hierarchical relationships</li>
            </ul>
          </li>
        </ul>
      </Card>

      <Title level={4}>2. FAISS Search Limitations</Title>
      <Card style={{ backgroundColor: '#f5f5f5', marginBottom: 16 }}>
        <Title level={5}>Problems:</Title>
        <ul>
          <li>Memory intensive for large datasets</li>
          <li>Approximate search can miss relevant results</li>
          <li>Fixed dimensionality requirements</li>
          <li>Limited to vector similarity only</li>
        </ul>

        <Title level={5}>Alternatives:</Title>
        <ul>
          <li>
            <Text strong>Elasticsearch:</Text>
            <ul>
              <li>Full-text search capabilities</li>
              <li>Better for keyword matching</li>
              <li>More flexible querying options</li>
            </ul>
          </li>
          <li>
            <Text strong>Pinecone:</Text>
            <ul>
              <li>Managed vector database</li>
              <li>Better scalability</li>
              <li>Easier deployment and maintenance</li>
            </ul>
          </li>
          <li>
            <Text strong>Weaviate:</Text>
            <ul>
              <li>Combines vector and keyword search</li>
              <li>Better for hybrid search</li>
              <li>More flexible schema</li>
            </ul>
          </li>
        </ul>
      </Card>

      <Title level={4}>3. Flan-T5-Base Model Limitations</Title>
      <Card style={{ backgroundColor: '#f5f5f5', marginBottom: 16 }}>
        <Title level={5}>Problems:</Title>
        <ul>
          <li>Limited context window (512 tokens)</li>
          <li>Can generate hallucinated information</li>
          <li>May struggle with complex reasoning</li>
          <li>Fixed response format</li>
        </ul>

        <Title level={5}>Alternatives:</Title>
        <ul>
          <li>
            <Text strong>GPT-3.5/4:</Text>
            <ul>
              <li>Larger context window</li>
              <li>Better reasoning capabilities</li>
              <li>More flexible response generation</li>
              <li>Higher cost</li>
            </ul>
          </li>
          <li>
            <Text strong>Llama 2:</Text>
            <ul>
              <li>Open source alternative</li>
              <li>Good performance on various tasks</li>
              <li>Customizable and fine-tunable</li>
              <li>Requires more computational resources</li>
            </ul>
          </li>
          <li>
            <Text strong>Mistral:</Text>
            <ul>
              <li>Efficient architecture</li>
              <li>Good performance with smaller size</li>
              <li>Better for resource-constrained environments</li>
            </ul>
          </li>
        </ul>
      </Card>

      <Title level={4}>4. Potential Solutions</Title>
      <Card style={{ backgroundColor: '#f5f5f5' }}>
        <Paragraph>
          To address these limitations, consider:
        </Paragraph>
        <ul>
          <li>
            <Text strong>Hybrid Search:</Text>
            Combine vector search with keyword matching for better results
          </li>
          <li>
            <Text strong>Dynamic Chunking:</Text>
            Use semantic-aware chunking with variable sizes
          </li>
          <li>
            <Text strong>Model Ensemble:</Text>
            Use multiple models for different aspects of the task
          </li>
          <li>
            <Text strong>Post-processing:</Text>
            Add validation and fact-checking steps
          </li>
        </ul>
      </Card>
    </Card>
  );
}

export default Problems; 