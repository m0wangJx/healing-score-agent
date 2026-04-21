import json
import re
import requests
from app.core.config import settings


HIGH_RISK_KEYWORDS = [
    "不想活",
    "活着没意义",
    "想死",
    "自杀",
    "结束生命",
    "不如死了",
    "我不想活了",
    "我想死",
]


def _call_ollama(prompt: str) -> str:
    response = requests.post(
        f"{settings.ollama_base_url}/api/generate",
        json={
            "model": settings.llm_model,
            "prompt": prompt,
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    data = response.json()
    return data["response"].strip()


def _extract_json_object(text: str) -> dict:
    """
    尽量从 LLM 输出中提取 JSON。
    支持：
    - 纯 JSON
    - ```json ... ``` 代码块
    - JSON 前后带说明文字
    """
    text = text.strip()

    # 1. 直接尝试整体解析
    try:
        return json.loads(text)
    except Exception:
        pass

    # 2. 去掉 markdown 代码块
    code_block_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if code_block_match:
        candidate = code_block_match.group(1)
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # 3. 提取第一个 {...}
    brace_match = re.search(r"\{.*\}", text, re.DOTALL)
    if brace_match:
        candidate = brace_match.group(0)
        try:
            return json.loads(candidate)
        except Exception:
            pass

    raise ValueError("无法从 LLM 输出中提取合法 JSON")


def score_with_llm(user_text: str) -> dict:
    # 第一层保险：显式高危表达直接硬判 high
    triggered_high_risk = [kw for kw in HIGH_RISK_KEYWORDS if kw in user_text]
    if triggered_high_risk:
        return {
            "risk_level": "high",
            "score": 95,
            "evidence": [f"命中高危表达：{kw}" for kw in triggered_high_risk[:3]],
        }

    prompt = f"""
你是一个文本风险评估助手。
请根据用户输入，判断其心理风险等级，并输出严格 JSON。

请注意以下分级标准：

1. low：
- 仅有日常疲惫、一般压力、轻度负面情绪
- 仍表现出希望、行动意愿、解决问题的动力
- 没有明显绝望、无助、自伤、自杀相关表达

2. medium：
- 有较明显的持续性痛苦、无助感、绝望感、失眠、情绪低落
- 表达“没有希望”“撑不下去”“崩溃”等
- 但没有直接自伤、自杀或结束生命的表述

3. high：
- 明确表达“不想活”“想死”“自杀”“结束生命”“活着没意义”等
- 或明显接近危机状态，需要尽快联系现实支持与专业帮助

输出要求：
1. 只输出 JSON
2. 不要输出解释
3. 不要输出 markdown 代码块
4. risk_level 只能是 low、medium、high 之一
5. score 必须是 0 到 100 的整数
6. evidence 必须是字符串数组，给出 2 到 4 条判断依据

输出格式必须严格如下：
{{
  "risk_level": "low",
  "score": 20,
  "evidence": ["依据1", "依据2"]
}}

用户输入：
{user_text}
""".strip()

    raw_text = _call_ollama(prompt)

    try:
        result = _extract_json_object(raw_text)

        risk_level = result.get("risk_level", "low")
        score = int(result.get("score", 20))
        evidence = result.get("evidence", [])

        if risk_level not in ["low", "medium", "high"]:
            risk_level = "low"

        if score < 0:
            score = 0
        if score > 100:
            score = 100

        if not isinstance(evidence, list):
            evidence = ["evidence 格式异常，已回退"]

        return {
            "risk_level": risk_level,
            "score": score,
            "evidence": evidence,
        }

    except Exception:
        return {
            "risk_level": "medium",
            "score": 50,
            "evidence": ["LLM评分解析失败，回退到中风险人工保守值"],
        }


def generate_supportive_reply(
    user_text: str,
    risk_level: str,
    score: int,
    evidence: list[str],
) -> str:
    if risk_level == "high":
        extra_instruction = (
            "当前用户表现出较高风险。"
            "请优先表达关切和陪伴感，明确建议其尽快联系现实中的可信任对象、心理援助热线或医疗资源。"
            "不要做轻率安慰，不要淡化风险，不要给出医学诊断。"
        )
    elif risk_level == "medium":
        extra_instruction = (
            "当前用户表现出中等风险。"
            "请表达理解与支持，并鼓励其继续描述当前最困扰的问题。"
        )
    else:
        extra_instruction = (
            "当前用户风险较低。"
            "请给出温和、支持性、开放式的回应。"
        )

    prompt = f"""
你是一个谨慎、温和、非评判的心理支持型助手。
你的任务是给用户提供支持性回应，而不是医学诊断。
请使用中文回复，控制在 2 到 5 句话内，语气自然、简洁、共情。

已知评分结果：
- 风险等级：{risk_level}
- 分数：{score}
- 判断依据：{evidence}

额外要求：
{extra_instruction}

用户输入：
{user_text}

请直接输出给用户的回复，不要解释推理过程，不要输出项目符号。
""".strip()

    return _call_ollama(prompt)