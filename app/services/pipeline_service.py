from app.services.scoring_service import score_text
from app.services.llm_service import generate_supportive_reply
from app.core.config import settings


def run_pipeline(user_text: str) -> dict:
    score_result = score_text(user_text)

    reply = generate_supportive_reply(
        user_text=user_text,
        risk_level=score_result["risk_level"],
        score=score_result["score"],
        evidence=score_result["evidence"],
    )

    return {
        "reply": reply,
        "risk_level": score_result["risk_level"],
        "score": score_result["score"],
        "evidence": score_result["evidence"],
        "model_provider": settings.llm_provider,
        "model_name": settings.llm_model,
    }