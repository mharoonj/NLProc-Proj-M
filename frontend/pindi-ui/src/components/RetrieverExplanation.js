import React from 'react';
import { Typography, Card, Divider } from 'antd';

const { Title, Paragraph, Text } = Typography;

function RetrieverExplanation() {
  return (
    <Card>
      <Title level={3}>How the Retriever Works</Title>
      <Paragraph>
        The retriever component is a sophisticated document search system that uses advanced techniques to find relevant information from your documents. Here's a detailed breakdown of how it works:
      </Paragraph>

      <Title level={4}>1. Document Chunking with RecursiveCharacterTextSplitter</Title>
      <Paragraph>
        We use RecursiveCharacterTextSplitter, a smart text splitting algorithm that:
        <ul>
          <li>Intelligently breaks down documents while preserving semantic meaning</li>
          <li>Uses a hierarchical approach to splitting based on natural text boundaries</li>
          <li>Maintains context by using overlapping chunks</li>
        </ul>
      </Paragraph>
      <Card style={{ backgroundColor: '#f5f5f5', marginBottom: 16 }}>
        <pre style={{ margin: 0 }}>
{`// RecursiveCharacterTextSplitter Configuration
const textSplitter = new RecursiveCharacterTextSplitter({
    chunk_size: 500,        // Maximum size of each chunk
    chunk_overlap: 50,      // Number of characters to overlap between chunks
    separators: [           // Priority order of separators
        "\\n\\n",          // Double newlines (paragraphs)
        "\\n",             // Single newlines
        ".",               // Sentences
        "!",               // Exclamations
        "?",               // Questions
        ",",               // Clauses
        " ",               // Words
        ""                 // Characters (as last resort)
    ],
    length_function: len,   // Function to measure chunk size
    is_separator_regex: false
});`}
        </pre>
      </Card>
      <Paragraph>
        The splitter works by:
        <ol>
          <li>First attempting to split on paragraph boundaries (double newlines)</li>
          <li>If chunks are still too large, splitting on single newlines</li>
          <li>If still too large, splitting on sentence boundaries (., !, ?)</li>
          <li>Continuing down the separator list until chunks are the right size</li>
          <li>Maintaining overlap between chunks to preserve context</li>
        </ol>
      </Paragraph>

      <Title level={4}>2. FAISS Indexing and Vector Storage</Title>
      <Paragraph>
        We use FAISS (Facebook AI Similarity Search) for efficient vector storage and similarity search:
        <ul>
          <li>Converts text chunks into high-dimensional vectors using embeddings</li>
          <li>Uses optimized indexing structures for fast similarity search</li>
          <li>Supports both CPU and GPU acceleration</li>
        </ul>
      </Paragraph>
      <Card style={{ backgroundColor: '#f5f5f5', marginBottom: 16 }}>
        <pre style={{ margin: 0 }}>
{`// FAISS Index Configuration
const index = faiss.IndexFlatL2(768);  // L2 distance metric
// or
const index = faiss.IndexIVFFlat(768, 100);  // IVF index for larger datasets

// Adding vectors to the index
const embeddings = chunks.map(chunk => generateEmbedding(chunk.text));
index.add(embeddings);

// Optional: Training the index for better performance
if (index.ntotal > 0) {
    index.train(embeddings);
}`}
        </pre>
      </Card>
      <Paragraph>
        FAISS provides several indexing options:
        <ul>
          <li><Text strong>IndexFlatL2:</Text> Exact search using L2 distance</li>
          <li><Text strong>IndexIVFFlat:</Text> Approximate search using inverted file index</li>
          <li><Text strong>IndexIVFPQ:</Text> Product quantization for memory efficiency</li>
        </ul>
      </Paragraph>

      <Title level={4}>3. FAISS Search Process</Title>
      <Paragraph>
        The search process in FAISS is highly optimized:
        <ul>
          <li>Converts query into the same vector space as documents</li>
          <li>Uses efficient similarity metrics (L2, cosine, etc.)</li>
          <li>Returns top-k most similar vectors with their distances</li>
        </ul>
      </Paragraph>
      <Card style={{ backgroundColor: '#f5f5f5', marginBottom: 16 }}>
        <pre style={{ margin: 0 }}>
{`// FAISS Search Process
const queryEmbedding = generateEmbedding(query);

// Search for similar vectors
const k = 3;  // number of results to return
const [distances, indices] = index.search(queryEmbedding, k);

// Convert distances to similarity scores
const similarityScores = distances.map(d => 1 / (1 + d));

// Get results with scores
const results = indices.map((idx, i) => ({
    text: chunks[idx].text,
    score: similarityScores[i],
    metadata: chunks[idx].metadata
}));`}
        </pre>
      </Card>

      <Title level={4}>4. Real Example</Title>
      <Paragraph>
        Here's how the system processed a real query about Imran Khan's cricket career:
      </Paragraph>
      <Card style={{ backgroundColor: '#f5f5f5' }}>
        <Paragraph>
          <Text strong>Query:</Text> "When did Imran Khan start his cricket career?"
        </Paragraph>
        <Paragraph>
          <Text strong>Top Result:</Text> "He began his international cricket career in a 1971 Test series against England"
        </Paragraph>
        <Paragraph>
          <Text strong>Score:</Text> 0.6027074749852854
        </Paragraph>
      </Card>

      <Divider />

      <Title level={4}>Implementation Example</Title>
      <Card style={{ backgroundColor: '#f5f5f5' }}>
        <pre style={{ margin: 0 }}>
{`// Complete example of using the retriever
const retriever = new Retriever({
  documents: yourDocuments,
  textSplitter: new RecursiveCharacterTextSplitter({
    chunk_size: 500,
    chunk_overlap: 50,
    separators: ["\\n\\n", "\\n", ".", "!", "?", ",", " ", ""]
  }),
  embeddingModel: 'your-embedding-model',
  indexType: 'IVFFlat',  // FAISS index type
  indexParams: {
    dimension: 768,
    nlist: 100  // number of clusters for IVF index
  }
});

// Initialize the retriever
await retriever.initialize();

// Search for information
const results = await retriever.search("your query here", {
  topK: 3,
  scoreThreshold: 0.5
});`}
        </pre>
      </Card>
    </Card>
  );
}

export default RetrieverExplanation; 