from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re


class BaseSpider(ABC):
    """爬虫基类"""
    
    @abstractmethod
    def crawl(self, url: str, max_articles: int = 10) -> List[Dict]:
        """
        爬取文章
        返回文章列表，每个文章包含：
        - title: 标题
        - content: 内容
        - url: 原文链接
        - publish_time: 发布时间
        - author: 作者
        """
        pass
    
    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """获取页面内容"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            }
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching page {url}: {e}")
            return None
    
    def extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        """提取文本内容"""
        element = soup.select_one(selector)
        return element.get_text(strip=True) if element else ""
    
    def extract_all_text(self, soup: BeautifulSoup, selector: str) -> str:
        """提取所有匹配元素的文本"""
        elements = soup.select(selector)
        return "\n\n".join([elem.get_text(strip=True) for elem in elements if elem.get_text(strip=True)])
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        # 简单的日期解析，可以根据需要扩展
        try:
            # 尝试多种日期格式
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d",
                "%B %d, %Y",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except:
                    continue
        except:
            pass
        return None

