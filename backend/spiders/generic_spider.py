from typing import List, Dict
from spiders.base_spider import BaseSpider
from bs4 import BeautifulSoup
import re


class GenericSpider(BaseSpider):
    """通用爬虫，适用于大多数新闻网站"""
    
    def crawl(self, url: str, max_articles: int = 10) -> List[Dict]:
        articles = []
        
        soup = self.fetch_page(url)
        if not soup:
            return articles
        
        # 查找文章链接（常见的新闻网站模式）
        article_links = []
        
        # 查找所有链接
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # 判断是否为文章链接
            if self.is_article_link(href, text):
                full_url = self.normalize_url(href, url)
                if full_url and full_url not in article_links:
                    article_links.append(full_url)
                    if len(article_links) >= max_articles:
                        break
        
        # 爬取每篇文章
        for article_url in article_links[:max_articles]:
            article = self.crawl_article(article_url)
            if article and article.get('title') and article.get('content'):
                articles.append(article)
        
        return articles
    
    def is_article_link(self, href: str, text: str) -> bool:
        """判断链接是否为文章链接"""
        # 排除的链接模式
        exclude_patterns = [
            r'^#',
            r'javascript:',
            r'mailto:',
            r'^/$',
            r'/tag/',
            r'/category/',
            r'/author/',
            r'/search',
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return False
        
        # 文章链接的特征
        article_patterns = [
            r'/article/',
            r'/news/',
            r'/story/',
            r'/\d{4}/\d{2}/',
            r'/[a-z]+-[a-z]+',
        ]
        
        for pattern in article_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return True
        
        # 如果链接文本足够长，可能是文章
        if len(text) > 20 and not any(exclude in href.lower() for exclude in ['home', 'about', 'contact']):
            return True
        
        return False
    
    def normalize_url(self, href: str, base_url: str) -> str:
        """规范化URL"""
        if href.startswith('http://') or href.startswith('https://'):
            return href
        elif href.startswith('//'):
            return 'https:' + href
        elif href.startswith('/'):
            from urllib.parse import urlparse
            parsed = urlparse(base_url)
            return f"{parsed.scheme}://{parsed.netloc}{href}"
        else:
            return f"{base_url.rstrip('/')}/{href}"
    
    def crawl_article(self, url: str) -> Dict:
        """爬取单篇文章"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # 提取标题（尝试多种选择器）
        title = None
        title_selectors = [
            'h1',
            'article h1',
            '.article-title',
            '.post-title',
            '.entry-title',
            '[itemprop="headline"]',
        ]
        
        for selector in title_selectors:
            title = self.extract_text(soup, selector)
            if title and len(title) > 10:
                break
        
        # 提取内容（尝试多种选择器）
        content = None
        content_selectors = [
            'article',
            '.article-body',
            '.post-content',
            '.entry-content',
            '[itemprop="articleBody"]',
            'main',
        ]
        
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                # 提取所有段落
                paragraphs = elem.find_all('p')
                content_parts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
                content = "\n\n".join(content_parts)
                if content and len(content) > 100:
                    break
        
        if not content:
            # 备用方案：提取所有段落
            paragraphs = soup.find_all('p')
            content_parts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
            content = "\n\n".join(content_parts)
        
        # 提取发布时间
        publish_time = None
        time_selectors = [
            'time[datetime]',
            'time',
            '[itemprop="datePublished"]',
            '.publish-date',
            '.post-date',
        ]
        
        for selector in time_selectors:
            time_elem = soup.select_one(selector)
            if time_elem:
                datetime_str = time_elem.get('datetime') or time_elem.get_text(strip=True)
                publish_time = self.parse_date(datetime_str)
                if publish_time:
                    break
        
        # 提取作者
        author = None
        author_selectors = [
            '[itemprop="author"]',
            '.author',
            '.by-author',
            '.post-author',
        ]
        
        for selector in author_selectors:
            author = self.extract_text(soup, selector)
            if author:
                break
        
        return {
            "title": title or "Untitled",
            "content": content or "",
            "url": url,
            "publish_time": publish_time,
            "author": author
        }

