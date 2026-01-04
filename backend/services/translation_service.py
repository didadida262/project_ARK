from googletrans import Translator
from typing import Optional
import sys
import os

# 添加backend目录到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from config import settings


class TranslationService:
    def __init__(self):
        self.translator = Translator()
        self.target_language = settings.translation_target_language
    
    def translate_text(self, text: str, source_language: Optional[str] = None) -> str:
        """
        翻译文本到目标语言（默认中文）
        """
        try:
            if source_language:
                result = self.translator.translate(text, src=source_language, dest=self.target_language)
            else:
                result = self.translator.translate(text, dest=self.target_language)
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            # 如果翻译失败，返回原文
            return text
    
    def translate_article(self, title: str, content: str) -> tuple[str, str]:
        """
        翻译文章标题和内容
        返回: (translated_title, translated_content)
        """
        translated_title = self.translate_text(title)
        translated_content = self.translate_text(content)
        return translated_title, translated_content


# 单例模式
translation_service = TranslationService()

