import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { createTask, getTasks, deleteAllTasks, getTaskArticles, downloadOriginal, downloadTranslated, generateAudio, downloadAudio } from '../api/tasks';

function Home() {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [recentTasks, setRecentTasks] = useState([]);
  const [tasksWithArticles, setTasksWithArticles] = useState([]);
  const [clearing, setClearing] = useState(false);
  const [downloading, setDownloading] = useState({});
  const [generatingAudio, setGeneratingAudio] = useState({});
  const [hoverMenu, setHoverMenu] = useState({}); // { 'type-taskId-articleId': true/false }
  const navigate = useNavigate();

  useEffect(() => {
    loadRecentTasks();
    // 如果有正在生成音频的任务，每2秒刷新一次
    const interval = setInterval(() => {
      const hasGenerating = tasksWithArticles.some(task => {
        const article = task.articles?.[0];
        return article && article.status === 'generating';
      });
      if (hasGenerating) {
        loadRecentTasks();
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [tasksWithArticles.length]);

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
    setHoverMenu({}); // 关闭菜单
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
      } else if (type === 'audio' || type === 'audio_original') {
        const audioType = type === 'audio_original' ? 'original' : 'translated';
        blob = await downloadAudio(articleId, audioType);
        const articlesData = await getTaskArticles(taskId);
        const article = articlesData.articles?.find(a => a.id === articleId);
        const title = audioType === 'original' 
          ? (article?.title || 'article')
          : (article?.title_cn || article?.title || 'article');
        const suffix = audioType === 'original' ? '_original' : '';
        filename = `${title}${suffix}.mp3`;
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

  const handleGenerateAudio = async (taskId, articleId, textType = 'translated') => {
    const key = `${taskId}-${articleId}-${textType}`;
    setGeneratingAudio({ ...generatingAudio, [key]: true });
    setHoverMenu({}); // 关闭菜单
    try {
      await generateAudio(articleId, textType);
      // 刷新任务列表以更新状态
      loadRecentTasks();
    } catch (error) {
      alert('生成音频失败: ' + (error.response?.data?.detail || error.message));
      setGeneratingAudio({ ...generatingAudio, [key]: false });
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
          文章翻译平台
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
                const hasAudio = article?.audio_path || article?.audio_path_original;
                
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
                        {article && article.status === 'generating' && (
                          <div className="mt-2">
                            <div className="flex items-center justify-between mb-1">
                              <span className="text-purple-400 text-xs">音频生成进度</span>
                              <span className="text-purple-400 text-xs">{article.translation_progress || 0}%</span>
                            </div>
                            <div className="w-full bg-gray-700 rounded-full h-1.5">
                              <div
                                className="bg-purple-600 h-1.5 rounded-full transition-all duration-300"
                                style={{ width: `${article.translation_progress || 0}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                      <div className="flex items-center gap-3">
                        <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(task.status)} text-white`}>
                          {task.status}
                        </span>
                        {article && (
                          <div className="flex items-center gap-2">
                            {/* 下载按钮 - 合并为hover菜单，修复hover问题 */}
                            <div 
                              className="relative"
                              onMouseEnter={() => setHoverMenu({ ...hoverMenu, [`download-${task.task_id}-${article.id}`]: true })}
                              onMouseLeave={() => {
                                // 延迟关闭，给用户时间移动到菜单
                                setTimeout(() => {
                                  setHoverMenu(prev => {
                                    const key = `download-${task.task_id}-${article.id}`;
                                    // 检查鼠标是否还在菜单区域
                                    const menuElement = document.querySelector(`[data-menu="download-${task.task_id}-${article.id}"]`);
                                    if (!menuElement || !menuElement.matches(':hover')) {
                                      return { ...prev, [key]: false };
                                    }
                                    return prev;
                                  });
                                }, 100);
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              <button
                                disabled={downloading[`${task.task_id}-${article.id}-original`] || downloading[`${task.task_id}-${article.id}-translated`]}
                                className="px-3 py-1.5 bg-blue-600 text-white rounded text-xs hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                              >
                                下载
                              </button>
                              {hoverMenu[`download-${task.task_id}-${article.id}`] && (
                                <div 
                                  data-menu={`download-${task.task_id}-${article.id}`}
                                  className="absolute right-0 mt-1 w-32 bg-gray-800 border border-gray-700 rounded shadow-lg z-10"
                                  onMouseEnter={() => setHoverMenu({ ...hoverMenu, [`download-${task.task_id}-${article.id}`]: true })}
                                  onMouseLeave={() => setHoverMenu({ ...hoverMenu, [`download-${task.task_id}-${article.id}`]: false })}
                                >
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleDownload(task.task_id, article.id, 'original');
                                    }}
                                    disabled={downloading[`${task.task_id}-${article.id}-original`]}
                                    className="w-full text-left px-3 py-2 text-xs text-white hover:bg-gray-700 disabled:opacity-50 transition-colors"
                                  >
                                    {downloading[`${task.task_id}-${article.id}-original`] ? '下载中...' : '下载原文'}
                                  </button>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      handleDownload(task.task_id, article.id, 'translated');
                                    }}
                                    disabled={downloading[`${task.task_id}-${article.id}-translated`] || !article.content_cn}
                                    className="w-full text-left px-3 py-2 text-xs text-white hover:bg-gray-700 disabled:opacity-50 transition-colors border-t border-gray-700"
                                  >
                                    {downloading[`${task.task_id}-${article.id}-translated`] ? '下载中...' : '下载译文'}
                                  </button>
                                </div>
                              )}
                            </div>
                            
                            {/* 生成/下载音频按钮 - hover菜单 */}
                            <div 
                              className="relative"
                              onMouseEnter={() => setHoverMenu({ ...hoverMenu, [`audio-${task.task_id}-${article.id}`]: true })}
                              onMouseLeave={() => {
                                setTimeout(() => {
                                  setHoverMenu(prev => {
                                    const key = `audio-${task.task_id}-${article.id}`;
                                    const menuElement = document.querySelector(`[data-menu="audio-${task.task_id}-${article.id}"]`);
                                    if (!menuElement || !menuElement.matches(':hover')) {
                                      return { ...prev, [key]: false };
                                    }
                                    return prev;
                                  });
                                }, 100);
                              }}
                              onClick={(e) => e.stopPropagation()}
                            >
                              {hasAudio ? (
                                <button
                                  disabled={downloading[`${task.task_id}-${article.id}-audio`] || downloading[`${task.task_id}-${article.id}-audio_original`]}
                                  className="px-3 py-1.5 bg-purple-600 text-white rounded text-xs hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                  下载音频
                                </button>
                              ) : (
                                <button
                                  disabled={generatingAudio[`${task.task_id}-${article.id}-original`] || generatingAudio[`${task.task_id}-${article.id}-translated`] || article.status === 'generating'}
                                  className="px-3 py-1.5 bg-purple-600 text-white rounded text-xs hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-1.5"
                                >
                                  {article.status === 'generating' && (
                                    <div className="animate-spin h-3 w-3 border-2 border-white border-t-transparent rounded-full"></div>
                                  )}
                                  <span>{article.status === 'generating' ? `生成中 ${article.translation_progress || 0}%` : '生成音频'}</span>
                                </button>
                              )}
                              {hoverMenu[`audio-${task.task_id}-${article.id}`] && (
                                <div 
                                  data-menu={`audio-${task.task_id}-${article.id}`}
                                  className="absolute right-0 mt-1 w-36 bg-gray-800 border border-gray-700 rounded shadow-lg z-10"
                                  onMouseEnter={() => setHoverMenu({ ...hoverMenu, [`audio-${task.task_id}-${article.id}`]: true })}
                                  onMouseLeave={() => setHoverMenu({ ...hoverMenu, [`audio-${task.task_id}-${article.id}`]: false })}
                                >
                                  {hasAudio ? (
                                    <>
                                      {article.audio_path_original && (
                                        <button
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            handleDownload(task.task_id, article.id, 'audio_original');
                                          }}
                                          disabled={downloading[`${task.task_id}-${article.id}-audio_original`]}
                                          className="w-full text-left px-3 py-2 text-xs text-white hover:bg-gray-700 disabled:opacity-50 transition-colors"
                                        >
                                          {downloading[`${task.task_id}-${article.id}-audio_original`] ? '下载中...' : '原文音频下载'}
                                        </button>
                                      )}
                                      {article.audio_path && (
                                        <button
                                          onClick={(e) => {
                                            e.stopPropagation();
                                            handleDownload(task.task_id, article.id, 'audio');
                                          }}
                                          disabled={downloading[`${task.task_id}-${article.id}-audio`]}
                                          className="w-full text-left px-3 py-2 text-xs text-white hover:bg-gray-700 disabled:opacity-50 transition-colors border-t border-gray-700"
                                        >
                                          {downloading[`${task.task_id}-${article.id}-audio`] ? '下载中...' : '译文音频下载'}
                                        </button>
                                      )}
                                    </>
                                  ) : (
                                    <>
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleGenerateAudio(task.task_id, article.id, 'original');
                                        }}
                                        disabled={generatingAudio[`${task.task_id}-${article.id}-original`] || !article.content}
                                        className="w-full text-left px-3 py-2 text-xs text-white hover:bg-gray-700 disabled:opacity-50 transition-colors flex items-center gap-2"
                                      >
                                        {generatingAudio[`${task.task_id}-${article.id}-original`] && (
                                          <div className="animate-spin h-3 w-3 border-2 border-white border-t-transparent rounded-full"></div>
                                        )}
                                        <span>生成原文音频</span>
                                      </button>
                                      <button
                                        onClick={(e) => {
                                          e.stopPropagation();
                                          handleGenerateAudio(task.task_id, article.id, 'translated');
                                        }}
                                        disabled={generatingAudio[`${task.task_id}-${article.id}-translated`] || !article.content_cn}
                                        className="w-full text-left px-3 py-2 text-xs text-white hover:bg-gray-700 disabled:opacity-50 transition-colors border-t border-gray-700 flex items-center gap-2"
                                      >
                                        {generatingAudio[`${task.task_id}-${article.id}-translated`] && (
                                          <div className="animate-spin h-3 w-3 border-2 border-white border-t-transparent rounded-full"></div>
                                        )}
                                        <span>生成译文音频</span>
                                      </button>
                                    </>
                                  )}
                                </div>
                              )}
                            </div>
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
