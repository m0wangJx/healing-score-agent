from typing import Dict, Any, Optional
from operator import itemgetter
from langchain_core.runnables import RunnableLambda, RunnableParallel
from app.services.scoring_service import score_text_and_audio
from app.services.llm_service import generate_supportive_reply
from app.core.config import settings


# 将评估逻辑包装为 RunnableLambda
scorer = RunnableLambda(
    lambda x: score_text_and_audio(
        text=x["user_text"],
        audio_path=x.get("audio_path")
    )
)

# 将回复生成逻辑包装为支持字典输入的 RunnableLambda
def _map_risk_level(risk_level_cn: str) -> str:
    """将评分引擎的中文风险等级映射为 generate_supportive_reply 所需的英文等级"""
    mapping = {"重度": "high", "中度": "medium", "轻度": "low", "正常": "low"}
    return mapping.get(risk_level_cn, "low")


def _format_evidence(details: dict) -> list:
    """将评分引擎的 details 字典转为 generate_supportive_reply 所需的字符串列表"""
    evidence = []
    text_features = details.get("text_features_extracted", {})
    if text_features:
        feature_labels = {
            "anhedonia": "快感缺失", "depressed": "情绪低落", "sleep": "睡眠问题",
            "fatigue": "疲劳", "appetite": "食欲变化", "guilt": "内疚感",
            "concentrate": "注意力困难", "movement": "运动迟缓"
        }
        high_items = [(k, v) for k, v in sorted(text_features.items(), key=lambda x: x[1], reverse=True) if v >= 1]
        for k, v in high_items[:4]:
            evidence.append(f"{feature_labels.get(k, k)}: {v}/3分")

    audio_summary = details.get("audio_features_summary")
    if isinstance(audio_summary, dict):
        evidence.append(
            f"音频特征: 基频均值 {audio_summary.get('pitch_mean_hz', 'N/A')}Hz, "
            f"能量均值 {audio_summary.get('energy_mean', 'N/A')}"
        )

    return evidence if evidence else ["评估数据不足"]


replier = RunnableLambda(
    lambda x: {
        "reply": generate_supportive_reply(
            user_text=x["user_text"],
            risk_level=_map_risk_level(x["score_result"]["risk_level"]),
            score=x["score_result"]["predicted_sds_score"],
            evidence=_format_evidence(x["score_result"]["details"]),
        ),
        "score_result": x["score_result"],
    }
)

# 构建 LCEL 链：保持 user_text，同时并行运行评分服务
step_a = RunnableParallel(
    user_text=RunnableLambda(itemgetter("user_text")),
    audio_path=RunnableLambda(lambda x: x.get("audio_path")),
    score_result=scorer
)

# 完整链条定义
chain = step_a | replier


# 运行函数
def run_pipeline(user_text: str, audio_path: Optional[str] = None) -> dict:

    # 直接复用全局已经构建好的 chain
    result: Dict[str, Any] = chain.invoke({
        "user_text": user_text,
        "audio_path": audio_path
    })

    score_res: Dict[str, Any] = result["score_result"]

    # 组装最终输出
    return {
        "reply": result["reply"],
        "risk_level": score_res["risk_level"],
        "score": score_res["predicted_sds_score"],
        "evidence": score_res["details"],
        "model_provider": settings.llm_provider,
        "model_name": settings.llm_model,
    }