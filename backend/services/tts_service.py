from gtts import gTTS
import os
import sys
import requests
from typing import Optional, Callable
from functools import wraps
import signal

# 添加backend目录到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from config import settings


class TimeoutError(Exception):
    pass


def timeout_handler(signum, frame):
    raise TimeoutError("Operation timed out")


class TTSService:
    def __init__(self):
        self.audio_storage_path = os.path.abspath("./storage/audio")
        # 确保存储目录存在
        os.makedirs(self.audio_storage_path, exist_ok=True)
    
    def text_to_speech(self, text: str, article_id: str, lang: str = "zh", progress_callback: Optional[Callable[[int], None]] = None) -> str:
        """
        将文本转换为语音
        返回音频文件路径
        
        Args:
            text: 要转换的文本
            article_id: 文章ID，用于生成文件名
            lang: 语言代码，默认中文
            progress_callback: 进度回调函数，参数为 (progress_percentage) 0-100
        """
        if not text:
            raise ValueError("Text cannot be empty")
        
        try:
            # gTTS单次处理的最大字符数约为5000
            max_chunk_length = 5000
            
            if len(text) <= max_chunk_length:
                # 短文本直接生成
                if progress_callback:
                    progress_callback(50)  # 开始生成
                
                audio_path = os.path.join(self.audio_storage_path, f"{article_id}.mp3")
                print(f"Generating audio for article {article_id} (short text, {len(text)} chars)...")
                
                try:
                    tts = gTTS(text=text, lang=lang, slow=False)
                    tts.save(audio_path)
                    print(f"✓ Audio generated successfully: {audio_path}")
                except Exception as e:
                    print(f"✗ Error generating audio: {e}")
                    raise
                
                if progress_callback:
                    progress_callback(100)  # 完成
                
                return audio_path
            else:
                # 长文本分段生成
                if progress_callback:
                    progress_callback(10)  # 开始处理
                
                # 按段落分割
                paragraphs = text.split('\n\n')
                audio_files = []
                
                for i, para in enumerate(paragraphs):
                    if not para.strip():
                        continue
                    
                    # 如果段落太长，按句子分割
                    if len(para) > max_chunk_length:
                        sentences = para.split('. ')
                        current_chunk = []
                        current_length = 0
                        
                        for sentence in sentences:
                            sentence = sentence.strip()
                            if not sentence:
                                continue
                            sentence_length = len(sentence)
                            
                            if current_length + sentence_length > max_chunk_length:
                                if current_chunk:
                                    chunk_text = '. '.join(current_chunk)
                                    chunk_audio = self._generate_chunk(chunk_text, f"{article_id}_chunk_{len(audio_files)}", lang)
                                    audio_files.append(chunk_audio)
                                
                                current_chunk = [sentence]
                                current_length = sentence_length
                            else:
                                current_chunk.append(sentence)
                                current_length += sentence_length
                        
                        # 处理最后一个chunk
                        if current_chunk:
                            chunk_text = '. '.join(current_chunk)
                            chunk_audio = self._generate_chunk(chunk_text, f"{article_id}_chunk_{len(audio_files)}", lang)
                            audio_files.append(chunk_audio)
                    else:
                        chunk_audio = self._generate_chunk(para, f"{article_id}_chunk_{len(audio_files)}", lang)
                        audio_files.append(chunk_audio)
                    
                    # 更新进度
                    if progress_callback:
                        progress = 10 + int((i + 1) / len(paragraphs) * 80)
                        progress_callback(min(progress, 90))
                
                # 合并音频文件
                if progress_callback:
                    progress_callback(95)  # 开始合并
                
                final_audio_path = self._merge_audio_files(audio_files, article_id)
                
                # 清理临时文件
                for temp_file in audio_files:
                    try:
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                    except:
                        pass
                
                if progress_callback:
                    progress_callback(100)  # 完成
                
                return final_audio_path
                
        except Exception as e:
            print(f"TTS error: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _generate_chunk(self, text: str, chunk_id: str, lang: str) -> str:
        """生成单个chunk的音频"""
        audio_path = os.path.join(self.audio_storage_path, f"{chunk_id}.mp3")
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(audio_path)
        return audio_path
    
    def _merge_audio_files(self, audio_files: list, article_id: str) -> str:
        """合并多个音频文件"""
        try:
            from pydub import AudioSegment
            
            combined = AudioSegment.empty()
            for audio_file in audio_files:
                if os.path.exists(audio_file):
                    audio = AudioSegment.from_mp3(audio_file)
                    combined += audio
                    # 添加短暂静音作为段落间隔
                    combined += AudioSegment.silent(duration=500)  # 0.5秒静音
            
            final_path = os.path.join(self.audio_storage_path, f"{article_id}.mp3")
            combined.export(final_path, format="mp3")
            return final_path
        except ImportError:
            # 如果没有pydub，只返回第一个文件
            print("Warning: pydub not installed, using first chunk only")
            return audio_files[0] if audio_files else None
        except Exception as e:
            print(f"Error merging audio: {e}")
            # 如果合并失败，返回第一个文件
            return audio_files[0] if audio_files else None


# 单例模式
tts_service = TTSService()
