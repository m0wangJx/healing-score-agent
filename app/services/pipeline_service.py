from app.services.scoring_service import simple_score_text
from app.services.llm_service import generate_supportive_reply


def run_pipeline(user_text: str) -> dict:
    score_result = simple_score_text(user_text)
    reply = generate_supportive_reply(
        user_text=user_text,
        risk_level=score_result["risk_level"]
    )

    return {
        "reply": reply,
        "risk_level": score_result["risk_level"],
        "score": score_result["score"]
    }