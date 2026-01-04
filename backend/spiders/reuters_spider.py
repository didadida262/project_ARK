from typing import List, Dict
from spiders.base_spider import BaseSpider
from bs4 import BeautifulSoup
import re
import requests
import time
import xml.etree.ElementTree as ET


class ReutersSpider(BaseSpider):
    """路透社爬虫"""
    
    def crawl(self, url: str, max_articles: int = 10) -> List[Dict]:
        articles = []
        
        # 首先尝试使用RSS feed（更可靠）
        rss_urls = [
            "https://www.reuters.com/tools/rss",
            "https://feeds.reuters.com/reuters/topNews",
            "https://feeds.reuters.com/reuters/worldNews",
        ]
        
        # 尝试从RSS获取文章链接
        article_urls = []
        for rss_url in rss_urls:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                }
                response = requests.get(rss_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    try:
                        root = ET.fromstring(response.content)
                        # 解析RSS
                        for item in root.findall('.//item')[:max_articles]:
                            link_elem = item.find('link')
                            if link_elem is not None and link_elem.text:
                                article_urls.append(link_elem.text)
                        if article_urls:
                            print(f"Found {len(article_urls)} articles from RSS")
                            break
                    except ET.ParseError:
                        continue
            except Exception as e:
                print(f"RSS fetch error for {rss_url}: {e}")
                continue
        
        # 如果RSS失败，尝试直接访问页面
        if not article_urls:
            list_urls = [
                "https://www.reuters.com/",
                "https://www.reuters.com/world/",
            ]
            
            soup = None
            for list_url in list_urls:
                soup = self.fetch_page(list_url)
                if soup:
                    break
            
            if not soup:
                print("Failed to fetch any Reuters page")
                return articles
            
            # 从页面提取文章链接
            seen_urls = set()
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').strip()
                if not href:
                    continue
                    
                if '/article/' in href:
                    full_url = href if href.startswith('http') else f"https://www.reuters.com{href}"
                    full_url = full_url.split('?')[0].split('#')[0]
                    
                    if full_url not in seen_urls:
                        seen_urls.add(full_url)
                        article_urls.append(full_url)
                        if len(article_urls) >= max_articles * 2:
                            break
        
        # 查找文章链接 - 改进选择器
        article_links = []
        seen_urls = set()
        
        # 查找所有可能的文章链接
        for link in soup.find_all('a', href=True):
            href = link.get('href', '').strip()
            if not href:
                continue
                
            # 路透社文章URL模式
            if any(pattern in href for pattern in ['/article/', '/world/', '/business/', '/markets/', '/technology/']):
                # 跳过非文章链接
                if any(skip in href for skip in ['/tag/', '/author/', '/search', '/video/', '/live/']):
                    continue
                    
                full_url = href if href.startswith('http') else f"https://www.reuters.com{href}"
                # 清理URL
                full_url = full_url.split('?')[0].split('#')[0]
                
                if full_url not in seen_urls and '/article/' in full_url:
                    seen_urls.add(full_url)
                    article_links.append(full_url)
                    if len(article_links) >= max_articles * 2:  # 多找一些，因为有些可能无法访问
                        break
        
        print(f"Found {len(article_urls)} potential article URLs")
        
        # 爬取每篇文章
        for article_url in article_urls[:max_articles * 2]:
            if len(articles) >= max_articles:
                break
            article = self.crawl_article(article_url)
            if article and article.get('title') and article.get('content') and len(article.get('content', '')) > 100:
                articles.append(article)
                print(f"Successfully crawled article: {article.get('title', '')[:50]}")
            # 添加延迟避免被封
            time.sleep(1)
        
        print(f"Successfully crawled {len(articles)} articles")
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

