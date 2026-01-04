import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { getArticle, downloadOriginal, downloadTranslated, downloadAudio } from '../api/tasks';

function ArticleDetail() {
  const { articleId } = useParams();
  const navigate = useNavigate();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showOriginal, setShowOriginal] = useState(false);
  const [downloading, setDownloading] = useState({});

  useEffect(() => {
    loadArticle();
    const interval = setInterval(loadArticle, 3000);
    return () => clearInterval(interval);
  }, [articleId]);

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
      } else if (type === 'audio') {
        blob = await downloadAudio(articleId);
        filename = `${article.title_cn || article.title}.mp3`;
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

          <div className="flex items-center gap-4 text-sm text-gray-400 mb-6">
            {article.publish_time && (
              <span>{new Date(article.publish_time).toLocaleString()}</span>
            )}
            {article.author && <span>作者: {article.author}</span>}
            <a
              href={article.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300"
            >
              查看原文
            </a>
          </div>
        </div>

        <div className="prose prose-invert max-w-none mb-8">
          <div className="text-white whitespace-pre-wrap leading-relaxed">
            {showOriginal
              ? article.content
              : (article.content_cn || article.content || '翻译中...')}
          </div>
        </div>

        {article.audio_path && (
          <div className="mb-8 p-6 bg-gray-900 rounded-lg">
            <h3 className="text-white font-medium mb-4">音频播放</h3>
            <audio
              controls
              className="w-full"
              src={`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/articles/${articleId}/download/audio`}
              preload="metadata"
            >
              您的浏览器不支持音频播放
            </audio>
          </div>
        )}

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
          {article.audio_path && (
            <button
              onClick={() => handleDownload('audio')}
              disabled={downloading.audio}
              className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
            >
              {downloading.audio ? '下载中...' : '下载音频'}
            </button>
          )}
        </div>
      </motion.div>
    </div>
  );
}

export default ArticleDetail;

