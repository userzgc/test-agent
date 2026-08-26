# 斜杠命令全表（Qoder CLI）

> 来源：https://docs.qoder.com/zh/cli/slash-reference
> 会话里输入 `/` 弹补全，`/help` 看全部。

## 会话与对话

| 命令 | 说明 |
|---|---|
| `/new` | 新建空会话 |
| `/clear` | 清除当前会话内容 |
| `/continue` | 继续当前项目最近一次会话 |
| `/resume` | 恢复历史会话 |
| `/rename` | 重命名当前会话 |
| **`/branch`** | **从当前会话分支出新会话**（= IDE 的 Fork） |
| `/export` | 导出当前会话内容 |
| `/copy` | 复制上一条响应 |
| **`/compact`** | **压缩上下文以释放空间** |
| **`/rewind`** | **回退到指定检查点** |
| `/quit` | 退出 CLI |

## 模型与推理

`/model`（选对话模型）、`/effort`（推理努力级别）、`/fast`（快速模式）、`/context-window`（设上下文窗口）

## 工作模式

| 命令 | 说明 |
|---|---|
| `/plan` | 进入 Plan（计划）模式 |
| `/goal` | 管理会话目标 → `/zh/cli/goal-reference` |
| **`/loop`** | **定期循环执行提示或命令** → `/zh/cli/loop-reference` |
| **`/quest`** | 智能工作流编排器，引导通过**专用子代理**逐步完成功能开发 |
| `/tasks` | 后台任务面板（别名 `/bg`、`/background`） |
| `/workflows` | 工作流面板（别名 `/workflow-tasks`） |
| `/kanban` | 看板面板 |

## 代码与审查

| 命令 | 说明 |
|---|---|
| `/diff` | 查看代码改动 Diff |
| `/review` | 审查代码改动 |
| **`/init`** | **初始化项目（生成项目说明文件）** ← 生成 `AGENTS.md` 的官方入口 |
| `/setup-github` | 配置 GitHub Actions 集成（**CN 版不可用**） |

## 配置与界面

`/settings`（别名 `/config`）、`/theme`、`/statusline`、`/editor`、`/vim`、`/voice`、`/shortcuts`

## ⭐ 扩展与工具（本项目排查失效的入口）

| 命令 | 说明 |
|---|---|
| `/mcp` | 管理 MCP 服务器 |
| `/tools` | 查看可用工具列表 |
| `/skills` | 管理 Agent Skills |
| `/agents` | 管理 Agent |
| `/hooks` | 管理 Hooks |
| `/commands` | **重新加载并列出**所有可用命令 |
| `/plugins` | 管理插件（别名 `/plugin`） |
| `/marketplace` | 插件市场（别名 `/market`） |
| `/memory` | 管理长期记忆 |

## 内置 Skills 提供的命令

也可由 Agent 按需自动调用：

| 命令 | 说明 |
|---|---|
| `/debug` | 调试助手，辅助定位与修复问题 |
| `/verify` | **验证结果是否符合预期** |
| `/simplify` | 简化代码或流程 |
| `/security-scan` | 云端安全扫描（支持 L2 轻量与 L3 深度评审） |
| `/run` | 启动并驱动项目实际应用，观察改动运行时效果 |
| `/run-skill-generator` | 创建或改进项目专属的 `run` 技能 |
| `/batch` | 在**隔离 git worktree** 中生成并行工作代理，跨多文件批量改动（需 git 仓库） |
| `/remember` | 评审自动积累的记忆条目并提出**晋升建议**（需启用自动记忆） |
| `/mcp-config` | 管理 MCP 服务器配置 |

## 账户与状态

`/login`(/signin)、`/logout`(/signout)、`/status`、`/profile`、`/usage`、`/upgrade`、
`/insights`、`/privacy`、**`/permissions`（查看与调整权限规则）**

## 远程与其他

`/remote-control`、`/remote-env`、**`/add-dir`（添加信任目录）**、`/context`（管理上下文）、
`/docs`、`/help`、`/about`、`/feedback`、`/release-notes`

## ⚠️ 条件性命令（可能不可见）

- `/agents`、`/plan`、`/workflows`、`/marketplace`：**仅当对应功能开关开启**
- `/skills`：需要 Skills 支持与**管理员权限**开启
- `/mcp`：MCP 被禁用时显示禁用提示
- `/setup-github`：**CN 版不可用**
- 被功能门控关闭时，输入会显示禁用提示

> 🎯 这一条解释了一种失效可能：不是配置写错，而是**功能开关/管理员权限没开**，
> 命令本身就不可见。排查 `.trae/` 迁移前，先确认 `/skills`、`/agents` 是否可见。

## 🎯 本项目最该先用的 5 条

| 命令 | 用途 |
|---|---|
| `/init` | 让 Qoder 自己生成 `AGENTS.md` 骨架，比手写省事 |
| `/skills` `/agents` `/hooks` `/memory` | 四条自查，用实际加载结果代替猜测 |
| `/remember` | 把散落的自动记忆整理并晋升，治 `lessons-learned.md` 越写越乱 |
| `/verify` | 用例生成完做独立校验 |
| `/branch` | 讨论到方案分叉点时开新线 |

## 关联页面（尚未抓取）

`/zh/cli/goal-reference`、`/zh/cli/scheduled-reference`、`/zh/cli/loop-reference`、`/zh/cli/commands`
