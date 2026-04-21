from app.services.pipeline_service import run_pipeline


def test_pipeline_returns_required_fields():
    result = run_pipeline("我最近很难过，感觉没有希望了")

    assert "reply" in result
    assert "risk_level" in result
    assert "score" in result
    assert "evidence" in result
    assert "model_provider" in result
    assert "model_name" in result

    assert result["risk_level"] in ["low", "medium", "high"]
    assert isinstance(result["score"], int)
    assert isinstance(result["evidence"], list)
    assert isinstance(result["reply"], str)
    assert isinstance(result["model_provider"], str)
    assert isinstance(result["model_name"], str)