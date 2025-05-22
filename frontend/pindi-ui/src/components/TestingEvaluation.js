import React, { useState, useEffect } from 'react';
import { Typography, Card, Table, Statistic, Row, Col, Progress, Alert, Spin } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

function TestingEvaluation({ isActive }) {
  const [logData, setLogData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [metrics, setMetrics] = useState({
    totalQueries: 0,
    successfulRetrievals: 0,
    averageScore: 0,
    responseTime: 0,
    accuracy: 0,
    matchedAnswers: 0,
    unmatchedAnswers: 0
  });

  useEffect(() => {
    if (isActive) {
      fetchLogData();
    }
  }, [isActive]);

  const fetchLogData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:8000/api/logs');
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch log data');
      }
      
      const data = await response.json();
      
      if (!Array.isArray(data)) {
        throw new Error('Invalid data format received from server');
      }
      
      setLogData(data);
      calculateMetrics(data);
    } catch (error) {
      console.error('Error fetching log data:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const calculateMetrics = (data) => {
    const totalQueries = data.length;
    const successfulRetrievals = data.filter(item => 
      item.retrieved_chunks && item.retrieved_chunks.length > 0
    ).length;
    
    const averageScore = data.reduce((acc, item) => {
      const scores = item.retrieval_scores || [];
      return acc + (scores.length > 0 ? scores[0] : 0);
    }, 0) / totalQueries;

    // Calculate matched and unmatched answers
    const matchedAnswers = data.filter(item => {
      const answer = item.generated_answer?.toLowerCase() || '';
      return answer !== 'cannot find' && answer !== 'can not find' && answer.trim() !== '';
    }).length;

    const unmatchedAnswers = totalQueries - matchedAnswers;

    setMetrics({
      totalQueries,
      successfulRetrievals,
      averageScore: averageScore.toFixed(4),
      responseTime: '0.5s',
      accuracy: ((matchedAnswers / totalQueries) * 100).toFixed(1),
      matchedAnswers,
      unmatchedAnswers
    });
  };

  const columns = [
    {
      title: 'Question',
      dataIndex: 'question',
      key: 'question',
      width: '25%',
    },
    {
      title: 'Retrieved Chunks',
      dataIndex: 'retrieved_chunks',
      key: 'retrieved_chunks',
      width: '35%',
      render: (chunks, record) => (
        <ul style={{ padding: 0, margin: 0 }}>
          {chunks?.map((chunk, index) => (
            <li key={index} style={{ marginBottom: '8px' }}>
              <div>Score: {record.retrieval_scores?.[index]?.toFixed(4) || 'N/A'}</div>
              <div style={{ 
                maxHeight: '100px', 
                overflow: 'auto',
                backgroundColor: '#f5f5f5',
                padding: '8px',
                borderRadius: '4px'
              }}>
                {chunk}
              </div>
            </li>
          ))}
        </ul>
      ),
    },
    {
      title: 'Generated Answer',
      dataIndex: 'generated_answer',
      key: 'generated_answer',
      width: '20%',
    },
    {
      title: 'Evaluation',
      key: 'evaluation',
      width: '20%',
      render: (_, record) => {
        const hasAnswer = record.generated_answer && 
          record.generated_answer.toLowerCase() !== 'cannot find' && 
          record.generated_answer.toLowerCase() !== 'can not find' &&
          record.generated_answer.trim() !== '';
        const hasGoodScore = record.retrieval_scores?.[0] > 0.5;
        
        return (
          <div>
            {hasAnswer && hasGoodScore ? (
              <CheckCircleOutlined style={{ color: 'green', fontSize: '20px' }} />
            ) : (
              <CloseCircleOutlined style={{ color: 'red', fontSize: '20px' }} />
            )}
            <div style={{ marginTop: '8px' }}>
              <Progress 
                percent={Math.round(record.retrieval_scores?.[0] * 100 || 0)} 
                size="small" 
                status={hasGoodScore ? "success" : "exception"}
              />
            </div>
          </div>
        );
      },
    },
  ];

  return (
    <Card>
      <Title level={3}>Testing and Evaluation Results</Title>
      
      {error && (
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: '16px' }}
        />
      )}
      
      {loading ? (
        <div style={{ textAlign: 'center', padding: '50px' }}>
          <Spin size="large" />
          <div style={{ marginTop: '16px' }}>Loading test results...</div>
        </div>
      ) : (
        <>
          <Row gutter={16} style={{ marginBottom: '24px' }}>
            <Col span={4}>
              <Card>
                <Statistic
                  title="Total Test Queries"
                  value={metrics.totalQueries}
                />
              </Card>
            </Col>
            <Col span={4}>
              <Card>
                <Statistic
                  title="Matched Answers"
                  value={metrics.matchedAnswers}
                  valueStyle={{ color: '#3f8600' }}
                />
              </Card>
            </Col>
            <Col span={4}>
              <Card>
                <Statistic
                  title="Unmatched Answers"
                  value={metrics.unmatchedAnswers}
                  valueStyle={{ color: '#cf1322' }}
                />
              </Card>
            </Col>
            <Col span={4}>
              <Card>
                <Statistic
                  title="Average Score"
                  value={metrics.averageScore}
                  precision={4}
                />
              </Card>
            </Col>
            <Col span={4}>
              <Card>
                <Statistic
                  title="Answer Accuracy"
                  value={metrics.accuracy}
                  suffix="%"
                />
              </Card>
            </Col>
            <Col span={4}>
              <Card>
                <Statistic
                  title="Successful Retrievals"
                  value={metrics.successfulRetrievals}
                  suffix={`/ ${metrics.totalQueries}`}
                />
              </Card>
            </Col>
          </Row>

          <Title level={4}>Test Results</Title>
          <Table
            dataSource={logData}
            columns={columns}
            rowKey="timestamp"
            pagination={{ pageSize: 5 }}
            scroll={{ x: true }}
          />

          <Title level={4}>Evaluation Summary</Title>
          <Card style={{ backgroundColor: '#f5f5f5', marginTop: '16px' }}>
            <Paragraph>
              <strong>Retrieval Quality:</strong> The system shows {metrics.averageScore > 0.5 ? 'good' : 'moderate'} retrieval quality with an average score of {metrics.averageScore}. 
              {metrics.averageScore > 0.5 ? ' Most queries return relevant chunks with scores above 0.5.' : ' Some queries may need improvement in retrieval accuracy.'}
            </Paragraph>
            <Paragraph>
              <strong>Response Accuracy:</strong> The system achieves {metrics.accuracy}% accuracy in generating meaningful answers. 
              {metrics.accuracy > 80 ? ' The high accuracy indicates reliable responses.' : ' There is room for improvement in answer generation.'}
            </Paragraph>
            <Paragraph>
              <strong>Answer Matching:</strong> Out of {metrics.totalQueries} test queries, {metrics.matchedAnswers} answers were successfully matched with the context, while {metrics.unmatchedAnswers} queries did not find matching information.
            </Paragraph>
            <Paragraph>
              <strong>Test Coverage:</strong> The test suite includes {metrics.totalQueries} queries covering various aspects of the system's functionality.
            </Paragraph>
          </Card>
        </>
      )}
    </Card>
  );
}

export default TestingEvaluation; 