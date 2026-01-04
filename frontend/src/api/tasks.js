import client from './client';

export const createTask = async (title, content) => {
  const response = await client.post('/api/tasks', { 
    title, 
    content
  });
  return response.data;
};

export const getTask = async (taskId) => {
  const response = await client.get(`/api/tasks/${taskId}`);
  return response.data;
};

export const getTasks = async (skip = 0, limit = 20) => {
  const response = await client.get('/api/tasks', {
    params: { skip, limit },
  });
  return response.data;
};

export const getTaskArticles = async (taskId) => {
  const response = await client.get(`/api/tasks/${taskId}/articles`);
  return response.data;
};

export const getArticle = async (articleId) => {
  const response = await client.get(`/api/articles/${articleId}`);
  return response.data;
};

export const downloadOriginal = async (articleId) => {
  const response = await client.get(`/api/articles/${articleId}/download/original`, {
    responseType: 'blob',
  });
  return response.data;
};

export const downloadTranslated = async (articleId) => {
  const response = await client.get(`/api/articles/${articleId}/download/translated`, {
    responseType: 'blob',
  });
  return response.data;
};

export const deleteAllTasks = async () => {
  const response = await client.delete('/api/tasks/all');
  return response.data;
};

