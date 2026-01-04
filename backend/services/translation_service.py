import argostranslate.package
import argostranslate.translate
from typing import Optional, Callable
import sys
import os
import time

# 添加backend目录到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from config import settings


class TranslationService:
    def __init__(self):
        self.target_language = settings.translation_target_language
        # Argos Translate使用语言代码，中文是'zh'
        self.target_lang_code = 'zh' if self.target_language == 'zh' else self.target_language
        # 默认源语言（自动检测或英文）
        self.default_source_lang_code = 'en'
        
        # 确保已安装语言包
        self._ensure_package_installed()
    
    def _ensure_package_installed(self):
        """确保必要的语言包已安装"""
        try:
            # 更新可用包列表
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            
            # 检查并安装英文到中文的语言包
            package_to_use = None
            for package in available_packages:
                if package.from_code == self.default_source_lang_code and package.to_code == self.target_lang_code:
                    package_to_use = package
                    break
            
            if package_to_use:
                # 检查是否已安装
                installed_packages = argostranslate.package.get_installed_packages()
                is_installed = any(
                    pkg.from_code == package_to_use.from_code and pkg.to_code == package_to_use.to_code
                    for pkg in installed_packages
                )
                
                if not is_installed:
                    print(f"Installing language package: {package_to_use.from_code} -> {package_to_use.to_code}")
                    argostranslate.package.install_from_path(package_to_use.download())
                    print("Language package installed successfully")
            else:
                print(f"Warning: Language package {self.default_source_lang_code} -> {self.target_lang_code} not found")
        except Exception as e:
            print(f"Error ensuring language package: {e}")
    
    def translate_text(self, text: str, source_language: Optional[str] = None, max_chunk_length: int = 1000, progress_callback: Optional[Callable[[int, int], None]] = None) -> str:
        """
        翻译文本到目标语言（默认中文）
        对于长文本，分段翻译以提高速度
        progress_callback: 进度回调函数，参数为 (current_chunk, total_chunks)
        
        注意：Argos Translate是离线翻译，不需要网络连接，但chunk大小建议较小（1000字符）
        """
        if not text:
            return text
        
        try:
            # 确定源语言代码
            source_lang_code = source_language if source_language else self.default_source_lang_code
            
            # 如果文本较短，直接翻译
            if len(text) <= max_chunk_length:
                translated_text = argostranslate.translate.translate(text, source_lang_code, self.target_lang_code)
                if progress_callback:
                    progress_callback(1, 1)
                return translated_text
            
            # 长文本分段翻译
            print(f"Text length {len(text)} exceeds limit, splitting into chunks...")
            
            # 按段落分割文本
            paragraphs = text.split('\n\n')
            chunks = []
            current_chunk = []
            current_length = 0
            
            for para in paragraphs:
                para_length = len(para)
                # 如果单个段落就超过限制，按句子分割
                if para_length > max_chunk_length:
                    # 先处理当前chunk
                    if current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                        current_chunk = []
                        current_length = 0
                    
                    # 按句子分割长段落
                    sentences = para.split('. ')
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue
                        sentence_length = len(sentence)
                        if current_length + sentence_length > max_chunk_length:
                            if current_chunk:
                                chunks.append('\n\n'.join(current_chunk))
                                current_chunk = []
                                current_length = 0
                        current_chunk.append(sentence)
                        current_length += sentence_length
                else:
                    # 如果加上当前段落超过限制，先处理当前chunk
                    if current_length + para_length > max_chunk_length and current_chunk:
                        chunks.append('\n\n'.join(current_chunk))
                        current_chunk = []
                        current_length = 0
                    current_chunk.append(para)
                    current_length += para_length
            
            # 添加最后一个chunk
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            
            print(f"Split into {len(chunks)} chunks for translation")
            
            # 翻译每个chunk
            translated_chunks = []
            for i, chunk in enumerate(chunks):
                try:
                    print(f"Translating chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
                    translated_chunk = argostranslate.translate.translate(chunk, source_lang_code, self.target_lang_code)
                    translated_chunks.append(translated_chunk)
                    
                    # 调用进度回调
                    if progress_callback:
                        progress_callback(i + 1, len(chunks))
                except Exception as e:
                    print(f"Error translating chunk {i+1}: {e}")
                    # 如果翻译失败，使用原文
                    translated_chunks.append(chunk)
                    if progress_callback:
                        progress_callback(i + 1, len(chunks))
            
            # 合并翻译结果
            return '\n\n'.join(translated_chunks)
            
        except Exception as e:
            print(f"Translation error: {e}")
            import traceback
            traceback.print_exc()
            # 如果翻译失败，返回原文
            return text
    
    def translate_article(self, title: str, content: str, progress_callback: Optional[Callable[[int], None]] = None) -> tuple[str, str]:
        """
        翻译文章标题和内容
        返回: (translated_title, translated_content)
        progress_callback: 进度回调函数，参数为 (progress_percentage) 0-100
        """
        try:
            # 翻译标题 (占10%进度)
            translated_title = self.translate_text(title)
            if progress_callback:
                progress_callback(10)  # 标题翻译完成，10%
        except Exception as e:
            print(f"Error translating title: {e}")
            translated_title = title  # 翻译失败时使用原标题
            if progress_callback:
                progress_callback(10)
        
        try:
            # 翻译内容 (占90%进度)
            # 计算内容需要分成多少块
            max_chunk_length = 1000  # Argos Translate建议较小的chunk大小
            content_length = len(content)
            
            if content_length > max_chunk_length:
                # 估算chunk数量（用于进度计算）
                estimated_chunks = (content_length // max_chunk_length) + 1
                
                def content_progress(current: int, total: int):
                    # 标题已完成10%，内容从10%开始到100%
                    # current/total 是内容的进度比例 (0-1)
                    # 映射到 10-100%
                    content_progress_pct = (current / total) * 90  # 0-90%
                    overall_progress = 10 + int(content_progress_pct)  # 10-100%
                    if progress_callback:
                        progress_callback(overall_progress)
                
                translated_content = self.translate_text(content, progress_callback=content_progress)
            else:
                translated_content = self.translate_text(content)
                if progress_callback:
                    progress_callback(100)  # 内容翻译完成
        except Exception as e:
            print(f"Error translating content: {e}")
            translated_content = content  # 翻译失败时使用原内容
            if progress_callback:
                progress_callback(100)
        
        return translated_title, translated_content


# 单例模式
translation_service = TranslationService()
