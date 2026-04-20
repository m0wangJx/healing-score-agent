def simple_score_text(user_text: str) -> dict:
    high_risk_keywords = ["不想活", "自杀", "结束生命", "活着没意义"]
    medium_risk_keywords = ["失眠", "痛苦", "绝望", "难过", "没有希望"]

    for word in high_risk_keywords:
        if word in user_text:
            return {
                "risk_level": "high",
                "score": 90
            }

    for word in medium_risk_keywords:
        if word in user_text:
            return {
                "risk_level": "medium",
                "score": 60
            }

    return {
        "risk_level": "low",
        "score": 20
    }