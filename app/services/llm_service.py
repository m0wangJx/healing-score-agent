
### 封装llm，runnable组件 reply_step
'''memory_step:
        input:
            user_text
            score_result
            session_id
            persistent_score
            risk_level
        output:
            reply
            score_result
            persistent_score
            risk_level
            evidence

'''
import os

import requests
from langchain_core.runnables import RunnableLambda
from app.core.config import settings
from app.prompt.knowledge_loader import KnowledgeBase

_kb: KnowledgeBase | None = None

_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "prompts")

with open(os.path.join(_TEMPLATE_DIR, "system_prompt.md"), "r", encoding="utf-8") as _f:
    REPLY_SYSTEM_PROMPT_TEMPLATE = _f.read()


def _get_kb() -> KnowledgeBase:
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb


def _call_ollama(prompt: str, system: str = "") -> str:
    body: dict = {
        "model": settings.llm_model,
        "prompt": prompt,
        "stream": False,
    }
    if system:
        body["system"] = system
    response = requests.post(
        f"{settings.ollama_base_url}/api/generate",
        json=body,
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["response"].strip()


def generate_supportive_reply(
    user_text: str,
    risk_level: str,
    persistent_score: int,
    evidence: list[str],
) -> str:

    if risk_level == "high":
        extra_instruction = (
            "当前用户表现出高风险。"
            "请优先表达关切和陪伴感，明确建议其尽快联系现实中的可信任对象、心理援助热线或医疗资源。"
            "不要做轻率安慰，不要淡化风险，不要给出医学诊断。"
        )
        refs = ["crisis-resources", "suicide-prevention"]
    elif risk_level == "medium":
        extra_instruction = (
            "当前用户表现出中等风险。"
            "请表达理解与支持，并鼓励其继续描述当前最困扰的问题。"
        )
        refs = ["emotion-support", "cbt-techniques"]
    elif risk_level == "low":
        extra_instruction = (
            "当前用户风险较低。"
            "请给出温和、支持性、开放式的回应。"
        )
        refs = ["emotion-support", "meditation-scripts"]
    elif risk_level == "normal":
        extra_instruction = (
            "当前用户无抑郁症风险，请正常交流"
        )
        refs = []
    else:
        extra_instruction = "请给出温和、支持性的回应。"
        refs = []

    kb = _get_kb()
    prompt_knowledge = kb.generate_prompt(include_refs=refs)
    prompt = user_text

    system_prompt = REPLY_SYSTEM_PROMPT_TEMPLATE.format(
        risk_level=risk_level,
        persistent_score=persistent_score,
        evidence="; ".join(evidence),
        extra_instruction=extra_instruction,
        prompt_knowledge=prompt_knowledge,
    ).strip()

    print(system_prompt)

    return _call_ollama(prompt, system=system_prompt)


def _format_evidence(details: dict) -> list:
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

### 构建runnable组件
reply_step = RunnableLambda(lambda x: {
    "reply": generate_supportive_reply(
        user_text=x["user_text"],
        risk_level=x["risk_level"],
        persistent_score=int(x["persistent_score"]),
        evidence=_format_evidence(x["score_result"]["details"]),
    ),
    "score_result": x["score_result"],
    "persistent_score": x["persistent_score"],
    "risk_level": x["risk_level"],
    "evidence": _format_evidence(x["score_result"]["details"]),
})
