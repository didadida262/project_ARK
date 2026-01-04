from gtts import gTTS
import os
import sys
from pathlib import Path

# 添加backend目录到路径
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, backend_dir)

from config import settings


class TTSService:
    def __init__(self):
        self.audio_storage_path = Path(settings.audio_storage_path)
        self.audio_storage_path.mkdir(parents=True, exist_ok=True)
        self.audio_format = settings.audio_format
    
    def text_to_speech(self, text: str, article_id: str, lang: str = "zh") -> str:
        """
        将文本转换为语音
        返回音频文件路径
        """
        try:
            audio_filename = f"{article_id}.{self.audio_format}"
            audio_path = self.audio_storage_path / audio_filename
            
            # 使用gTTS生成音频
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(str(audio_path))
            
            return str(audio_path)
        except Exception as e:
            print(f"TTS error: {e}")
            raise


# 单例模式
tts_service = TTSService()

