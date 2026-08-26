# CLI 命令与参数（Qoder CLI）

> 来源：https://docs.qoder.com/zh/cli/cli-reference
> 终端里 `qoder --help` 可看完整列表。

```bash
qoder [选项] [提示文本]
```
不传参数 → 交互式会话；传提示文本或 `--print` → **非交互模式**。

## 通用

| 标志 | 短写 | 说明 |
|---|---|---|
| `--version` | `-v` | 输出版本号并退出 |
| `--help` | `-h` | 帮助 |
| `--debug` | `-d` | 启用调试日志输出 |
| `--cwd` | `-w` | 指定工作目录 |
| `--config-dir` | | 覆盖用户配置目录（默认 `~/.qoder`） |
| `--add-dir` | | 为当前会话添加**额外的信任目录**（可多次） |
| **`--attachment`** | | **为初始提示附加文件（可多次）** |
| `--worktree` | | 在新 Git Worktree 中隔离执行，结果合并回主分支；名称可选 |

## 模型与推理

`--model`/`-m`（`auto`、`lite`、`performance` 或 BYOK key）、`--reasoning-effort`、
**`--context-window`**（覆盖本次会话上下文窗口 token 数）、`--list-models`、`--output-style`

## 会话管理

| 标志 | 短写 | 说明 |
|---|---|---|
| `--continue` | `-c` | 继续最近一次会话 |
| `--resume` | `-r` | 按标识恢复历史会话；不带 id 时从列表选 |
| `--session-id` | | 继续指定 ID 的会话 |
| **`--fork-session`** | | 从恢复的会话中 fork 出新会话（配合 `--resume`/`--session-id`） |
| `--name` | `-n` | 设置或覆盖会话名称 |
| `--list-sessions` | | 列出所有历史会话 |
| `--delete-session` | | 按序号删除 |

> **冲突规则**：`--continue`、`--resume`、`--remote`、`--remote-session`、`--teleport`、`--remote-control` **不能同时使用**。

## ⭐ 输出与脚本模式（本项目自动化的入口）

| 标志 | 短写 | 说明 |
|---|---|---|
| `--print` | `-p` | **非交互模式**：输出一次响应后退出（适合 CI/脚本） |
| `--output-format` | `-o` | `text`（默认）/ **`json`** / `stream-json` |
| `--input-format` | | `text`（默认）/ `stream-json` |
| **`--max-turns`** | | 限制单次查询的最大对话轮数（**自动化场景防无限循环**） |
| `--max-output-tokens` | | 单次输出最大 token 数 |
| `--prompt-interactive` | `-i` | 先执行给定提示词，随后进入交互模式 |
| `--no-session-persistence` | | 不写磁盘、无法恢复（仅 `--print` 下有效） |

## 权限控制

| 标志 | 说明 |
|---|---|
| `--permission-mode` | `default` / `plan` / `auto` / `bypass_permissions` / `accept_edits` / `dont_ask` |
| `--yolo` | ≡ `--permission-mode bypass_permissions`（**危险：跳过所有权限确认**） |
| `--dangerously-skip-permissions` | 同上 |

## 工具与 MCP

`--tools`（限制可用内置工具，空格或逗号分隔；`""` 禁用全部、`default` 启用全部）、
`--allowed-tools` / `--disallowed-tools`、`--mcp-config`、`--strict-mcp-config`、
`--allowed-mcp-server-names`、`--max-model-request-retries`

## 沙箱

`--sandbox` / `-s`：**布尔开关，不接受后端名**。后端由 `QODER_SANDBOX` 或 `tools.sandbox` 指定。

## Agent 与系统提示

| 标志 | 说明 |
|---|---|
| `--agent` | 指定**主线程**使用的 Agent 名称 |
| `--agents` | 以 **JSON 对象**定义自定义 Agent |
| `--system-prompt` | **覆盖**系统提示 |
| `--append-system-prompt` | 在默认系统提示后**追加** |

## 配置覆盖

`--settings`（JSON 文件路径或**内联 JSON**，以 `{` 开头时按内联解析，**最高优先级**）、
`--setting-sources`、`--plugin-dir`

## 远程与协作

`--remote [task]`（创建云端远程会话并打印访问 URL）、`--remote-session <id>`（冷加载接入）、
`--teleport <id>`、`--remote-control <id>`（作为无头 worker 运行）

## 编辑器集成

`--acp`：以 ACP 服务器形式启动，供 Zed 等实现 ACP 协议的客户端通过标准输入输出集成。

## 子命令

| 子命令 | 说明 |
|---|---|
| `mcp` | 配置与管理 MCP 服务器 |
| `plugins`(plugin) | 管理插件 |
| `skills`(skill) | 管理 Agent Skills |
| `hooks`(hook) | 管理 Hooks |
| `agents`(agent) | 管理 Agent |
| `login` | 登录账户 |
| `commit` | 生成提交信息并提交改动 |
| `rollback` | 回滚到先前版本 |
| `update` | 更新到最新版本 |
| `remote-control` | 启动 remote-control 守护进程 |
| `status` | 显示会话状态 |
| `feedback` | 提交反馈 |
| **`wiki`** | **为项目生成 Wiki 文档** |

## 用法示例

```bash
qoder                                   # 交互式启动
qoder -m performance                    # 指定模型
qoder -p "解释这段代码做了什么"              # 非交互一次性执行
qoder -p -o json "列出项目依赖"            # JSON 输出用于脚本消费
qoder -c                                # 继续上次会话
qoder --worktree "重构数据库层"            # 在隔离 Worktree 中执行
qoder --permission-mode auto -s docker "运行测试并修复失败项"   # 全自动 + 沙箱
```

## 🎯 本项目可以怎么用

| 目标 | 命令 |
|---|---|
| CI 里批量校验用例 XMind 结构 | `qoder -p -o json --max-turns 5 "校验 docs/test-cases 下所有 xmind 的必填字段"` |
| 需求文档更新后自动重跑用例生成 | `qoder -p --attachment docs/requirements/xxx.md "按此需求生成用例 XMind"` |
| 隔离环境批量重构用例资产 | `qoder --worktree "统一 53 条用例的字段格式"` |
| 给自动化脚本兜底防跑飞 | 始终带 **`--max-turns`** |
