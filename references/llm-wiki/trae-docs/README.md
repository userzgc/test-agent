# Trae IDE 官方文档知识库

> 来源：https://docs.trae.cn/ 及 https://docs.trae.ai/ （2026-08 整理）
> 用途：让 test-agent 的 AI 了解 Trae 能力，正确使用 IDE 提供的机制

## 文档结构

| 文件 | 内容 | 官方链接 |
|------|------|---------|
| [01-overview.md](./01-overview.md) | Trae IDE 概览、版本、模式 | https://docs.trae.cn/ide/what-is-trae |
| [02-agents.md](./02-agents.md) | 智能体（Agent）机制、自定义、内置 | https://docs.trae.cn/ide/agent |
| [03-skills.md](./03-skills.md) | 技能（Skill）SKILL.md 格式 | https://docs.trae.cn/ide/skills |
| [04-rules.md](./04-rules.md) | 规则（Rules）配置、路径生效 | https://docs.trae.cn/ide/rules |
| [05-hooks.md](./05-hooks.md) | Hook 机制、事件、配置 | https://docs.trae.cn/ide_automate-actions-with-hooks |
| [06-mcp.md](./06-mcp.md) | MCP Server 配置与使用 | https://docs.trae.cn/ide/model-context-protocol |
| [07-context.md](./07-context.md) | 上下文（@引用、#引用、文档集） | https://docs.trae.cn/ide/context |
| [08-cue.md](./08-cue.md) | CUE 智能编程助手 | https://docs.trae.cn/ide/cue |
| [09-solo.md](./09-solo.md) | SOLO 模式 / SOLO Coder | https://docs.trae.cn/ide/solo |
| [10-config-layout.md](./10-config-layout.md) | `.trae/` 目录结构、作用域、优先级 | （社区整理 + 官方） |
| [11-enterprise.md](./11-enterprise.md) | 企业版能力（Hook/智能体/文档集/MCP） | https://www.volcengine.com/docs/86677/2558676 |

## 快速导航

### 我要做什么 → 看哪个文件
- **创建自定义 Agent** → 02-agents.md
- **写 SKILL.md** → 03-skills.md
- **配置项目规则** → 04-rules.md
- **配置自动化 Hook** → 05-hooks.md
- **接入 MCP 工具** → 06-mcp.md
- **引用文件/代码/网页作为上下文** → 07-context.md
- **代码补全/智能重命名** → 08-cue.md
- **AI 主导全流程开发** → 09-solo.md
- **`.trae/` 目录下放什么** → 10-config-layout.md
- **企业版有什么** → 11-enterprise.md

## Trae 核心能力速查

| 能力 | 机制 | 配置位置 |
|------|------|---------|
| 自定义智能体 | `.trae/agents/<name>/agent.md` | 项目 `.trae/agents/` |
| 技能 | `.trae/skills/<name>/SKILL.md` | 项目 `.trae/skills/` 或 `~/.trae/skills/` |
| 规则 | `.trae/rules/*.md` | 项目 `.trae/rules/` |
| Hook | `.trae/hooks.json` + `.trae/hooks/*.sh` | 项目根 `.trae/` |
| MCP Server | `.trae/mcp.json` | 项目 `.trae/` |
| 上下文引用 | `@agent` / `#file` / `#docs` | 对话框 |
| CUE 补全 | 自动激活 | 编辑器内 |
| 文档集 | 上传文档作为上下文 | IDE 设置 |
