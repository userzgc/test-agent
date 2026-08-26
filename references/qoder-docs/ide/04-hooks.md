# Hooks（Qoder IDE）

> ⚠️ **本篇已被 `cli/05-hooks-reference.md` 重大修正**：
> - IDE 文档写 **12 个事件**，CLI 文档写 **26 个**
> - IDE 文档写只支持 `command` / `http`，CLI 文档写支持 **`command` / `http` / `prompt` / `agent`**
> - Subagent frontmatter 里的 `hooks` 也支持 `prompt` / `agent`（见 `cli/02-subagent.md`）
>
> 下面这份仍然有效，作为「IDE 入口确认支持的子集 + 逐事件字段详情」使用。

> 来源：https://docs.qoder.com/zh/extensions/hooks
> 适用：Qoder IDE / JetBrains 插件。**CLI 的 Hooks 另见 /zh/cli/hooks，事件支持范围不同。**
> IDE 与 CLI **共用同一份配置文件**，但各入口只执行自身支持的事件。

## 是什么

在 Agent 执行的关键节点插入自定义逻辑，无需改代码。与 Prompt 指令的本质区别：
**Hooks 是确定性的——只要事件触发，脚本一定执行，不受模型理解偏差影响。**

## 12 个事件

| 事件 | 触发时机 | 可阻断 |
|------|---------|--------|
| `SessionStart` | 会话启动或恢复时 | 否 |
| `UserPromptSubmit` | 用户提交 Prompt 后、Agent 处理前 | **是** |
| `PreToolUse` | 工具调用执行前 | **是** |
| `PermissionRequest` | 工具需要用户授权时 | **是** |
| `PostToolUse` | 工具调用成功后 | 否 |
| `PostToolUseFailure` | 工具调用失败后 | 否 |
| `SubagentStart` | 子代理启动时 | 否 |
| `SubagentStop` | 子代理停止时 | 否 |
| `Stop` | Agent 完成响应时 | **是** |
| `SessionEnd` | 会话结束时 | 否 |
| `PreCompact` | 上下文压缩前 | 否 |
| `Notification` | 发出面向用户的通知时 | 否 |

## 配置文件位置（三级合并，优先级低→高）

| 位置 | 作用域 | 优先级 | 可共享 |
|------|--------|--------|--------|
| `~/.qoder/settings.json` | 用户级 | 1（最低） | 否 |
| `.qoder/settings.json` | 项目级 | 2 | **是（提交 Git，团队共享）** |
| `.qoder/settings.local.json` | 项目级本地 | 3（最高） | 否（gitignore） |

**⚠️ 暂不支持热加载，修改配置后必须重启 IDE 才生效。**

## 配置格式

```json
{
  "hooks": {
    "事件名": [
      {
        "matcher": "匹配条件（可选）",
        "hooks": [
          { "type": "command", "command": "脚本路径" }
        ]
      }
    ]
  }
}
```

| 字段 | 必填 | 说明 |
|------|------|------|
| `type` | 是 | `"command"` 或 `"http"`（**不支持 `prompt` / `agent`**） |
| `command` | 是 | shell 命令或脚本路径 |
| `timeout` | 否 | 超时秒数，默认 30；超时后终止，**按放行处理** |
| `matcher` | 否 | 不填则匹配该事件所有触发 |
| `if` | 否 | 单条 Hook 的细粒度过滤，形如 `"ToolName"` 或 `"ToolName(arg_pattern)"` |
| `async` | 否 | `true` 时后台执行，不阻塞 |
| `asyncRewake` | 否 | `true` 时后台执行并可用结果唤醒模型（适合耗时检查） |
| `statusMessage` | 否 | 运行时状态栏显示的描述 |

### matcher 写法

| 写法 | 含义 |
|------|------|
| 不填 或 `"*"` | 匹配所有 |
| `"Bash"` | 精确匹配 |
| `"Write\|Edit"` | 竖线分隔匹配多个 |
| `"mcp__.*"` | 正则，匹配所有 MCP 工具 |

### 工具名映射（两套名称等价，任选）

| Qoder 原生名 | Claude Code 兼容名 |
|---|---|
| `run_in_terminal` | `Bash` |
| `read_file` | `Read` |
| `create_file` | `Write` |
| `search_replace` | `Edit` |
| `grep_code` | `Grep` |
| `search_file` | `Glob` |
| `list_dir` | `LS` |
| `Agent` | `Task` |
| `search_web` | `WebSearch` |
| `fetch_content` | `WebFetch` |
| `todo_write` | `TodoWrite` |
| `edit_file` / `delete_file` / `get_terminal_output` / `Skill` / `ask_user_question` / `search_memory` / `update_memory` / `switch_mode` / `create_plan` / `run_preview` / `get_problems` / `fetch_rules` / `ImageGen` | 无兼容名 |
| `mcp__<server>__<tool>` | 同左 |

## 脚本协议

**输入**：stdin 收 JSON。通用字段：

| 字段 | 必有 | 说明 |
|------|------|------|
| `session_id` | 是 | 会话 ID |
| `cwd` | 是 | 工作目录 |
| `hook_event_name` | 是 | 事件名 |
| `transcript_path` | 是 | **会话上下文 JSON 文件路径**（可用于复盘分析） |
| `request_set_id` | 否 | IDE 请求轮次 ID |
| `tool_name` / `tool_input` / `tool_response` | 否 | 工具相关事件 |
| `extra.email` / `extra.repo` / `extra.branch` | 否 | Git 信息 |
| `extra.request_time` / `extra.response_time` | 否 | RFC3339 时间 |
| `extra.full_diff_text` | 否 | 本次变更完整 diff（仅编辑类工具的 PostToolUse） |

> 所有字段都应**按可选消费**——即使字段已声明，特定执行路径下也可能不填充。

**输出**：exit code 控制行为

| Exit Code | 行为 |
|-----------|------|
| `0` | 继续执行，**并尝试解析 stdout JSON** |
| `2` | 阻断，stderr 内容注入对话（仅对支持阻断的事件生效） |
| 其他 | 非阻断错误，stderr 显示给用户，继续执行 |

> IDE 对 exit 0 和 exit 2 **都会**尝试解析 stdout JSON——不要假设 exit 2 的 stdout 只当纯文本。

**公共 stdout 顶层字段**：`systemMessage`、`continueWithPrompt`、`decision`（`"block"`）、`reason`、`updatedToolOutput`、`hookSpecificOutput`。

**注入的环境变量**：`QODER_SESSION_ID`、`QODER_TOOL_NAME`、`QODER_CWD`、`QODER_TRANSCRIPT_PATH`、`QODER_TOOL_INPUT_FILE_PATH`。

**前置依赖**：`jq`（示例脚本都用它解析 JSON）；脚本需 `chmod +x`。

## 各事件专属字段

### SessionStart
额外输入：`type`（当前 IDE 传 `"startup"`）、`model`。
输出：`hookSpecificOutput.additionalContext` → 注入启动上下文。

### UserPromptSubmit
额外输入：`prompt`。
exit 2 阻断 Prompt，stderr 反馈给用户，Agent 不处理该 Prompt。
输出：`hookSpecificOutput.additionalContext` → **作为 system-reminder 追加到用户 Prompt 后注入 Agent**。

### PreToolUse
matcher：工具名。额外输入：`tool_name`、`tool_input`。
输出 `hookSpecificOutput`：
- `permissionDecision`：`"allow"` / `"deny"` / `"ask"`
- `permissionDecisionReason`
- `updatedInput`（改写工具调用参数）
- `additionalContext`

### PermissionRequest
matcher：工具名。额外输入：`tool_use_id`。
输出同 PreToolUse（可自动放行/拒绝，免弹窗）。

### PostToolUse
额外输入：`tool_response`（IDE 当前通常为字符串）。
输出：`hookSpecificOutput.feedback` → 展示给用户（如 lint 结果摘要）。

### PostToolUseFailure
matcher：工具名。额外输入：
- `error`（错误信息）
- `is_interrupt`（失败是否由中断导致）
- `tool_use_id`

### Stop
额外输入：
- `stop_hook_active`（**关键**：被上次 Stop Hook 阻断后重试时为 `true`）
- `last_assistant_message`

exit 2 阻断 Agent 停止，原因作为用户消息注入，Agent 继续工作。
输出：`{"decision":"block","reason":"..."}`。

> **⚠️ 防死循环（必须）**：脚本必须检查 `stop_hook_active`，为 `true` 时立刻 `exit 0`，
> 否则会陷入「阻断→重试→再阻断」无限循环。

### SubagentStart / SubagentStop
额外输入：`agent_id`、`agent_type`；SubagentStop 另有 `agent_transcript_path`、
`stop_hook_active`、`last_assistant_message`。
SubagentStart 输出 `additionalContext` 可注入子代理上下文。

### SessionEnd
额外输入：`reason`（结束原因）。
> 历史 matcher 元数据曾叫 `exit_reason`，**脚本应以 stdin 中实际的 `reason` 为准**。

### PreCompact
matcher：`manual`（用户手动压缩）/ `auto`（接近上限自动压缩）。
额外输入：`trigger`、`custom_instructions`。
IDE 中**仅通知与副作用，无法阻断压缩**。

### Notification
matcher：通知类型。额外输入：`notification_type`、`title`、`message`。

## 注意事项

- **超时**：默认 30s，超时终止并**按放行处理**
- **错误**：exit code 非 0 非 2 时，错误显示给用户，Agent 流程继续
- **配置合并**：多级配置同一事件按优先级低→高依次执行，**任一 Hook exit 2 则终止后续执行**

## 官方场景清单

| 场景 | 事件 |
|------|------|
| 拦截危险命令（`rm -rf`、`DROP TABLE`） | PreToolUse |
| 文件路径校验（限制可写目录） | PreToolUse |
| 自动 Lint / 格式化 | PostToolUse |
| 日志审计（记录所有工具调用） | PostToolUse |
| **失败监控告警** | **PostToolUseFailure** |
| Prompt 敏感信息检测（密码/密钥/内网 IP） | UserPromptSubmit |
| **自动注入上下文（项目规范、Skill 提示）** | **UserPromptSubmit** |
| 桌面通知 | Stop |
| 质量门禁（完成前跑构建/测试，未过则阻断） | Stop |
| **Harness 自进化（自动知识沉淀）** | **Stop** |

### 场景 1 关键点：自动注入 Skill 提示

`additionalContext` 会作为 **system-reminder** 追加到用户 Prompt 后。
官方示例用 `session_id` + `/tmp/hook-dedup/` 临时文件做**会话级去重**，避免每轮重复注入。

### 场景 8 关键点：Harness 自进化

痛点：每次任务的经验和决策散落在对话历史里，没有自动沉淀流程。
方案：`Stop` Hook 读 `transcript_path` 分析本次会话，两条落地路径：
- **A**：调用外部分析服务（`curl` 到自建 API）
- **B**：`exit 2` + `{"decision":"block","reason":"...请运行 /retro 复盘..."}` **阻断 Agent 并强制进入复盘 Skill**

官方示例把会话摘要 append 到 `~/.ai/inbox/pending-review.jsonl` 供后续批量复盘。

> **当前限制**：Hooks 只支持 `command` 和 `http`，**不支持 `prompt` / `agent` 类型**，
> 所以「自进化」只能走上面 A/B 两条路。官方计划未来支持 `prompt`/`agent` 处理器。

## 调试

```bash
# 模拟事件
echo '{"tool_name":"Bash","tool_input":{"command":"rm -rf /"},"hook_event_name":"PreToolUse"}' \
  | ~/.qoder/hooks/block-rm.sh
echo "Exit code: $?"
```
