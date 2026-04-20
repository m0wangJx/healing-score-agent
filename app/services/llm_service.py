import requests
from app.core.config import settings


def generate_supportive_reply(user_text: str, risk_level: str) -> str:
    system_prompt = (
        "你是一个谨慎、温和、非评判的心理支持型助手。"
        "你的任务是提供支持性回应，而不是做医学诊断。"
        "请使用中文回复，控制在2到5句话内，语气自然、简洁、共情。"
    )

    if risk_level == "high":
        extra_instruction = (
            "当前用户文本表现出较高风险。"
            "请优先表达关切，并建议尽快联系现实中的可信任对象、心理援助热线或医疗资源。"
            "不要做轻率安慰。"
        )
    elif risk_level == "medium":
        extra_instruction = (
            "当前用户文本表现出中等风险。"
            "请表达理解与支持，并鼓励用户继续描述当前最困扰的问题。"
        )
    else:
        extra_instruction = (
            "当前用户文本风险较低。"
            "请给出温和、支持性、开放式的回应。"
        )

    full_prompt = (
        f"{system_prompt}\n"
        f"{extra_instruction}\n"
        f"用户输入：{user_text}\n"
        f"请直接输出给用户的回复，不要解释你的推理过程。"
    )

    response = requests.post(
        f"{settings.ollama_base_url}/api/generate",
        json={
            "model": settings.llm_model,
            "prompt": full_prompt,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()

    data = response.json()
    return data["response"].strip()