# Hooks 使用指南（Qoder CLI）—— 4 种类型 + 26 事件完整规格

> 来源：https://docs.qoder.com/zh/cli/hooks （997 行，已完整读取）
> 与 `05-hooks-reference.md` 互补：那篇是速查表，这篇是**可直接抄用的完整字段规格**。
> ⚠️ 本篇内容**推翻 `ide/04-hooks.md`** 的「12 事件 / 2 类型」说法。

## 配置文件位置（三个来源**合并执行**，不互相覆盖）

```
~/.qoder/settings.json                    # 用户级，对所有项目生效
${project}/.qoder/settings.json           # 项目级，可提交 git 共享给团队
${project}/.qoder/settings.local.json     # 项目级本地，建议加 .gitignore
```

## 配置结构

```json
{
  "hooks": {
    "事件名": [
      {
        "matcher": "匹配条件",
        "async": false,
        "hooks": [
          { "type": "command", "command": "要执行的命令", "timeout": 600 }
        ]
      }
    ]
  }
}
```

**分组（HookDefinition）字段**

| 字段 | 必填 | 说明 |
|---|---|---|
| `matcher` | 否 | 匹配条件，不填则匹配所有 |
| `hooks` | 是 | 该分组下的 hook 条目数组 |
| `async` | 否 | `true` 时该组全部后台执行，不阻塞当前操作；结果在**下一轮模型对话**中作为附加上下文注入 |

## 四种 Hook 条目类型

### ① `command` — 执行 shell 命令（13 个字段）

| 字段 | 必填 | 说明 |
|---|---|---|
| `command` | 是 | 要执行的 shell 命令 |
| `timeout` | 否 | 秒，默认 **600** |
| `shell` | 否 | `"bash"` / `"powershell"`；不填用系统默认 |
| `env` | 否 | 额外环境变量，与系统环境合并 |
| `if` | 否 | 条件过滤，`"ToolName"` 或 `"ToolName(arg_pattern)"` |
| `async` | 否 | 该条单独后台执行，**覆盖分组级 `async`** |
| `asyncRewake` | 否 | 后台执行；**若 exit 2，用 stderr/stdout 生成系统提醒并唤醒模型继续处理**，常用于长耗时检查 |
| `rewakeMessage` | 否 | 配合 `asyncRewake`，覆盖注入消息前缀 |
| `rewakeSummary` | 否 | 配合 `asyncRewake`，覆盖一行摘要（≤300 字符） |
| `once` | 否 | 首次成功执行后从注册表移除，**仅对会话级 hook 生效** |
| `statusMessage` | 否 | 自定义状态行/spinner 显示的描述 |
| `args` | 否 | argv 数组。设置后走 **exec 形态**（不经 shell） |

#### 占位符引用规范

`${QODER_PROJECT_DIR}` 等作为**环境变量**注入子进程。bash 下 CLI **不预先替换**，由 shell 运行时展开：

| 写法 | 评价 |
|---|---|
| `"${QODER_PLUGIN_ROOT}"/scripts/hook.sh` | ✅ 推荐。路径含空格或 `'`、`$`、反引号也能正确解析为单个 token |
| `"$QODER_PLUGIN_ROOT/scripts/hook.sh"` | ✅ 与上等价 |
| `${QODER_PLUGIN_ROOT}/scripts/hook.sh` | ❌ 不推荐。未引用参数展开会做单词拆分与路径名展开，含空格被拆、含 `*` 被通配展开 |

PowerShell 下 `${QODER_PROJECT_DIR}` / `${QODER_PLUGIN_ROOT}` / `${QODER_PLUGIN_DATA}` 由 CLI 在调用前**替换进命令模板**（PowerShell 用 `$env:NAME` 语法）。

#### Exec form vs Shell form

- **Shell 形态（默认）**：`command` 是 shell 代码片段，走 `bash -c`。支持管道、重定向、glob、`${VAR}` 展开。
- **Exec 形态（设置 `args` 时）**：`command` 是单个可执行文件路径，`args` 每项是**字面** argv 元素。直接调二进制，**不做引号处理、单词拆分或 glob 展开**。设置 `args` 时 `shell` 字段被忽略。

```json
{
  "type": "command",
  "command": "/usr/bin/python3",
  "args": ["${QODER_PLUGIN_ROOT}/scripts/check.py", "--strict"]
}
```

选择依据：需要管道/重定向/glob → shell 形态；路径或参数含 shell 元字符、想完全避免 shell 解析不确定性 → exec 形态。

Windows 注意：`.bat`/`.cmd` 无法直接 exec，要写 `{"command": "cmd.exe", "args": ["/c", "script.bat"]}`。

### ② `http` — POST 到 URL

| 字段 | 必填 | 说明 |
|---|---|---|
| `url` | 是 | 接收 POST 的 URL |
| `headers` | 否 | 值支持 `${ENV_VAR}` 插值 |
| `allowedEnvVars` | 否 | 限制 `headers` 可插值的环境变量白名单；不填允许所有 |
| `timeout` | 否 | 秒，默认 600 |
| `if` / `once` / `statusMessage` | 否 | 同 command |

### ③ `prompt` — 单次模型调用

模型按提示词返回 `{ ok, reason }`：`ok=false` 视为**阻塞**，`reason` 返回给 Agent。

| 字段 | 必填 | 说明 |
|---|---|---|
| `prompt` | 是 | 提示词模板，**序列化后的事件 JSON 会自动追加在其后** |
| `model` | 否 | 覆盖模型（如 `haiku`），不填用会话默认 |
| `timeout` | 否 | 秒，默认 **30** |
| `if` / `once` / `statusMessage` | 否 | 同 command |

> ⚠️ **独立评估**：评估模型在独立会话运行，**只收到你的 `prompt` 与当前事件数据，看不到主对话**的工具调用、模型输出或任何历史。依赖会话历史的规则无法可靠评估 → 改用维护自身状态的 `command`，或可访问文件系统的 `agent`。

### ④ `agent` — 子 Agent 校验

子 Agent 必须调用 **`StructuredOutput`** 工具返回 `{ ok: boolean, reason?: string }`。

| 字段 | 必填 | 说明 |
|---|---|---|
| `prompt` | 是 | 校验提示词，支持 **`$ARGUMENTS`** 占位符（自动替换为 hook 输入 JSON） |
| `tools` | 否 | 工具白名单。不填继承全部，但自动过滤不适合 hook 的工具（递归 Agent、计划模式、交互提问等） |
| `maxTurns` | 否 | 默认 **50** |
| `model` | 否 | 覆盖模型 |
| `timeout` | 否 | 秒，默认 **60** |
| `if` / `once` / `statusMessage` | 否 | 同 command |

> 与 `prompt` 同样看不到主对话历史，**区别是它能用工具检查工作目录与运行检查**，适合需要核查真实状态（读文件、跑校验）的场景。
> ⭐ 这是本项目「XMind 产出物结构校验」最合适的载体。

## `matcher`（分组级）与 `if`（条目级）匹配规则

`matcher` 匹配的字段**因事件而异**（工具名、trigger、来源等）：

| 写法 | 含义 | 示例 |
|---|---|---|
| 不填或 `"*"` | 匹配所有 | 所有工具都触发 |
| 精确值 | 精确匹配 | `"Bash"` |
| `\|` 分隔 | 多值 | `"Write\|Edit"` |
| 正则 | **matcher 支持正则** | `"mcp__.*"` |

`if`（条目级）格式 `"ToolName"` 或 `"ToolName(arg_pattern)"`，
⚠️ **括号内走 glob 通配匹配，不是正则**：`"Bash(git *)"`、`"Edit(*.ts)"`。

## Hook 脚本协议

- **输入**：stdin 收到 JSON
- **退出码**：`0` 正常；`2` 阻塞（仅部分事件支持，见事件清单）；其他非零视为失败
- **stdout**：可返回 JSON 精确控制行为

### stdout JSON 通用字段

| 字段 | 说明 |
|---|---|
| `continue` | 是否继续 |
| `stopReason` | 停止原因 |
| `suppressOutput` | 抑制输出展示 |
| `systemMessage` | 注入系统消息 |
| `decision` | `"allow"` / `"deny"`，`deny` 等价于 exit 2 |
| `reason` | 决策原因 |
| `hookSpecificOutput` | 事件专属输出 |

> ⚠️ **输出 `hookSpecificOutput` 时必须带上 `hookEventName`，否则整个 JSON 输出会被拒绝。**

### 环境变量

| 变量 | 说明 |
|---|---|
| `QODER_PROJECT_DIR` | 项目根目录 |
| `QODER_PLUGIN_ROOT` | 插件根目录（仅 plugin hook） |
| `QODER_PLUGIN_DATA` | 插件数据目录（仅 plugin hook） |

## 事件清单总览（26 个）

| 事件 | matcher 匹配 | exit 2 阻塞 | 关键输入字段 |
|---|---|---|---|
| `SessionStart` | `source` | — | `source`, `model` |
| `SessionEnd` | `reason` | — | `reason` |
| `UserPromptSubmit` | — | ✅ | `prompt` |
| `PreToolUse` | 工具名 | ✅ | `tool_name`, `tool_input`, `tool_use_id` |
| `PostToolUse` | 工具名 | — | `tool_name`, `tool_input`, `tool_response` |
| `PostToolUseFailure` | 工具名 | — | `tool_name`, `error`, `error_type`, `is_interrupt` |
| `PermissionRequest` | 工具名 | — | `tool_name`, `tool_input`, `permission_suggestions` |
| `PermissionDenied` | 工具名 | — | `tool_name`, `tool_input`, `reason` |
| `Stop` | — | ✅ | `stop_hook_active`, `last_assistant_message` |
| `StopFailure` | `error_type` | — | `error_type`, `error`, `error_details` |
| `SubagentStart` | Agent 类型 | — | `agent_id`, `agent_type` |
| `SubagentStop` | Agent 类型 | ✅ | `agent_id`, `agent_type`, `stop_hook_active`, `agent_transcript_path` |
| `PreCompact` | `trigger` | ✅ | `trigger`, `custom_instructions` |
| `PostCompact` | `trigger` | — | `trigger`, `compact_summary` |
| `Notification` | `notification_type` | — | `notification_type`, `message`, `title`, `details` |
| `InstructionsLoaded` | `load_reason` | — | `file_path`, `memory_type`, `load_reason`, `globs` |
| `ConfigChange` | `source` | ✅（`policy_settings` 除外） | `source`, `file_path` |
| `CwdChanged` | — | — | `old_cwd`, `new_cwd` |
| `FileChanged` | 文件 basename | — | `file_path`, `event` |
| `WorktreeCreate` | — | 失败：非 0 exit | `name` |
| `WorktreeRemove` | — | — | `worktree_path` |
| `Elicitation` | `mcp_server_name` | ✅ | `mcp_server_name`, `message`, `requested_schema` |
| `ElicitationResult` | `mcp_server_name` | ✅ | `mcp_server_name`, `action`, `content` |

### 各事件 matcher 取值与专属输出

**`SessionStart`** — matcher：`startup` / `resume` / `clear` / `compact` / `new`。
输出 `additionalContext`；**返回纯文本（非 JSON）时 stdout 也会作为上下文注入对话**。

**`SessionEnd`** — matcher：`clear` / `resume` / `logout` / `prompt_input_exit` / `bypass_permissions_disabled` / `other`。

**`UserPromptSubmit`** — exit 2 拒绝该 Prompt，stderr 展示给用户。
输出 `additionalContext`、**`sessionTitle`**（建议的会话标题）。纯文本 stdout 同样注入。

**`PreToolUse`** — MCP 工具额外附带 `mcp_context`（含 `server_name`、`tool_name`、连接信息）和 `original_request_name`。
输出：

| 字段 | 说明 |
|---|---|
| `permissionDecision` | `"allow"`/`"deny"`/`"ask"`，等价顶层 `decision` 但**覆盖优先** |
| `permissionDecisionReason` | 覆盖顶层 `reason` |
| `updatedInput` | **修改后的工具输入参数**（替换原始 `tool_input`） |
| `additionalContext` | 注入对话 |

**`PostToolUse`** — 输出 `updatedToolOutput`（替换工具响应，任意工具）、
`updatedMCPToolOutput`（仅 MCP，优先级低于前者）、`additionalContext`。

**`PermissionRequest`** — 输出 `decision` 对象，字段随 `behavior` 变化：

```json
{ "behavior": "allow", "updatedInput": {}, "updatedPermissions": [] }
{ "behavior": "deny",  "message": "...", "interrupt": false }
```

> ⚠️ `PermissionRequest` **不支持 `"ask"`**；要弹窗征询用户请用 `PreToolUse` 的 `permissionDecision: "ask"`。

**`PermissionDenied`** — 权限分类器拒绝时触发，输出 `retry: true` 可**请求重试**该工具调用。

**`Stop`** — `stop_hook_active` 表示当前是否正处于由 Stop hook 驱动的延续轮次（**用它避免无限循环**）。
exit 2 → stderr 作为消息注入对话，Agent 继续工作。输出 `clearContext: true` 可同时清空上下文。

**`StopFailure`** — 仅通知，输出与 exit code 被忽略。
`error_type`：`rate_limit` / `authentication_failed` / `billing_error` / `invalid_request` / `server_error` / `max_output_tokens` / `unknown`。

**`SubagentStop`** — exit 2 → stderr 注入**子 Agent** 对话。输出 `clearContext`。

**`PreCompact` / `PostCompact`** — matcher：`manual`（`/compact`）/ `auto`（接近上限）。
`PreCompact` exit 2 阻止本次压缩。

**`Notification`** — matcher：`permission_prompt` / `idle_prompt` / `auth_success` /
`elicitation_dialog` / `elicitation_response` / `elicitation_complete`。

**`InstructionsLoaded`** — 仅通知，输出与 exit code 被忽略。
`load_reason`：`session_start` / `nested_traversal` / `path_glob_match` / `include` / `compact`。
⭐ **可用于验证规则/记忆文件是否真被加载**——本项目排查「资产是否生效」的直接手段。

**`ConfigChange`** — matcher：`user_settings` / `project_settings` / `local_settings` /
`policy_settings` / `skills` / `agents`。
exit 2 阻止该变更应用到当前会话；**`policy_settings` 例外**：hook 仍触发用于审计，但变更强制生效不可阻止。

**`CwdChanged` / `FileChanged`** — 输出 `additionalContext` 与 **`watchPaths`**（注册到 `FileChanged` 监听器的绝对路径列表）。
`FileChanged` 的 `event`：`change` / `add` / `unlink`；matcher 匹配 basename，支持精确、`|`、正则。
⭐ **`CwdChanged` 返回 `watchPaths` 是启用 `FileChanged` 的前置动作**——想监听 `docs/test-cases/*.xmind` 必须先注册。

**`WorktreeCreate`** — Hook 必须返回 worktree **绝对路径**（写 stdout 或 `hookSpecificOutput.worktreePath`），任何非零 exit 视为失败。

**`Elicitation`** — exit 2 拒绝。输出 `action`（`"accept"`/`"decline"`/`"cancel"`）、`content`。
**`ElicitationResult`** — exit 2 把 action 改写为 `decline`。输出 `action`、`content` 覆盖原响应。

## 官方三个实用示例

**桌面通知**（`Notification` + `osascript`）：
```bash
#!/bin/bash
input=$(cat)
ntype=$(echo "$input" | jq -r '.notification_type')
if [ "$ntype" = "permission_prompt" ]; then
  osascript -e 'display notification "任务需要授权" with title "Qoder CLI"'
fi
exit 0
```

**写文件后自动 Lint**（`PostToolUse`，matcher `Write|Edit`）：
```bash
#!/bin/bash
input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path')
case "$file_path" in
  *.js|*.ts|*.jsx|*.tsx) npx eslint "$file_path" --fix 2>/dev/null ;;
esac
exit 0
```

**让 Agent 继续工作**（`Stop`）：
```bash
#!/bin/bash
if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
  echo "检测到未提交的变更，请完成 git commit" >&2
  exit 2
fi
exit 0
```

## 🎯 对本项目的可用组合

| 目标 | 事件 + 类型 | 做法 |
|---|---|---|
| 产出物格式校验（XMind 结构、必填字段） | `PostToolUse` + `agent` | 子 Agent 读文件核查真实结构，`ok=false` 阻塞 |
| 禁止在用例目录写 md | `PreToolUse` + `command` | 返回 `permissionDecision: "deny"`，**连 YOLO 都拦得住** |
| 验证规则是否真被加载 | `InstructionsLoaded` + `command` | 记录 `file_path` / `memory_type`，用于自查资产生效情况 |
| 长耗时用例校验不阻塞对话 | `PostToolUse` + `asyncRewake` | 后台跑，exit 2 时唤醒模型来修 |
| 收尾前确认交付物完整 | `Stop` + `command` | 检查 XMind 是否已生成，缺失则 exit 2 让 Agent 继续 |
