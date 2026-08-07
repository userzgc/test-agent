---
inclusion: auto
description: 多 Agent 协作与路由规则，决定用户说的话交给谁处理
---

# 多 Agent 协作规则

## 核心原则

主 Agent 接收所有任务，根据路由规则识别任务归属，加载对应 Agent 指令 + Skill 规范执行。每个 Agent 只做自己的职责，不越界。

**为什么不用单一 Agent 包揽所有事**：上下文窗口有限，职责不清晰，可维护性差，agent 间无法复用。

## Trae 的 sub-agent 落地说明

Trae **没有原生 `invokeSubAgent` API**（不同于 Kiro），无法真正在主 Agent 内部切分上下文给子 agent。当前采用两种模式混合：

| 模式 | 适用场景 | 上下文是否切分 |
|------|---------|--------------|
| 主 Agent 编排（内部加载 agent.md + skill） | 多步工作流（需求→用例→评审） | ❌ 不切分，靠 `docs/` 文件中转减少上下文占用 |
| 用户主动 `@agent-name` 切换 | 单步任务（评审用例、分析设计稿） | ✅ 真正切分，独立窗口 |

### 上下文膨胀兜底

当前作为内部工具，单任务对话量可控（30-50 轮），不主动解决膨胀。触发以下信号时再处理：
- 单任务对话 > 100 轮
- 多人并发使用
- 跨会话/跨天延续

兜底方案：
1. 用户主动 `@agent-name` 切分独立上下文
2. 所有中间产物落 `docs/` 文件，主 Agent 只读摘要
3. 复杂任务拆成多会话，用文件衔接

## MCP Server 化预留

所有可复用脚本（`.trae/scripts/`）保持**独立脚本**形态，不与 Agent 逻辑耦合。未来抽 MCP Server 时只需包一层 stdio/SSE 接口。

- ✅ 正确形态：`gen_xmind.py` / `parse_xmind.py` 独立可执行
- ❌ 错误形态：把脚本逻辑写死在 agent.md 里

未来对外赋能分阶段：
1. **当前（个人工具）**：本地 Agent + Skill + Wiki
2. **中期（团队试用）**：抽 2-3 个核心能力做成 MCP Server（XMind 生成器、用例解析器）
3. **远期（团队推广）**：评估 Web 服务/测试环境部署

## Agent 注册表

| Agent | 指令文件 | 职责 | 输入 | 输出 |
|------|---------|------|------|------|
| requirements | `.trae/agents/requirements/agent.md` | 需求分析 | 需求文档/技术方案/历史用例 | 需求分析文档 + 待确认问题 |
| design-extractor | `.trae/agents/design-extractor/agent.md` | 设计稿提取 | 蓝湖/墨刀/Confluence/飞书链接 | 测试关注点清单 |
| case-writing | `.trae/agents/case-writing/agent.md` | 用例编写 | 需求分析 + 确认结果 | XMind 用例文件 |
| case-review | `.trae/agents/case-review/agent.md` | 用例评审 | XMind 用例 + 需求文档 | 评审报告 + 修改建议 |
| execution | `.trae/agents/execution/agent.md` | 测试执行 | 评审通过的用例 | 执行计划 + 报告 |
| utils | `.trae/agents/utils/agent.md` | 工具对接 | 外部工具链接/ID | 下载到本地的文件 |

## Skill 注册表

| Skill | 文件 | 何时用 |
|------|------|--------|
| requirements-analysis | `requirements-analysis/SKILL.md` | 需求分析时 |
| design-extraction | `design-extraction/SKILL.md` | 提取设计稿/截图时 |
| test-case-writing | `test-case-writing/SKILL.md` | 写用例时（含 XMind 场景树规范） |
| test-case-reviewer | `test-case-reviewer/SKILL.md` | 评审用例时 |
| functional-testing | `functional-testing/SKILL.md` | 设计功能测试方案时 |
| qa-workflow | `qa-workflow/SKILL.md` | 事务式工作流（需求→场景→用例→评审） |
| tool-usage | `tool-usage/SKILL.md` | 调用外部工具/脚本时 |

## 路由决策流程

```
用户消息
  │
  ▼
┌──────────────────────────────────┐
│ 1. 识别意图关键词                 │
│ 2. 匹配 Agent 注册表             │
│ 3. 加载 agent.md 作为指令         │
│ 4. 加载对应 Skill 作为操作规范    │
│ 5. 执行任务                      │
│ 6. 输出结果，回到主 Agent         │
└──────────────────────────────────┘
```

### 意图关键词路由

| 意图关键词 | 路由 Agent | 加载 Skill |
|-----------|-----------|-----------|
| 需求分析、需求理解、梳理需求、对齐 | `requirements` | `requirements-analysis` |
| 设计稿、原型稿、截图识别、蓝湖、墨刀 | `design-extractor` | `design-extraction` |
| 写用例、编写用例、生成用例、冒烟 | `case-writing` | `test-case-writing` |
| 评审用例、review用例、检查用例 | `case-review` | `test-case-reviewer` |
| 执行测试、跑用例、测试执行 | `execution` | `functional-testing` |
| Confluence、飞书、YAPI、脚本调用 | `utils` | `tool-usage` |
| 测试工作流、用例全流程 | 主 Agent 编排 | `qa-workflow` |

### 多意图任务

一个用户消息可能包含多个意图（如"分析需求并写用例"），此时主 Agent 按 qa-workflow 的事务式流程编排：

```
Step 1: requirements agent → 需求分析
Step 2: 用户确认待澄清问题
Step 3: case-writing agent → 写用例
Step 4: case-review agent → 评审
```

每步完成后用 `AskUserQuestion` 推送下一步选项，不要自动连续执行。

## Sub-agent 调用模板

主 Agent 执行子任务时，按以下模板加载 Agent 指令和 Skill：

```
# 执行子任务：<任务名>
# Agent 指令：.trae/agents/<agent-name>/agent.md
# Skill 规范：<skill-name>

## 当前角色
<从 agent.md 读取的角色定义>

## 当前任务
<具体子任务描述>

## 执行步骤
<从 agent.md 读取的工作流>

## 操作规范
<从对应 SKILL.md 加载的规范>
```

### 调用示例

**场景**：用户说"写下买A赠B二期的用例"

```
1. 主 Agent 识别意图：写用例 → case-writing agent
2. 加载 agent.md：
   - 角色：资深测试用例编写专家
   - 输入：需求分析文档、确认结果
   - 输出：XMind 文件
   - 工作流：读需求→参考历史→确认格式→构造→生成→验证
3. 加载 test-case-writing skill：
   - XMind 场景树规范
   - 大场景划分规则
   - 节点编写规则
   - 脚本调用方法
4. 执行任务
5. 输出 XMind 文件 + 下一步建议
```

**场景**：用户说"分析这个设计稿"

```
1. 主 Agent 识别意图：设计稿 → design-extractor agent
2. 加载 agent.md：
   - 角色：工具型 agent，收口视觉类输入
   - 输入：蓝湖/墨刀/Confluence/飞书链接
   - 输出：测试关注点清单
3. 加载 design-extraction skill：
   - 获取策略表
   - 图片分析流程
   - 输出格式
4. 执行任务
5. 输出关注点清单 + 提示下一步
```

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
design-extractor（设计稿提取，可选）
  │  输出：测试关注点清单
  │
  ▼  补充到需求分析
  │
case-writing（用例编写）
  │  输出：XMind 用例
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

## 上下文传递

Agent 间通过 `docs/` 目录下的文件传递信息，不靠对话记忆：

| 阶段 | 输出文件 | 下游读取 |
|------|---------|---------|
| 需求分析 | `docs/requirements/<活动名>_需求分析.md` | case-writing |
| 设计稿提取 | `docs/design-analysis/<页面名>_关注点.md` | case-writing |
| 用例编写 | `docs/test-cases/<活动名>_测试用例.xmind` | case-review |
| 用例评审 | `docs/test-cases/<活动名>_用例评审报告.md` | case-writing（修改） |
| 测试执行 | `docs/reports/<活动名>_执行报告.md` | — |

## 约束

- 每个 Agent 只做自己的职责，不越界
- Agent 间通过 `docs/` 目录下的文件传递信息
- 所有中间产物保存在 `docs/` 对应子目录
- 不要在 Agent 里写可复用的操作规范（那是 Skill 的职责）
- 多步任务每步完成后用 `AskUserQuestion` 推送下一步选项

## 自改进机制

每次完成任务后，按 `.trae/steering/self-improvement.md` 检查是否需要：
1. 记录踩坑到 `docs/lessons-learned.md`
2. 更新 `references/llm-wiki/wiki/` 知识页面
3. 更新 `.trae/agents/*/agent.md` 或 `.trae/skills/*/SKILL.md`
4. 新增/修改 `.trae/scripts/` 脚本
