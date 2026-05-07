import os
from typing import Optional
from app.models.scoring_engine import UnifiedDepressionEngine
from app.core.config import settings

# 1. 动态生成模型的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
v1_path = os.path.abspath(os.path.join(current_dir, "..", "models", "eatd_rf_model_v1.joblib"))
v2_path = os.path.abspath(os.path.join(current_dir, "..", "models", "eatd_multimodal_rf_model_v2.joblib"))

# 2. 传入绝对路径
engine = UnifiedDepressionEngine(
    v1_model_path=v1_path,
    v2_model_path=v2_path,
    api_key=settings.dashscope_api_key
)

def score_text_and_audio(text: str, audio_path: Optional[str] = None) -> dict:
    return engine.predict(text=text, audio_path=audio_path)