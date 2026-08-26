# 子代理 Subagent（Qoder CLI，权威版）

> 来源：https://docs.qoder.com/zh/cli/subagent
> ⚠️ **本篇远比 `ide/03-subagent.md` 完整**：IDE 页面只列了 6 个 frontmatter 字段，
> CLI 页面列了 **18 个**，且包含 `permissionMode`、`isolation`、`hooks`、`maxTurns` 等
> 「安全边界 / 运行上限」类字段——这些正是本项目做多 Agent 编排真正需要的。

## 存放位置与优先级

同名定义按优先级覆盖，**从低到高**：

| 优先级 | 来源 | 入口 |
|---|---|---|
| 1 | Built-in | `/agents` 的 `BuiltIn` 标签页，不可直接编辑 |
| 2 | **User** | `~/.qoder/agents/*.md` |
| 3 | **Project** | `.qoder/agents/*.md`（受文件夹信任状态影响） |
| 4 | Plugin | 已安装插件提供 |
| 5 | Flag | `--agents` JSON，仅本次进程 |

⚠️ **注意：Subagent 是 Project > User，而 Skills 是 User > Project（相反！）** 见 `cli/01-skills.md`。

被覆盖的定义在 `qoder agents list` 中标记为 `shadowed`。

**文件名不决定 Subagent 名称，实际名称来自 frontmatter 的 `name` 字段。**

## 内置 Subagent

| 名称 | 能力 |
|---|---|
| `general-purpose` | 通用研究型。复杂搜索、多文件分析、调用链追踪。**未显式指定类型时默认用它** |
| `Explore` | 快速只读代码探索。继承可用工具后移除写入/控制类工具 |
| `Plan` | 只读方案设计。改代码前梳理实现路径、关键文件、依赖顺序 |
| `qoder-guide` | 非 SDK 模式下出现。回答 Qoder 使用/配置/Skills/Agents/MCP/Hooks 问题 |
| `statusline-setup` | TUI 模式下出现。配置自定义 status line |

内置不可编辑。要定制就创建同名自定义 Subagent 用优先级覆盖。

## ⭐ Frontmatter 全字段表（18 个）

未识别字段会被忽略。

| 字段 | 必需 | 可取值 | 含义 |
|---|:-:|---|---|
| `name` | **是** | 非空字符串 | 名称，便于自然语言引用 |
| `description` | **是** | 非空字符串 | 用途说明，**用于调度判断何时调用** |
| `background` | 否 | 布尔 | 是否默认后台运行（需版本启用后台能力） |
| `color` | 否 | `red`/`blue`/`green`/`yellow`/`purple`/`orange`/`pink`/`cyan` | TUI 展示颜色 |
| `disallowedTools` | 否 | 字符串或数组 | 工具黑名单，在注册后移除 |
| `effort` | 否 | `low`/`medium`/`high`/`xhigh`/`max` 或正整数 | 推理强度/预算 |
| `hooks` | 否 | Hook 配置对象 | **仅作用于该 Subagent 会话的 hooks** |
| `initialPrompt` | 否 | 字符串 | 仅当通过 `--agent` 作为主 Agent 时作为初始提示 |
| `isolation` | 否 | 推荐 `worktree` | `worktree` 让它在独立 git worktree 中运行 |
| `kind` | 否 | `local` | 当前仅支持本地 |
| `maxTurns` | 否 | 正整数 | 单次调用最大对话轮次 |
| `mcpServers` | 否 | 服务名数组 / 内联对象 | 为该 Subagent 额外发现 MCP 工具 |
| `memory` | 否 | `user`/`project`/`local` | 持久记忆作用域（需全局自动记忆已启用） |
| `model` | 否 | 模型名或 `inherit`/`auto`/`lite`/`efficient`/`performance` | 省略时为 `inherit` |
| `permissionMode` | 否 | 见下表 | 权限模式，未声明时继承父会话 |
| `skills` | 否 | 字符串或数组 | 限制该 Subagent 可用的 Skills |
| `temperature` | 否 | 数字 | 模型温度 |
| `timeoutMins` | 否 | 正整数 | 单次调用最长执行分钟数 |
| `tools` | 否 | 字符串或数组；支持 `*` | 工具白名单。省略时用当前可用集合 |

### 完整示例

```markdown
---
name: api-reviewer
description: Review API designs, endpoint naming, request methods, status codes, error responses, and versioning.
tools: [Read, Grep, Glob]
disallowedTools: [Write, Edit]
permissionMode: default
model: inherit
maxTurns: 8
timeoutMins: 10
color: cyan
---

You are an API design reviewer.
Focus on: Resource naming / Request method semantics / Status code consistency / Pagination & versioning
Return concise findings grouped by severity.
```

## 工具配置

三种写法等价：`tools: Read,Grep,Glob` / `tools: [Read, Grep, Glob]` / YAML 列表。

常用工具名：`Read`、`Grep`、`Glob`、`Bash`、`Write`、`Edit`、`WebFetch`、`WebSearch`、`Agent`。

MCP 工具用完全限定名，支持通配：
```yaml
tools:
  - mcp__docs__search
  - mcp__docs__*
  - mcp__*
```

### 限制二次调度（重要）

```yaml
tools:
  - Agent(Explore, Plan)      # 只允许继续调用这两个 Subagent
```
```yaml
disallowedTools: [Agent]      # 完全禁止继续调度
```

**处理顺序**：先按 `tools` 注册，再按 `disallowedTools` 移除。
MCP 工具必须**先被 `mcpServers` 或全局配置发现，再被 `tools` 放行**——只写 `mcpServers` 不等于自动授权。

## MCP 配置

引用已有服务：
```yaml
mcpServers:
  - docs
```

内联定义（仅该 Subagent 可用）：
```yaml
mcpServers:
  docs:
    command: ./scripts/docs-mcp
    args: ["--stdio"]
    include_tools: ["search", "read"]
```

内联字段：`command`、`args`、`env`、`cwd`、`url`/`http_url`、`headers`、`tcp`、
`type`（`sse`/`http`）、`timeout`、`trust`、`description`、`include_tools`、`exclude_tools`。

## ⭐ Subagent 级 Hooks（支持 prompt / agent 类型！）

写在 frontmatter 的 `hooks` **只对该 Subagent 会话生效**。
支持事件：`PreToolUse`、`PostToolUse`、`PostToolUseFailure`、`Stop`、`SubagentStart`、`SubagentStop`、`Notification`。

⚠️ **Subagent 中的 `Stop` 会映射为 `SubagentStop`**——在该 Subagent 完成时触发，不是主会话结束时。

不支持字符串简写，每个事件的值必须是 matcher 数组：

```yaml
hooks:
  PreToolUse:
    - matcher: Bash
      hooks:
        - type: command
          command: ./scripts/check-subagent-command.sh
          timeout: 30
          statusMessage: Checking command
  Stop:
    - hooks:
        - type: command
          command: ./scripts/subagent-finished.sh
```

| `type` | 必需字段 | 说明 |
|---|---|---|
| `command` | `command` | 执行本地命令。可选 `shell`、`timeout`、`if`、`statusMessage` |
| `http` | `url` | 调 HTTP endpoint。可选 `headers`、`allowedEnvVars`、`timeout`、`if`、`statusMessage` |
| **`prompt`** | `prompt` | **用提示词跑一次模型判断**。可选 `model`、`timeout`、`if`、`statusMessage` |
| **`agent`** | `prompt` | **用独立 Hook Agent 执行判断**。可选 `model`、`timeout`、`if`、`statusMessage` |

> ⭐ 这一条推翻了 `ide/04-hooks.md` 里记的「只支持 command 和 http」。
> `prompt` / `agent` 类型在 **CLI + Subagent frontmatter** 层面**已经可用**。

`once` 字段在普通 Subagent frontmatter 中**不保留一次性语义**，需要一次性行为要自己在命令或外部状态里控制。

## permissionMode

| 值 | 含义 |
|---|---|
| `default` | 默认策略，需要确认时询问 |
| `acceptEdits` | 自动接受编辑类操作 |
| `bypassPermissions` | 跳过权限确认。安全策略禁用时降级为 `acceptEdits` |
| `dontAsk` | 不主动询问；需要询问的操作被**拒绝** |
| `auto` | 自动判断策略 |
| `plan` | 开启该 Subagent 自己的计划状态，适合只读规划 |

注意：
- 未声明时**继承父会话当前模式**
- 父会话已在 `acceptEdits`/`bypassPermissions`/`auto` 时，**Subagent 不能把权限降得更严格**
- `plan` 不污染主会话计划状态
- `yolo` 被兼容解析为 `bypassPermissions`，但公开配置应直接写 `bypassPermissions`

## 调用方式

| 方式 | TUI | Headless |
|---|---|---|
| 显式 | `使用 api-reviewer subagent 审查这个接口设计` 或 `@api-reviewer ...` | `qoder -p "使用 api-reviewer subagent ..."` |
| 隐式 | `帮我做一次接口设计审查`（按 `description` 匹配） | `qoder -p "帮我做一次接口设计审查"` |
| 作为主 Agent | `qoder --agent api-reviewer` | `qoder --agent api-reviewer -p "..."` |
| 编排多个 | `先使用 general-purpose subagent 检查实现方案，再使用 api-reviewer subagent 审查 API 设计` | 同上 + `--max-turns 10` |

> 必须被使用的 Subagent，**用显式方式调用**。
> `--max-turns` 限制整次 Headless 查询；限制单个 Subagent 要在其配置里写 `maxTurns`。

独立任务可并发调度；有依赖关系就在提示中说明先后顺序。

## `settings.json` 覆盖（不能新建，只能覆盖已发现的同名）

```json
{
  "agents": {
    "overrides": {
      "api-reviewer": {
        "enabled": true,
        "tools": ["Read", "Grep", "Glob"],
        "runConfig": { "maxTurns": 6, "maxTimeMinutes": 10 },
        "modelConfig": { "model": "auto", "generateContentConfig": { "temperature": 0.2 } },
        "mcpServers": { "docs": { "command": "./scripts/docs-mcp", "args": ["--stdio"] } }
      }
    }
  }
}
```

常见用途：`"enabled": false` 临时隐藏、单独调模型和温度、限制轮次/时长、收紧工具集合、追加 MCP。

⚠️ **插件提供的 Subagent 会被应用额外安全策略**：`hooks`、`mcpServers`、`permissionMode`
会被**移除**，`isolation` 只保留 `worktree`。所以打包成 Plugin 分发时不要依赖这些字段。

## 临时注入 `--agents`

```bash
qoder --agents '{"api-reviewer":{"description":"Review API designs","prompt":"You are an API reviewer.","tools":["Read","Grep","Glob"],"maxTurns":6}}' \
  -p "使用 api-reviewer subagent 审查 docs/api.yaml"
```

用 `prompt` 字段作系统提示词。JSON schema 支持：`description`、`prompt`、`tools`、
`disallowedTools`、`mcpServers`、`model`、`effort`、`color`、`maxTurns`、`initialPrompt`、
`skills`、`permissionMode`。
**需要 `timeoutMins`、`temperature`、`hooks`、`memory`、`background`、`isolation` 时必须用 Markdown 配置。**

## 验证清单

1. `/agents reload` 或重开会话
2. `/agents` 或 `qoder agents list` 确认出现在预期来源下
3. 检查 `description` 是否具体说明了何时调用
4. 用显式名称调用一次
5. 配了只读工具就故意要求它改文件，确认没有写入
6. 配了 `disallowedTools` 就试着触发被禁能力
7. 配了 MCP 就确认 `tools` 没把它挡掉
8. 配了 `background` 就确认启动结果立即返回

## 最佳实践

- 一个 Subagent 只承担一种清晰职责
- `description` 写给调度用，正文提示词写给它自己用，**两者都要具体**
- **默认先给只读工具**，需要写入时再加 `Edit`/`Write`/`Bash`
- 高风险 Subagent 必设 `maxTurns`、`timeoutMins`、明确的 `permissionMode`
- 需要独立改动用 `isolation: worktree`，返回后检查 worktree 路径和实际 diff
- 项目级适合提交版本控制，用户级适合个人偏好

## 🔁 与当前项目 `.trae/agents/` 的差距

| | 当前项目（Kiro 血统） | Qoder |
|---|---|---|
| 文件布局 | `agents/{name}/agent.md` + `sub_agents/` 子目录 | **单文件 `.qoder/agents/{name}.md`** |
| 路由 | 手写 `multi-agent-orchestration.md` 意图关键词表 | **框架原生按 `description` 调度** |
| 工具边界 | 无声明 | `tools` / `disallowedTools` / `permissionMode` |
| 运行上限 | 无 | `maxTurns` / `timeoutMins` |
| 隔离 | 无 | `isolation: worktree` |

6 个 agent 迁移**不是改目录名**，而是「合并成单文件 + 补 frontmatter + 删掉手写路由表」。
