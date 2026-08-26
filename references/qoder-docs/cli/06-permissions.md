# 权限（Qoder CLI）—— 硬性约束层

> 来源：https://docs.qoder.com/zh/cli/permissions
> ⭐ **这是「防复发」的正确落点**。记忆和规则只是上下文（软约束），
> 官方明确说：「需要**硬性**阻止某类命令、工具或路径，请使用**权限**或**钩子**。」

## 权限模式（5 种）

| 模式 | 适用场景 | 行为 |
|---|---|---|
| `default` | 常规交互式使用 | 安全读取和内部动作可自动执行；敏感操作请求确认 |
| `accept_edits` | 日常编码任务 | 自动批准工作目录内的安全文件编辑。Shell 命令、外部动作和敏感路径仍走正常检查 |
| `auto` | 自动化运行、无人值守的 Goal 执行 | **零弹窗**。安全读取和工作区内编辑自动批准；风险动作被拒绝或交给 **AI 分类器**判断 |
| `bypass_permissions`（YOLO） | 仅用于可信本地实验 | 跳过所有批准提示，全部放行 |
| `dont_ask` | 必须不弹窗的 headless 流程 | **从不询问**。任何原本需要询问的动作都会被**拒绝** |

- **Shift+Tab** 循环切换模式，**Ctrl+Y** 直达 YOLO
- 启动参数 `--permission-mode <mode>`，快捷方式 `--yolo` / `--dangerously-skip-permissions`
- 命名大小写不敏感，`accept_edits`≡`acceptEdits`，`bypass_permissions`≡`bypassPermissions`≡`yolo`
- ⚠️ **非默认模式只在可信目录中生效**。当前目录未被信任时强制回退到 `default`

## 权限决策：三种结果 + 五步顺序

结果只有 `allow` / `ask` / `deny`。评估顺序固定：

1. **先检查 `deny` 规则**——命中即拒绝
2. 工具自身的安全检查（危险命令检测、敏感路径检测）
3. **`ask` 规则**——命中则标记为需要确认
4. 工具级 `allow` 规则和模式带来的自动允许
5. 结果仍是 `ask` 时，由运行环境决定如何消费

> **宽泛 allow 规则不等于所有动作都静默执行**——安全检查和 ask 规则优先级更高。

### `ask` 在不同环境的归宿

| 运行环境 | `ask` 归宿 |
|---|---|
| **TUI**（交互式终端） | 弹窗确认 |
| **Headless**（`-p`） | **自动拒绝**（`ask` → `deny`） |
| **SDK**（stdio） | 发 `canUseTool` 回调给宿主 |
| **ACP**（IDE 集成） | 发 `requestPermission` RPC 给 IDE |

## 配置来源（7 层，低 → 高）

| 层 | 来源 | 说明 |
|---|---|---|
| 1 | `userSettings` | `~/.qoder/settings.json` |
| 2 | `projectSettings` | `<project>/.qoder/settings.json`（团队共享） |
| 3 | `localSettings` | `<project>/.qoder/settings.local.json`（加 `.gitignore`） |
| 4 | `flagSettings` | `--settings <path>` |
| 5 | `cliArg` | `--allowed-tools` / `--disallowed-tools` |
| 6 | `command` | 会话中 `/allow`、`/deny`（**持久化到 `settings.local.json`**） |
| 7 | `session` | 弹窗里选"本次会话允许"，进程退出即失效 |

组织策略开启 `allowManagedPermissionRulesOnly` 时只用策略托管的规则。

## 规则语法

```json
{
  "permissions": {
    "allow": ["Read(/src/**)", "Edit(/src/**)", "Bash(npm run test:*)"],
    "ask":   ["Bash(npm publish:*)", "WebFetch"],
    "deny":  ["Read(*.pem)", "Bash(rm -rf:*)"]
  }
}
```

| 形式 | 含义 |
|---|---|
| `ToolName` | 作用于整个工具 |
| `ToolName(content)` | 作用于某个路径、命令、agent 类型等 |
| `*` | 匹配所有工具 |

`ToolName(*)` ≡ `ToolName`。内容含括号需转义：`"Bash(python -c \"print\\(1\\)\")"`。

规范工具名：`Read`、`Edit`、`Write`、`Bash`、`Grep`、`Glob`、`WebFetch`、`WebSearch`、`Agent`，
以及 `mcp__github__create_issue` 这类 MCP 工具名。

### 文件路径规则

写入规则用 **`Edit(...)`**，它**覆盖 `Edit`、`Write` 和 `NotebookEdit` 的文件写入检查**。
某路径上的 `Edit(...)` allow 规则**隐含允许读取同一路径**。gitignore 风格匹配。

| 模式 | 含义 |
|---|---|
| `/src/**` | **基于规则来源根目录**。project/local settings 中相对项目根；user settings 中相对 home |
| `~/Documents/**` | 基于 home 目录 |
| `//tmp/data/**` | 系统绝对路径，**需要双斜杠** |
| `*.secret` | 不带根目录的文件名模式，任意位置匹配 |

### Bash 规则

| 规则 | 匹配 |
|---|---|
| `Bash(npm run build)` | 精确匹配 |
| `Bash(npm run test:*)` | 匹配 `npm run test` 及以 `npm run test ` 开头的命令 |
| `Bash(git log *)` | glob 风格通配 |

Shell 匹配是**保守的**：
- `deny` 和 `ask` 规则会**穿透常见 wrapper 和环境变量前缀**，所以 `Bash(rm -rf:*)` 能拦截被包装的破坏性命令
- 前缀/通配 `allow` 规则**不会静默批准复合命令**，除非每个顶层片段都能独立被允许
- 危险命令（破坏性删除、force push）即使有宽泛 allow 也可能强制确认；**`auto` 模式下直接拒绝**

> 除非完全信任当前会话，避免使用 `Bash` 或 `Bash(*)` 这类宽泛规则。

### MCP 规则

`mcp__<server>__<tool>`，支持 `mcp__github__*`、`mcp__github`、`mcp__*`。
也可在 MCP server 配置里用 `alwaysAllow`；单次运行限定用 `--allowed-mcp-server-names context7,github`。

## Auto 模式的 AI 分类器（自然语言软引导）

```json
{
  "autoMode": {
    "allow": ["running npm/yarn/pnpm scripts defined in package.json", "creating or editing test files"],
    "soft_deny": ["deleting files outside the test directory", "modifying CI/CD configuration"],
    "environment": ["This is a Node.js monorepo with pnpm workspaces", "The project uses Vitest for testing"]
  }
}
```

⚠️ **软引导**，最终由 AI 分类器决策。出于安全，`autoMode` **只从可信来源读取
（user settings 和 localSettings），项目 settings 被排除**以防恶意权限提升。

## 信任目录

启动时的 CWD 是**主信任目录**。信任目录内：文件读取默认 allow、
`accept_edits`/`auto` 下写入可自动批准、非默认权限模式才能生效。

扩展信任：`--add-dir ../shared`、`/add-dir`、`permissions.additionalDirectories`，
或全局 settings 的 `permissions.trustDirectories` 永久信任。

### 受保护路径（改动会影响执行行为/凭据）

`.git`、`.vscode`、`.idea`、`.husky`、**大多数 `.qoder` 配置文件**、
`.bashrc`/`.zshrc` 等 shell 启动文件、Git 配置、`.mcp.json`、`.ripgreprc`。
常规交互模式下需明确批准，**`auto` 模式下会被拒绝**。

## ⭐⭐ Hook 与权限：不可绕过的拦截能力

只有两个 Hook 事件参与权限决策：

| Hook 事件 | 触发时机 | 权限影响 |
|---|---|---|
| `PreToolUse` | 工具执行前（权限检查阶段） | 返回 `permissionDecision: "allow"/"deny"/"ask"` **直接覆盖权限管道结果** |
| `PermissionRequest` | 权限管道产出 `ask` 后、弹窗前 | 返回 `decision.behavior` 为 `allow`/`deny`，**代替用户交互** |

其他事件（`PostToolUse`、`SessionStart`、`Stop` 等）**不参与权限决策**。

### PreToolUse 返回格式

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Command blocked by security policy"
  }
}
```

`permissionDecision`：`"allow"` 跳过管道直接批准 / `"deny"` 跳过管道直接拒绝 / `"ask"` 继续走正常管道（默认）。

### PermissionRequest 返回格式

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PermissionRequest",
    "decision": { "behavior": "allow", "updatedInput": {}, "updatedPermissions": [] }
  }
}
```

适合自动化审批系统或外部通知（Slack/邮件提醒）。

### 🔒 优先级：Hook > 权限模式

> 官方原话：「Hook 的权限决策优先级**高于**权限模式——**即使在 `bypass_permissions` 模式下，
> PreToolUse Hook 返回 `deny` 仍然会阻止执行**。这为组织级安全策略提供了**不可绕过的拦截能力**。」

执行顺序：
1. Hook `PreToolUse` → 返回 allow/deny 则**短路**
2. 权限管道（规则 + 模式 + 安全检查）
3. 结果是 `ask` → Hook `PermissionRequest` → 返回 allow/deny 则**短路**
4. 运行环境消费 `ask`

## 🎯 本项目「防复发」的三层落地方案

用户前面提的诉求是「不要踩坑记录，要防复发机制」。官方给的层次很清楚：

| 层 | 载体 | 强度 | 适合本项目哪条约束 |
|---|---|---|---|
| **软约束** | `AGENTS.md` / `.qoder/rules/` | 上下文提示，模型可能忽略 | 「用例先给 XMind 不给 md」这类偏好 |
| **半硬约束** | `permissions.deny` | 规则匹配，命中即拒 | `"deny": ["Edit(/docs/test-cases/*.md)"]` —— 直接禁止在用例目录写 md |
| **硬约束** | `PreToolUse` Hook + `permissionDecision: "deny"` | **不可绕过，连 YOLO 都拦得住** | 需要看工具参数内容才能判断的场景（如 XMind 结构校验、必填字段检查） |

三者叠加才是完整的 Harness。当前项目**一层都没有真正生效**。
