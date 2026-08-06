# 多 Agent 协作规则

## 路由规则

根据用户意图自动路由到对应 Agent：

| 意图关键词 | 路由 Agent | 说明 |
|-----------|-----------|------|
| 需求分析、需求理解、梳理需求、对齐 | `requirements` | 需求分析 Agent |
| 写用例、编写用例、生成用例 | `case-writing` | 用例编写 Agent |
| 评审用例、review用例、检查用例 | `case-review` | 用例评审 Agent |
| 执行测试、跑用例、测试执行 | `execution` | 测试执行 Agent |
| Confluence、飞书、YAPI、蓝湖 | `utils` | 工具 Agent |

## 协作流程

```
用户需求
  │
  ▼
requirements（需求分析）
  │  输出：需求理解文档 + 待确认问题
  │
  ▼  用户确认
  │
case-writing（用例编写）
  │  输出：XMind/JSON 用例
  │
  ▼  用户 review
  │
case-review（用例评审）
  │  输出：评审报告 + 修改建议
  │
  ▼  修改后
  │
execution（测试执行）
  │  输出：测试报告
```

## 约束

- 每个 Agent 只做自己的职责，不越界
- Agent 间通过 `docs/` 目录下的文件传递信息
- 所有中间产物保存在 `docs/` 对应子目录

## 自改进机制

每次完成任务后，按 `.trae/steering/self-improvement.md` 检查是否需要：
1. 记录踩坑到 `docs/lessons-learned.md`
2. 更新 `references/llm-wiki/wiki/` 知识页面
3. 更新 `.trae/agents/*/agent.md` 或 `.trae/skills/*/SKILL.md`
4. 新增/修改 `.trae/scripts/` 脚本

详见 `self-improvement.md`。
