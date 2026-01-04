import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getArticle, downloadOriginal, downloadTranslated } from '../api/tasks';

function ArticleDetail() {
  const { articleId } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showOriginal, setShowOriginal] = useState(false);
  const [downloading, setDownloading] = useState({});

  useEffect(() => {
    loadArticle();
    // 如果正在翻译，每1秒刷新；否则每3秒刷新
    const interval = setInterval(loadArticle, 1000);
    return () => clearInterval(interval);
  }, [articleId]);
  
  // 当文章状态改变时，调整刷新频率
  useEffect(() => {
    if (article && article.status === 'completed') {
      // 已完成时，停止频繁刷新
      return;
    }
  }, [article?.status]);

  const loadArticle = async () => {
    try {
      const data = await getArticle(articleId);
      setArticle(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to load article:', error);
      setLoading(false);
    }
  };

  const handleDownload = async (type) => {
    setDownloading({ ...downloading, [type]: true });
    try {
      let blob;
      let filename;

      if (type === 'original') {
        blob = await downloadOriginal(articleId);
        filename = `${article.title}_original.txt`;
      } else if (type === 'translated') {
        blob = await downloadTranslated(articleId);
        filename = `${article.title_cn || article.title}_translated.txt`;
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
      setDownloading({ ...downloading, [type]: false });
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="text-center text-white">加载中...</div>
      </div>
    );
  }

  if (!article) {
    return (
      <div className="container mx-auto px-4 py-16">
        <div className="text-center text-white">文章不存在</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-16 max-w-4xl">
      <Link to={`/tasks/${article.task_id}`} className="text-blue-400 hover:text-blue-300 mb-6 inline-block">
        ← 返回任务列表
      </Link>

      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gray-800 rounded-lg border border-gray-700 p-8"
      >
        <div className="mb-6">
          <div className="flex items-center gap-4 mb-4">
            <button
              onClick={() => setShowOriginal(!showOriginal)}
              className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition-colors"
            >
              {showOriginal ? '显示中文' : '显示原文'}
            </button>
          </div>

          <h1 className="text-3xl font-bold text-white mb-4">
            {showOriginal ? article.title : (article.title_cn || article.title)}
          </h1>

          <div className="flex items-center gap-4 text-sm text-gray-400 mb-6 flex-wrap">
            {article.publish_time && (
              <span>{new Date(article.publish_time).toLocaleString()}</span>
            )}
            {article.author && <span>作者: {article.author}</span>}
            {article.translation_started_at && article.translation_completed_at && (
              <span>
                翻译耗时: {Math.round((new Date(article.translation_completed_at) - new Date(article.translation_started_at)) / 1000)}秒
              </span>
            )}
            <a
              href={article.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300"
            >
              查看原文
            </a>
          </div>
          
          {article.status === 'translating' && (
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-white font-medium">翻译进度</span>
                <span className="text-gray-400 text-sm">{article.translation_progress || 0}%</span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${article.translation_progress || 0}%` }}
                />
              </div>
            </div>
          )}
        </div>

        <div className="prose prose-invert max-w-none mb-8">
          {article.status === 'translating' && !article.content_cn && (
            <div className="mb-4 p-4 bg-blue-900/30 border border-blue-500 rounded-lg text-blue-200">
              <div className="flex items-center gap-2">
                <div className="animate-spin h-4 w-4 border-2 border-blue-400 border-t-transparent rounded-full"></div>
                <span>正在翻译中... {article.translation_progress || 0}%</span>
              </div>
            </div>
          )}
          <div className="text-white whitespace-pre-wrap leading-relaxed">
            {showOriginal
              ? article.content
              : (article.content_cn || article.content || '翻译中...')}
          </div>
        </div>

        <div className="flex gap-4 flex-wrap">
          <button
            onClick={() => handleDownload('original')}
            disabled={downloading.original}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
          >
            {downloading.original ? '下载中...' : '下载原文'}
          </button>
          {article.content_cn && (
            <button
              onClick={() => handleDownload('translated')}
              disabled={downloading.translated}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              {downloading.translated ? '下载中...' : '下载译文'}
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
}

export default ArticleDetail;

