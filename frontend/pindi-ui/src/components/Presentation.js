import React, { useState } from 'react';
import { 
  Card, 
  Input, 
  Button, 
  Space, 
  Spin, 
  Typography, 
  Divider,
  Row,
  Col,
  Progress,
  message
} from 'antd';
import { SearchOutlined, ClearOutlined, LoadingOutlined } from '@ant-design/icons';

const { Text, Title } = Typography;

const QuestionAnswerApp = () => {
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [answer, setAnswer] = useState(null);

  const handleSearch = async () => {
    if (!question.trim()) {
      message.warning('Please enter a question');
      return;
    }

    setLoading(true);
    setResults(null);
    setAnswer(null);

    try {
      // Simulate API call
      const response = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question.trim() }),
      });

      const data = await response.json();
      setResults(data.retrieved_chunks || data.retrieved_chunks); // Handle potential typo in API response
      setAnswer(data.generated_answer);
    } catch (error) {
      message.error('Failed to get answer. Please try again.');
      console.error('API Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setQuestion('');
    setResults(null);
    setAnswer(null);
  };

  const formatScore = (score) => {
    return Math.round(score * 100);
  };

  return (
    <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '24px' }}>
      <Title level={2} style={{ textAlign: 'center', marginBottom: '32px' }}>
        Question Answering System
      </Title>
      
      <Card bordered={false} style={{ boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <Space.Compact style={{ width: '100%' }}>
          <Input
            placeholder="Enter your question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onPressEnter={handleSearch}
            size="large"
            disabled={loading}
          />
          <Button 
            onClick={handleClear} 
            icon={<ClearOutlined />} 
            size="large"
            disabled={loading}
          >
            Clear
          </Button>
          <Button 
            type="primary" 
            onClick={handleSearch} 
            icon={loading ? <LoadingOutlined /> : <SearchOutlined />} 
            size="large"
            loading={loading}
          >
            Search
          </Button>
        </Space.Compact>
      </Card>

      {loading && (
        <div style={{ textAlign: 'center', margin: '40px 0' }}>
          <Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />
          <Text style={{ display: 'block', marginTop: '16px' }}>Searching for answers...</Text>
        </div>
      )}

      {results && (
        <div style={{ marginTop: '32px' }}>
          <Title level={4}>Relevant Information Chunks</Title>
          <Divider />
          <Row gutter={[16, 16]}>
            {results.map((chunk, index) => (
              <Col key={index} xs={24} sm={12} lg={8}>
                <Card 
                  title={`Chunk ${index + 1}`} 
                  bordered={false}
                  hoverable
                  style={{ height: '100%', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
                  headStyle={{ borderBottom: 0 }}
                >
                  <div style={{ marginBottom: '16px' }}>
                    <Text strong>Relevance Score:</Text>
                    <Progress 
                      percent={formatScore(chunk.score)} 
                      status="active" 
                      showInfo={false}
                      strokeColor={{
                        '0%': '#108ee9',
                        '100%': '#87d068',
                      }}
                    />
                    <Text>{formatScore(chunk.score)}%</Text>
                  </div>
                  <Text>{chunk.text}</Text>
                </Card>
              </Col>
            ))}
          </Row>
        </div>
      )}

      {answer && (
        <div style={{ marginTop: '32px' }}>
          <Title level={4}>Generated Answer</Title>
          <Divider />
          <Card
            bordered={false}
            style={{ 
              backgroundColor: '#f6ffed',
              borderLeft: '4px solid #52c41a',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
            }}
          >
            <Title level={5} style={{ color: '#52c41a' }}>Answer:</Title>
            <Text style={{ fontSize: '16px' }}>{answer}</Text>
          </Card>
        </div>
      )}
    </div>
  );
};

export default QuestionAnswerApp;