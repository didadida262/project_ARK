import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { createTask, createTextTask, getTasks } from '../api/tasks';

function Home() {
  const [mode, setMode] = useState('url'); // 'url' or 'text'
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [recentTasks, setRecentTasks] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    loadRecentTasks();
  }, []);

  const loadRecentTasks = async () => {
    try {
      const data = await getTasks(0, 5);
      setRecentTasks(data.tasks || []);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (mode === 'url') {
      if (!url.trim()) return;
    } else {
      if (!content.trim()) return;
    }

    setLoading(true);
    try {
      let task;
      if (mode === 'url') {
        task = await createTask(url);
      } else {
        task = await createTextTask(title || 'Untitled', content);
      }
      navigate(`/tasks/${task.task_id}`);
    } catch (error) {
      alert('创建任务失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-500',
      crawling: 'bg-blue-500',
      translating: 'bg-purple-500',
      generating: 'bg-indigo-500',
      completed: 'bg-green-500',
      failed: 'bg-red-500',
    };
    return colors[status] || 'bg-gray-500';
  };

  return (
    <div className="container mx-auto px-4 py-16">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        <h1 className="text-5xl font-bold text-white text-center mb-4">
          新闻转换平台
        </h1>
        <p className="text-gray-400 text-center mb-8">
          自动翻译并转换为音频
        </p>

        {/* 模式切换 */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex bg-gray-800 rounded-lg p-1 border border-gray-700">
            <button
              type="button"
              onClick={() => setMode('url')}
              className={`px-6 py-2 rounded-md transition-colors ${
                mode === 'url'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              网址模式
            </button>
            <button
              type="button"
              onClick={() => setMode('text')}
              className={`px-6 py-2 rounded-md transition-colors ${
                mode === 'text'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              文本模式
            </button>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="mb-16">
          {mode === 'url' ? (
            <div className="flex gap-4">
              <input
                type="url"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="输入新闻网站URL，例如: https://www.reuters.com"
                className="flex-1 px-6 py-4 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
                disabled={loading}
              />
              <button
                type="submit"
                disabled={loading || !url.trim()}
                className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? '处理中...' : '开始'}
              </button>
            </div>
          ) : (
            <div className="space-y-4">
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="文章标题（可选）"
                className="w-full px-6 py-4 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
                disabled={loading}
              />
              <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="输入文章内容..."
                rows={10}
                className="w-full px-6 py-4 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500 resize-none"
                disabled={loading}
              />
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={loading || !content.trim()}
                  className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {loading ? '处理中...' : '开始处理'}
                </button>
              </div>
            </div>
          )}
        </form>

        {recentTasks.length > 0 && (
          <div>
            <h2 className="text-2xl font-bold text-white mb-6">最近任务</h2>
            <div className="space-y-4">
              {recentTasks.map((task) => (
                <motion.div
                  key={task.task_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  onClick={() => navigate(`/tasks/${task.task_id}`)}
                  className="p-6 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 cursor-pointer transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="text-white font-medium truncate">
                        {task.url === 'text_input' ? '文本输入' : task.url}
                      </p>
                      <p className="text-gray-400 text-sm mt-1">
                        {new Date(task.created_at).toLocaleString()}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)} text-white`}>
                        {task.status}
                      </span>
                      {task.articles_count > 0 && (
                        <span className="text-gray-400 text-sm">
                          {task.articles_count} 篇文章
                        </span>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}

export default Home;

