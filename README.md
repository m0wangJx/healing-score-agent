# Healing Score Agent

一个用于“疗愈对话 + 风险评分”的后端原型项目。

## 1. 项目简介

本项目用于从 0 开始实践一个简单的心理支持对话 Agent 原型，目标是逐步完成这样一条基础链路：

**用户输入文本 -> 风险评分 -> 支持性回复 -> 后续扩展到本地 LLM / 微信接入 / 数据存储**

当前版本重点不在“临床可用”，而在于：

- 熟悉 Python 后端项目搭建
- 熟悉 Git 和 GitHub 的基本协作流程
- 学习最小可运行 Agent / pipeline 的组织方式
- 为后续接入本地模型、评分模块和微信消息链路做准备

---

## 2. 当前已实现功能

当前版本已经支持：

- 使用 FastAPI 启动本地后端服务
- 提供健康检查接口：`/health`
- 提供聊天接口：`/chat/message`
- 基于简单规则的风险评分
- 根据风险等级生成不同风格的支持性回复
- 使用 Git 本地管理代码
- 同步项目到 GitHub 仓库

---

## 3. 当前系统流程

当前最小原型的处理流程如下：

1. 用户发送一段文本
2. 后端接收文本请求
3. 评分模块根据关键词进行简单风险判断
4. 系统生成对应的支持性回复
5. 返回：
   - `reply`
   - `risk_level`
   - `score`

当前版本的 `risk_level` 分为：

- `low`
- `medium`
- `high`

当前版本的 `score` 为简化演示用分数，不代表正式心理测评结果。

---

## 4. 项目结构

```text
healing-score-agent/
├── README.md
├── .gitignore
├── .env.example
├── requirements.txt
├── pyproject.toml
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes_chat.py
│   │   ├── routes_health.py
│   │   └── routes_admin.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── safety.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── database.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py
│   │   ├── scoring_service.py
│   │   ├── pipeline_service.py
│   │   ├── memory_service.py
│   │   └── crisis_service.py
│   ├── prompts/
│   │   ├── supportive_reply.txt
│   │   ├── risk_assessment.txt
│   │   └── crisis_reply.txt
│   ├── repos/
│   │   ├── __init__.py
│   │   └── conversation_repo.py
│   └── utils/
│       ├── __init__.py
│       ├── text_clean.py
│       └── json_parser.py
├── data/
│   ├── logs/
│   └── samples/
├── tests/
│   ├── test_api.py
│   ├── test_scoring.py
│   └── test_pipeline.py
├── scripts/
│   ├── init_db.py
│   ├── run_local.sh
│   └── demo_client.py
└── docs/
    ├── architecture.md
    ├── api_spec.md
    ├── deployment.md
    └── roadmap.md