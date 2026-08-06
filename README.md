# test-agent

测试需求对焦和用例管理项目。

## 项目结构

```
test-agent/
├── .trae/
│   ├── agents/              # Agent 指令
│   │   ├── requirements/     # 需求分析 Agent
│   │   ├── case-writing/     # 用例编写 Agent
│   │   ├── case-review/      # 用例评审 Agent
│   │   ├── execution/        # 测试执行 Agent
│   │   └── utils/            # 工具 Agent（Confluence/飞书/YAPI）
│   ├── hooks/                # 事件驱动的自动化
│   ├── settings/             # 配置（凭据、环境变量）
│   ├── skills/               # 可复用技能
│   └── steering/             # 全局行为约束
├── docs/
│   ├── requirements/         # 需求分析文档
│   ├── test-cases/           # 测试用例
│   └── reports/              # 测试报告
├── references/
│   └── llm-wiki/             # 知识库
│       ├── SCHEMA.md
│       └── wiki/
│           ├── activities/   # 活动知识
│           ├── conventions/  # 测试规范
│           ├── confluence.md
│           ├── feishu.md
│           ├── xmind.md
│           └── yapi.md
└── .gitignore
```

## 工作流

```
需求文档 → requirements(分析) → 用户确认 → case-writing(编写) → case-review(评审) → execution(执行)
```

## 已有资产
- 4个测试技能：requirements-analysis、test-case-writing、test-case-reviewer、functional-testing
- 城市徽章活动用例（v2.xmind）
- 买A赠B一期用例（JSON）
- Confluence/飞书/YAPI 访问配置
