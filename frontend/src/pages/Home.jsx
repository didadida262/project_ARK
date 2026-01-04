import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { createTask, getTasks, deleteAllTasks, getTaskArticles, downloadOriginal, downloadTranslated } from '../api/tasks';

function Home() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [recentTasks, setRecentTasks] = useState([]);
  const [tasksWithArticles, setTasksWithArticles] = useState([]);
  const [clearing, setClearing] = useState(false);
  const [downloading, setDownloading] = useState({});
  const navigate = useNavigate();

  useEffect(() => {
    loadRecentTasks();
  }, []);

  const loadRecentTasks = async () => {
    try {
      const data = await getTasks(0, 5);
      const tasks = data.tasks || [];
      setRecentTasks(tasks);
      
      // 为每个任务加载文章信息
      const tasksWithArticlesData = await Promise.all(
        tasks.map(async (task) => {
          try {
            const articlesData = await getTaskArticles(task.task_id);
            const articles = articlesData.articles || [];
            return {
              ...task,
              articles: articles
            };
          } catch (error) {
            console.error(`Failed to load articles for task ${task.task_id}:`, error);
            return {
              ...task,
              articles: []
            };
          }
        })
      );
      setTasksWithArticles(tasksWithArticlesData);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!content.trim()) return;

    setLoading(true);
    try {
      const task = await createTask(title, content);
      navigate(`/tasks/${task.task_id}`);
    } catch (error) {
      alert('创建任务失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('确定要清空所有任务和文章吗？此操作不可恢复！')) {
      return;
    }
    
    setClearing(true);
    try {
      await deleteAllTasks();
      setRecentTasks([]);
      setTasksWithArticles([]);
      alert('所有记录已清空');
    } catch (error) {
      alert('清空失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setClearing(false);
    }
  };

  const handleDownload = async (taskId, articleId, type) => {
    const key = `${taskId}-${articleId}-${type}`;
    setDownloading({ ...downloading, [key]: true });
    try {
      let blob;
      let filename;

      if (type === 'original') {
        blob = await downloadOriginal(articleId);
        // 获取文章信息以生成文件名
        const articlesData = await getTaskArticles(taskId);
        const article = articlesData.articles?.find(a => a.id === articleId);
        filename = `${article?.title || 'article'}_original.txt`;
      } else if (type === 'translated') {
        blob = await downloadTranslated(articleId);
        const articlesData = await getTaskArticles(taskId);
        const article = articlesData.articles?.find(a => a.id === articleId);
        filename = `${article?.title_cn || article?.title || 'article'}_translated.txt`;
      }

      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      alert('下载失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setDownloading({ ...downloading, [key]: false });
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
        <p className="text-gray-400 text-center mb-12">
          输入文章内容，自动翻译成中文
        </p>

        <form onSubmit={handleSubmit} className="mb-16">
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
              rows={12}
              className="w-full px-6 py-4 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500 resize-none"
              disabled={loading}
            />
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={loading || !content.trim()}
                className="px-8 py-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? '处理中...' : '开始翻译'}
              </button>
            </div>
          </div>
        </form>

        {tasksWithArticles.length > 0 && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">最近任务</h2>
              <button
                onClick={handleClearAll}
                disabled={clearing}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors text-sm"
              >
                {clearing ? '清空中...' : '一键清空'}
              </button>
            </div>
            <div className="space-y-4">
              {tasksWithArticles.map((task) => {
                const article = task.articles && task.articles.length > 0 ? task.articles[0] : null;
                const displayTitle = article?.title_cn || article?.title || (task.url === 'text_input' ? '文本输入' : task.url);
                
                return (
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
                        {displayTitle}
                      </p>
                      <div className="flex items-center gap-3 text-gray-400 text-sm mt-1">
                        <span>{new Date(task.created_at).toLocaleString()}</span>
                        {article?.translation_started_at && article?.translation_completed_at && (
                          <span className="text-blue-400">
                            翻译耗时: {Math.round((new Date(article.translation_completed_at) - new Date(article.translation_started_at)) / 1000)}秒
                          </span>
                        )}
                      </div>
                    </div>
                      <div className="flex items-center gap-3">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)} text-white`}>
                          {task.status}
                        </span>
                        {article && (
                          <div className="flex items-center gap-2">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDownload(task.task_id, article.id, 'original');
                              }}
                              disabled={downloading[`${task.task_id}-${article.id}-original`]}
                              className="px-3 py-1.5 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                            >
                              {downloading[`${task.task_id}-${article.id}-original`] ? '下载中...' : '下载原文'}
                            </button>
                            {article.content_cn && (
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleDownload(task.task_id, article.id, 'translated');
                                }}
                                disabled={downloading[`${task.task_id}-${article.id}-translated`]}
                                className="px-3 py-1.5 bg-green-600 text-white rounded text-xs hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              >
                                {downloading[`${task.task_id}-${article.id}-translated`] ? '下载中...' : '下载译文'}
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}

export default Home;

