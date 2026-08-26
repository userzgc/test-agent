# 自定义智能体 Subagent（Qoder IDE）

> 来源：https://docs.qoder.com/zh/extensions/subagent
> **完整指南在 CLI 文档下**：https://docs.qoder.com/zh/cli/subagent

## 是什么

专门处理特定任务的 AI Agent。**每个智能体拥有独立的上下文窗口、工具权限和系统提示词。**
目前调度方式是通过 subagent 机制管理。

## 存放位置

| 位置 | 路径 | 作用域 |
|------|------|--------|
| 用户级 | `~/.qoder/agents/<agentName>.md` | 所有项目 |
| 项目级 | `${project}/.qoder/agents/<agentName>.md` | 仅当前项目 |

⚠️ **是单个 `.md` 文件，不是目录**。（Kiro 是 `agents/{域}/sub_agents/*.md`，Trae 是 `agents/{name}/agent.md`，都不兼容。）

## 文件格式

```markdown
---
name: code-review
description: 代码审查专家，检查代码质量和安全性
tools: Read, Grep, Glob, Bash
model: "[ModelName](modelId)"
skills:
 - {skillName1}
 - {skillName2}
mcpServers:
 - {mcpServerName1}
 - {mcpServerName2}
---

你是一位资深代码审查员，负责确保代码质量。

审查清单：
1. 代码可读性
2. 命名规范
...
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `name` | **是** | 唯一标识名称 |
| `description` | **是** | 简短描述功能和专长，**用于模型自动选择** |
| `model` | 否 | 指定运行模型，不设置时跟随对话中的模型选择 |
| `tools` | 否 | 允许使用的工具列表，逗号分隔 |
| `skills` | 否 | 允许的技能列表 |
| `mcpServers` | 否 | 允许的 MCP 服务列表 |

## 可用工具列表（8 个）

| 工具 | 说明 |
|------|------|
| `Bash` | 执行 shell 命令 |
| `Edit` | 对特定文件做有针对性的编辑 |
| `Write` | 创建或覆盖文件 |
| `Glob` | 检索文件 |
| `Grep` | 检索文件内容 |
| `Read` | 读取文件内容 |
| `WebFetch` | 从指定 URL 获取内容 |
| `WebSearch` | 带域过滤的 Web 搜索 |

## 触发方式

1. **自动触发**：自然语言描述任务，**模型根据 `description` 自动识别意图并选择智能体**
   例：「帮我审查这个接口的实现」→ 自动调用 `code-review`
2. **手动触发**：`/agent-name`，例 `/code-review`

## 创建方式

### 推荐：内置 `/create-agent`

```
/create-agent <您的诉求，例如代码审查专家>
```

引导完成：定义名称和描述 → 选择工具权限 → 生成系统提示词模板 → 保存到正确位置。

### 手动创建

按上面格式在两个路径之一建 `.md` 文件。

## 模型配置

Quest 视图 → **Setting → Agents** → 选择目标智能体 → **Change Model**，
可为不同角色的智能体分配最合适的模型。

## 关键差异：路由不再需要手写注册表

Kiro 时代需要手写 `multi-agent-orchestration.md` 维护「Agent 注册表 + 意图关键词路由表」。
**Qoder 的路由是框架原生的**——写好 `description` 即可被模型自动选中，
手写路由表在 Qoder 下是冗余设计。
