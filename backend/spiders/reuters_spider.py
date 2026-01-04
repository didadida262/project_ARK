from typing import List, Dict
from spiders.base_spider import BaseSpider
from bs4 import BeautifulSoup
import re


class ReutersSpider(BaseSpider):
    """路透社爬虫"""
    
    def crawl(self, url: str, max_articles: int = 10) -> List[Dict]:
        articles = []
        
        # 路透社新闻列表页
        list_url = "https://www.reuters.com/world/"
        soup = self.fetch_page(list_url)
        
        if not soup:
            return articles
        
        # 查找文章链接
        article_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            # 路透社文章URL模式
            if '/article/' in href or '/world/' in href or '/business/' in href:
                full_url = href if href.startswith('http') else f"https://www.reuters.com{href}"
                if full_url not in article_links:
                    article_links.append(full_url)
                    if len(article_links) >= max_articles:
                        break
        
        # 爬取每篇文章
        for article_url in article_links[:max_articles]:
            article = self.crawl_article(article_url)
            if article:
                articles.append(article)
        
        return articles
    
    def crawl_article(self, url: str) -> Dict:
        """爬取单篇文章"""
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # 提取标题
        title = self.extract_text(soup, 'h1[data-testid="Heading"]') or \
                self.extract_text(soup, 'h1') or \
                self.extract_text(soup, '.article-header__title__3YxCq')
        
        # 提取内容
        content_parts = []
        
        # 尝试多种内容选择器
        content_selectors = [
            'div[data-testid="paragraph"]',
            '.article-body__content__17Yit p',
            '.StandardArticleBody_body p',
            'article p',
        ]
        
        for selector in content_selectors:
            content = self.extract_all_text(soup, selector)
            if content and len(content) > 100:  # 确保有足够的内容
                content_parts.append(content)
                break
        
        if not content_parts:
            # 备用方案：提取所有段落
            paragraphs = soup.find_all('p')
            content_parts = [p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)]
        
        content = "\n\n".join(content_parts)
        
        # 提取发布时间
        publish_time = None
        time_elem = soup.find('time')
        if time_elem:
            datetime_str = time_elem.get('datetime') or time_elem.get_text(strip=True)
            publish_time = self.parse_date(datetime_str)
        
        # 提取作者
        author = self.extract_text(soup, '[data-testid="Byline"]') or \
                 self.extract_text(soup, '.article-header__author-name')
        
        return {
            "title": title,
            "content": content,
            "url": url,
            "publish_time": publish_time,
            "author": author
        }

