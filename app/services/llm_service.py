def generate_supportive_reply(user_text: str, risk_level: str) -> str:
    if risk_level == "high":
        return (
            "我注意到你现在可能处在很痛苦的状态。"
            "请尽快联系你信任的人，或联系当地紧急心理援助与医疗资源。"
        )

    if risk_level == "medium":
        return (
            "听起来你最近承受了很多。"
            "如果你愿意，可以继续告诉我，最近最让你难受的事情是什么。"
        )

    return (
        "谢谢你愿意说出来。"
        "你可以继续和我讲讲，你最近最在意的感受是什么。"
    )