# Hooks、MCP 和插件问题 —— 排查（Qoder CLI）

> 来源：https://docs.qoder.com/zh/cli/troubleshoot-extensions
> 加载类问题见 `cli/10-troubleshoot-loading.md`

## ⭐ 先检查这两项

### 1. 目录是否受信任

**未信任的工作区不会加载**项目级设置、Hooks、MCP 与项目级 Agent
（交互式会话中 Hook 会被**直接拦截**）。

- 首次进入目录时弹信任选择：「仅本次会话」/「记住」（后者写入 `settings.local.json`）
- ⭐ 也可用 **`permissions.trustDirectories`** 永久信任常用目录

### 2. 改完配置是否重新加载

多数扩展支持**热重载，比重启快**：
`/mcp reload`、`/plugins reload`、`/skills reload`、`/agents reload`
标注「需重启」的配置项仍需重启 CLI。

## Hooks 未触发或行为异常

| 检查项 | 说明 |
|---|---|
| **事件与匹配** | 事件名是否正确；`matcher` 能否匹配目标（空或 `*` 匹配全部，精确值、`\|` 多值或正则） |
| **退出码** | `command` 类型靠退出码控制：`0` 成功、**`2` 阻塞（stderr 反馈给 Agent）**、其他为非阻塞错误。Hook 意外阻塞操作时先查是否返回了 `2` |
| **输入解析** | Hook 从 **stdin 接收 JSON**（含 `session_id`、`cwd`、`hook_event_name`），确认脚本正确读取 |
| **可执行权限** | `command` 指向的脚本需有可执行权限，路径正确 |
| **自查命令** | **`/hooks`** 查看已注册的 Hooks |

> 🎯 本项目 `.trae/hooks.json` 就算改对了目录和事件名，如果脚本没 `chmod +x`
> 或没从 stdin 读 JSON，照样不触发。这两点是最容易漏的。

## MCP 服务器未连接 / 工具不可用

| 检查项 | 说明 |
|---|---|
| **自查命令** | `/mcp` 查看连接状态 |
| **命令与路径** | stdio 类型确认 `command`/`args`/`cwd` 正确，**服务器能独立启动** |
| **项目级批准** | 项目级 MCP 默认需逐个批准，用 `mcp.enableAllProjectMcpServers` 或 `mcp.enabledProjectMcpServers` |
| **白名单限制** | 是否被 `mcp.allowed`/`mcp.excluded`、`--allowed-mcp-server-names` 或 `--strict-mcp-config` 过滤掉 |
| **认证** | HTTP/SSE 类型确认 `headers` 中认证信息正确 |
| **超时** | 连接慢可调 `timeout` |
| **重载顺序** | MCP 配置标「需重启」，但**先试 `/mcp reload`** |

## 插件未加载 / 组件缺失

| 检查项 | 说明 |
|---|---|
| **自查命令** | `/plugins` 查看已安装插件 |
| **Manifest** | 位于 **`.qoder-plugin/plugin.json`**（可省略）；已声明则 `name` 须为 kebab-case 无空格 |
| **目录结构** | 组件须在约定目录（`commands/`、`agents/`、`skills/`、`hooks/hooks.json`、`.mcp.json`），或在 manifest 显式声明路径 |
| **安全限制** | `security.blockGitExtensions` 为 true 时阻止从 Git 加载；`security.allowedExtensions` 非空时仅允许匹配来源 |

## 🎯 完整自查命令清单（本项目应该逐条跑一遍）

```
/memory        # 当前加载的记忆来源
/skills        # 已加载的 Skills
/agents        # 已加载的 Agent
/hooks         # 已注册的 Hooks
/mcp           # MCP 连接状态
/plugins       # 已安装插件
```

这 6 条命令的输出，比任何推测都能更快确认「哪些资产真的在生效」。
