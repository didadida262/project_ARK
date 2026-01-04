import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getTask, getTaskArticles } from '../api/tasks';

function TaskDetail() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [task, setTask] = useState(null);
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 3000); // 每3秒刷新一次
    return () => clearInterval(interval);
  }, [taskId]);

  const loadData = async () => {
    try {
      const [taskData, articlesData] = await Promise.all([
        getTask(taskId),
        getTaskArticles(taskId),
      ]);
      setTask(taskData);
      setArticles(articlesData.articles || []);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load data:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-500',
      translating: 'bg-purple-500',
      generating: 'bg-indigo-500',
      completed: 'bg-green-500',
      failed: 'bg-red-500',
    };
    return colors[status] || 'bg-gray-500';
  };

  const getProgress = () => {
    if (!task || task.status === 'pending' || task.status === 'crawling') return 20;
    if (task.status === 'translating') return 50;
    if (task.status === 'generating') return 80;
    if (task.status === 'completed') return 100;
    return 0;
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="text-center text-white">加载中...</div>
      </div>
    );
  }

  if (!task) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="text-center text-white">任务不存在</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-16">
      <Link to="/" className="text-blue-400 hover:text-blue-300 mb-6 inline-block">
        ← 返回首页
      </Link>

      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-white mb-4">任务详情</h1>
        <p className="text-gray-400 mb-4">{task.url}</p>

        <div className="mb-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-white font-medium">进度</span>
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)} text-white`}>
              {task.status}
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${getProgress()}%` }}
            />
          </div>
        </div>

        {task.error_message && (
          <div className="p-4 bg-red-900/50 border border-red-500 rounded-lg text-red-200 mb-4">
            {task.error_message}
          </div>
        )}
      </motion.div>

      <div>
        <h2 className="text-2xl font-bold text-white mb-6">
          文章列表 ({articles.length})
        </h2>
        <div className="space-y-4">
          {articles.map((article) => (
            <motion.div
              key={article.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              onClick={() => navigate(`/articles/${article.id}`)}
              className="p-6 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 cursor-pointer transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-white font-medium mb-2">
                    {article.title_cn || article.title}
                  </h3>
                  {article.title_cn && article.title !== article.title_cn && (
                    <p className="text-gray-400 text-sm mb-2">{article.title}</p>
                  )}
                  <div className="flex items-center gap-4 text-sm text-gray-400">
                    {article.publish_time && (
                      <span>{new Date(article.publish_time).toLocaleString()}</span>
                    )}
                    {article.author && <span>作者: {article.author}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(article.status)} text-white`}>
                    {article.status}
                  </span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>

        {articles.length === 0 && task.status !== 'completed' && (
          <div className="text-center text-gray-400 py-12">
            文章正在爬取中...
          </div>
        )}
      </div>
    </div>
  );
}

export default TaskDetail;

