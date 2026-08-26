# Hooks 参考（Qoder CLI，26 事件 + 4 类型）

> 来源：https://docs.qoder.com/zh/cli/hooks-reference
> ⚠️ **与 `ide/04-hooks.md` 有重大差异，必读**：
> - IDE 文档写 **12 个事件**，CLI 文档写 **26 个事件**
> - IDE 文档写只支持 `command` / `http`，CLI 文档写支持 **`command` / `http` / `prompt` / `agent`**
>
> 两者**共用 `settings.json` 的同一个 `hooks` 分组**，但各入口只执行自身支持的事件与类型。
> 写配置时按你实际使用的入口取规格；跨入口共用的配置只用两边都支持的交集。

## 事件类型（26）

| 事件 | 触发时机 |
|---|---|
| `PreToolUse` | 工具调用前 |
| `PostToolUse` | 工具调用成功后 |
| `PostToolUseFailure` | 工具调用失败后 |
| `UserPromptSubmit` | 用户提交提示时 |
| `SessionStart` | 会话开始 |
| `SessionEnd` | 会话结束 |
| `Stop` | 主 Agent 停止响应时 |
| `StopFailure` | 停止流程失败时 |
| `SubagentStart` | 子 Agent 启动 |
| `SubagentStop` | 子 Agent 停止 |
| `PreCompact` | 上下文压缩前 |
| `PostCompact` | 上下文压缩后 |
| `Notification` | 产生通知时 |
| `ConfigChange` | 配置变更时 |
| `InstructionsLoaded` | 加载项目说明后 |
| `CwdChanged` | 工作目录变更时 |
| `FileChanged` | 文件变更时 |
| `WorktreeCreate` | 创建 Worktree 时 |
| `WorktreeRemove` | 移除 Worktree 时 |
| `Elicitation` | 发起信息征询时 |
| `ElicitationResult` | 征询结果返回时 |
| `TaskCreated` | 创建任务时 |
| `TaskCompleted` | 任务完成时 |
| `PermissionRequest` | 发起权限请求时 |
| `PermissionDenied` | 权限被拒绝时 |
| `TeammateIdle` | 协作者空闲时 |
| `Setup` | 初始化安装时 |

**IDE 独有 / CLI 独有的取舍**：IDE 那 12 个是这 26 个的子集。
CLI 多出来的里对本项目有用的是：`InstructionsLoaded`（可校验规则是否真被加载）、
`FileChanged`（产出物落地即触发校验）、`TaskCompleted`、`PostCompact`、`StopFailure`。

## Hook 类型（4）

| 类型 | 说明 |
|---|---|
| `command` | 执行一条 Shell 命令 |
| `http` | 发送 HTTP 请求 |
| **`prompt`** | 独立的单轮模型调用做判定，模型返回 `{ ok, reason }`，**`ok=false` 阻塞** |
| **`agent`** | 启动子 Agent 校验，经 `StructuredOutput` 返回 `{ ok, reason }`，**`ok=false` 阻塞** |

> ⭐ `prompt` / `agent` 让「用模型做语义校验并阻断」成为原生能力——
> 例如 Stop 事件挂 `agent` 类型 hook 判断「本次会话是否产出了符合规范的 XMind」，
> 不合规就 `ok=false` 阻断。这比写死的 Python 脚本表达力强得多。

## 定义结构

配置在 `settings.json` 的 `hooks` 分组，按事件分组：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "./scripts/check.sh" }
        ]
      }
    ]
  }
}
```

分组字段：`matcher`（匹配规则）、`hooks`（Hook 数组，每项含 `type` 及类型参数）。

单个 Hook 条目除 `type` 及类型专属参数外，还支持：
`name`、`timeout`、`if`、`async`（**后台执行，不阻塞主流程**）。

## 匹配规则

`matcher` 决定 Hook 对哪些目标（如工具名）生效：

- 空或 `*` — 匹配全部
- 精确值 — 如 `Bash`
- 管道符 — `Bash|Edit|Write`
- **正则** — 支持正则表达式

更细粒度的 `if` 条件可写作 `"ToolName"` 或 **`"ToolName(arg_glob)"`**，
其中 `arg_glob` 用 glob 模式匹配**工具参数**。
例：`"Write(docs/test-cases/*.xmind)"` 只在写入用例目录时触发。

## 输入（stdin JSON）通用字段

| 字段 | 说明 |
|---|---|
| `session_id` | 当前会话 ID |
| `transcript_path` | **会话记录文件路径**（复盘/自进化的关键入口） |
| `cwd` | 当前工作目录 |
| `hook_event_name` | 触发的事件名 |
| `permission_mode` | 当前权限模式 |
| `agent_id` | 触发的 Agent ID（如适用） |
| `agent_type` | Agent 类型（如适用） |

## 退出码（`command` 类型）

| 退出码 | 含义 |
|---|---|
| `0` | 成功。stdout 可输出 JSON 供 CLI 解析 |
| `2` | **阻塞**。stderr 内容作为反馈返回给 Agent（仅对支持阻塞的事件生效） |
| 其他 | 非阻塞错误，记录但不中断流程 |

`exit 0` 时可通过 stdout 返回 JSON 做精细控制，字段：
`continue`、`stopReason`、`suppressOutput`、`systemMessage`、`decision`、`reason`、`hookSpecificOutput`。

## 插件中的 Hooks

插件可携带 Hooks，配置于**插件目录下的 `hooks/hooks.json`**，格式与 `settings.json` 的 `hooks` 分组一致。

## 🔁 与当前项目 `.trae/hooks.json` 的差距

当前项目把 hook 配置写在 `.trae/hooks.json`（Trae 的约定）。Qoder 里：

| | 位置 |
|---|---|
| **Trae** | `.trae/hooks.json`（独立文件） |
| **Qoder** | `settings.json` 的 `hooks` 分组（`~/.qoder/` / `.qoder/` / `.qoder/settings.local.json` 三级） |
| **Qoder Plugin** | 插件目录下 `hooks/hooks.json` |

所以 hooks 的迁移**不是改目录名**，是把 JSON 内容搬进 `settings.json` 的 `hooks` 键下，
并把事件名和 matcher 换成 Qoder 的写法。4 个 Python hook 脚本本身**可以直接复用**。

## 待补

官方「使用指南」页（含**事件清单**逐事件的 matcher 字段 / stdin 额外字段 / 是否支持阻塞 /
可用 `hookSpecificOutput` 字段，以及 **Hook 条目类型**小节的 `prompt`/`agent` 完整返回约定）
在 `/zh/cli/hooks`——参考页里的链接自指到了 hooks-reference，需单独抓取。
`ide/04-hooks.md` 已记录了 IDE 那 12 个事件的逐事件字段，可先用那份。
