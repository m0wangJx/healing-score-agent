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


## 2. 当前已实现功能

当前版本已经支持：

- 使用 FastAPI 启动本地后端服务
- 提供健康检查接口：`/health`
- 提供聊天接口：`/chat/message`
- 基于简单规则的风险评分
- 根据风险等级生成不同风格的支持性回复
- 使用 Git 本地管理代码
- 同步项目到 GitHub 仓库
- 构建打分模型
- 注入mental health skill


## 3. 系统架构

```
用户输入 (文本 + 可选音频)
       │
       ▼
┌─────────────────────────────────┐
│        Pipeline Service         │
│  (LangChain LCEL chain)         │
│                                 │
│  ┌───────────────────────────┐  │
│  │    Scoring Engine          │  │
│  │  ┌─────────────────────┐  │  │
│  │  │ 高危关键词硬拦截     │  │  │
│  │  │ (不想活/自杀/想死等) │  │  │
│  │  └─────────────────────┘  │  │
│  │           │ (未命中)       │  │
│  │           ▼               │  │
│  │  ┌─────────────────────┐  │  │
│  │  │ UnifiedDepression    │  │  │
│  │  │ Engine               │  │  │
│  │  │                      │  │  │
│  │  │ V1: 纯文本 RF 模型   │  │  │
│  │  │  (8维Qwen特征提取)   │  │  │
│  │  │                      │  │  │
│  │  │ V2: 多模态 RF 模型   │  │  │
│  │  │  (8维文本+17维音频)  │  │  │
│  │  └─────────────────────┘  │  │
│  │           │               │  │
│  │           ▼               │  │
│  │   risk_level / score      │  │
│  └───────────────────────────┘  │
│              │                  │
│              ▼                  │
│  ┌───────────────────────────┐  │
│  │  LLM Service (Ollama)     │  │
│  │  根据风险等级生成回复     │  │
│  │  low / medium / high      │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
       │
       ▼
   ChatResponse
   (reply, risk_level, score, evidence)
```

## 4. 项目结构

```text
healing-score-agent/
├── app/
│   ├── main.py                     # FastAPI 应用入口
│   ├── api/
│   │   ├── routes_chat.py          # POST /chat/message
│   │   ├── routes_health.py        # GET /health
│   │   └── routes_admin.py         # 管理接口（预留）
│   ├── core/
│   │   ├── config.py               # 配置管理（环境变量 + pydantic）
│   │   ├── logger.py               # 日志
│   │   └── safety.py               # 高危关键词检测
│   ├── models/
│   │   ├── schemas.py              # Pydantic 请求/响应模型
│   │   ├── scoring_engine.py       # 双模型自适应打分引擎
│   │   └── database.py             # SQLAlchemy 数据库模型
│   ├── services/
│   │   ├── pipeline_service.py     # LangChain LCEL 流程编排
│   │   ├── scoring_service.py      # 评分引擎封装
│   │   ├── llm_service.py          # Ollama LLM 评分 + 回复生成
│   │   ├── memory_service.py       # 对话记忆服务
│   │   └── crisis_service.py       # 危机干预服务
│   ├── prompts/
│   │   ├── SKILL.md                # 心理健康助手角色定义
│   │   ├── supportive_reply.txt    # 支持性回复 prompt 模板
│   │   ├── risk_assessment.txt     # 风险评估 prompt 模板
│   │   └── crisis_reply.txt        # 危机回复 prompt 模板
│   ├── repos/
│   │   └── conversation_repo.py    # 对话数据访问层
│   └── utils/
│       ├── text_clean.py           # 文本清洗
│       └── json_parser.py          # LLM 输出 JSON 解析
├── tests/
│   ├── conftest.py                 # 测试配置
│   ├── test_api.py                 # API 接口测试
│   ├── test_scoring.py             # 评分模块测试
│   └── test_pipeline.py            # Pipeline 集成测试
├── scripts/
│   ├── init_db.py                  # 数据库初始化
│   └── demo_client.py              # 演示客户端
├── docs/
│   ├── api_spec.md
│   ├── architecture.md
│   ├── deployment.md
│   └── roadmap.md
├── .env.example
├── requirements.txt
└── pyproject.toml
```

## 5. 评分系统

### 5.1 双层安全机制

1. **高危关键词硬拦截**：命中 "不想活"、"自杀"、"想死" 等关键词 → 直接判定 `high` / 95分
2. **ML 模型评分**：由 `UnifiedDepressionEngine` 进行精细化评估

### 5.2双模型自适应路由

| 模型 | 输入 | 特征维度 | 路由条件 |
|------|------|----------|----------|
| V1 (纯文本) | 仅文本 | 8维语义特征（Qwen提取） | 仅传入文本 |
| V2 (多模态) | 文本 + 音频 | 8维文本 + 17维声学特征（librosa） | 传入音频路径 |

文本8维特征：anhedonia / depressed / sleep / fatigue / appetite / guilt / concentrate / movement（0-3分制）

音频17维特征：基频均值/标准差 + 能量均值/标准差 + MFCC 1-13均值

### 5.3 风险等级划分

| SDS 分数 | 风险等级 |
|-----------|----------|
| ≥ 73 | 重度 (high) |
| 63-72 | 中度 (medium) |
| 53-62 | 轻度 (low) |
| < 53 | 正常 (low) |

## 6. 配置

通过 `.env` 文件或环境变量配置：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `APP_ENV` | `dev` | 运行环境 |
| `HOST` | `127.0.0.1` | 服务地址 |
| `PORT` | `8000` | 服务端口 |
| `DATABASE_URL` | `sqlite:///./data/app.db` | 数据库连接 |
| `LLM_PROVIDER` | `ollama` | LLM 提供商 |
| `LLM_MODEL` | `qwen2.5:1.5b` | LLM 模型名 |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama 服务地址 |
| `LOG_LEVEL` | `INFO` | 日志级别 |

