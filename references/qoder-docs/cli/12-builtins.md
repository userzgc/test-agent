# 内置 Agent 与 Skills（Qoder CLI）

> 来源：https://docs.qoder.com/zh/cli/builtins-reference

## 内置 Subagent

| Agent | 用途 | 约束 |
|---|---|---|
| `general-purpose` | 通用 Agent，处理大多数请求与复杂多步任务 | 可用全部工具 |
| `Explore` | 探索 Agent，**只读**检索与理解代码；可指定彻底程度（快速/中等/非常彻底） | 只读，禁写入与状态变更类工具；**使用轻量模型** |
| `Plan` | 计划 Agent，设计实施方案，给出步骤、关键文件与架构取舍 | 只读；**继承当前会话模型** |
| `statusline-setup` | 协助配置状态栏 | 仅交互式界面可用 |
| `qoder-guide` | 回答关于 Qoder CLI 功能与用法的问题 | 仅交互式；只读工具集 |

可通过 `agents.overrides` 覆盖特定 Agent 的模型、工具或运行配置，**也可禁用某个 Agent**。

## 内置 Bundled Skills

通过 `/技能名` 或由 Agent 自动按需调用。

| Skill | 用途 |
|---|---|
| `loop` | **按固定间隔重复执行提示或斜杠命令** |
| `remember` | 评审自动积累的记忆条目，提出晋升到说明文件的建议，**识别过期、冲突和重复的条目**（需启用自动记忆） |
| `run` | 启动并驱动项目的实际应用，观察改动的运行时效果 |
| `run-skill-generator` | 创建或改进项目专属的 `run` 技能 |
| `batch` | **在隔离的 git worktree 中生成并行工作代理**，跨多文件批量改动（需 git 仓库） |
| `debug` | 调试助手 |
| `quest` | **智能工作流编排器，通过专用子代理引导完成功能开发** |
| `verify` | 验证结果是否符合预期 |
| `security-scan` | 云端安全扫描（L2 轻量 / L3 深度评审） |
| `simplify` | 简化代码或流程 |
| `mcp-config` | 管理 MCP 服务器配置 |

## ⚠️ 与本会话实际可用 Skill 的差异

本会话（Qoder IDE）实际可用的 skill 是：
`better-harness` / `canvas` / `create-plugin` / `create-skill` / `create-subagent` / `vercel-deploy`。

**与上表完全不重叠** —— 说明 IDE 与 CLI 的内置 Skill 集是两套。
引用「内置能力」时必须区分入口，不能拿 CLI 文档的清单当 IDE 的现状。

## 🎯 对本项目直接有用的三个

| Skill | 用法 |
|---|---|
| **`batch`** | 批量改多个用例文件（如给 53 条用例统一补字段）时，在隔离 worktree 里并行跑，不互相污染 |
| **`remember`** | 定期跑一次，把散落的自动记忆整理成说明文件，并**清掉过期与冲突项** —— 正好治「lessons-learned.md 越写越乱」 |
| **`verify`** | 用例生成后做「是否符合预期」的独立校验，比让同一个 Agent 自己检查更可靠 |
