import logo from './logo.svg';
import './App.css';
import QuestionAnswerApp from './components/Presentation';
import RetrieverExplanation from './components/RetrieverExplanation';
import GeneratorExplanation from './components/GeneratorExplanation';
import Problems from './components/Problems';
import TestingEvaluation from './components/TestingEvaluation';
import { Tabs } from 'antd';
import { useState } from 'react';

function App() {
  const [activeTab, setActiveTab] = useState('1');

  const items = [
    {
      key: '1',
      label: 'Demo',
      children: <QuestionAnswerApp />,
    },
    {
      key: '2',
      label: 'Retriever Explanation',
      children: <RetrieverExplanation />,
    },
    {
      key: '3',
      label: 'Generator Explanation',
      children: <GeneratorExplanation />,
    },
    {
      key: '4',
      label: 'Problems & Alternatives',
      children: <Problems />,
    },
    {
      key: '5',
      label: 'Testing & Evaluation',
      children: <TestingEvaluation isActive={activeTab === '5'} />,
    },
  ];

  return (
    <div style={{ padding: '20px' }}>
      <Tabs
        activeKey={activeTab}
        onChange={setActiveTab}
        items={items}
        size="large"
      />
    </div>
  );
}

export default App;
