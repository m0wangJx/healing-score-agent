from app.services.llm_service import score_with_llm


def score_text(user_text: str) -> dict:
    result = score_with_llm(user_text)

    risk_level = result.get("risk_level", "low")
    score = result.get("score", 20)
    evidence = result.get("evidence", [])

    if risk_level not in ["low", "medium", "high"]:
        risk_level = "low"

    if not isinstance(score, int):
        score = 20

    if not isinstance(evidence, list):
        evidence = ["evidence 格式异常，已回退"]

    return {
        "risk_level": risk_level,
        "score": score,
        "evidence": evidence,
    }