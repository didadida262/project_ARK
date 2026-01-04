import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import Home from './pages/Home';
import TaskDetail from './pages/TaskDetail';
import ArticleDetail from './pages/ArticleDetail';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/tasks/:taskId" element={<TaskDetail />} />
          <Route path="/articles/:articleId" element={<ArticleDetail />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
