from app.core.safety import classify_risk


def simple_score_text(user_text: str) -> dict:
    result = classify_risk(user_text)
    return {
        "risk_level": result["risk_level"],
        "score": result["score"],
    }