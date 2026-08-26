# MCP 参考（Qoder CLI）

> 来源：https://docs.qoder.com/zh/cli/mcp-reference
> IDE 侧用法见 `ide/10-mcp.md`

## 传输方式（`type` 字段）

| 类型 | 说明 |
|---|---|
| `stdio`（**默认**） | 启动子进程，通过 stdin/stdout 交互 |
| `sse` | Server-Sent Events HTTP 连接 |
| `http` / `streamable-http` | HTTP（JSON-RPC + 可选流式） |
| `ws` | WebSocket / TCP |
| `sdk` | 内置 SDK 级服务器（进程内） |

## 配置位置与字段

配置在 `settings.json` 的 **`mcpServers`** 字段下，每个 key 是服务器名：

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["./mcp-server.js"],
      "env": { "API_KEY": "..." },
      "cwd": "/path/to/dir"
    }
  }
}
```

**stdio**：`command` / `args` / `env` / `cwd`
**sse**：`url` / `type:"sse"` / `headers`（可含认证）
**http**：`url` / `type:"http"` / `headers`
**ws**：`tcp`（host/port）/ `type:"ws"`

### 通用可选字段

| 字段 | 说明 |
|---|---|
| `timeout` | 连接/请求超时（毫秒） |
| `description` | 管理视图中展示的描述 |
| `trust` | **信任该服务器，调用其工具时跳过确认** |
| `includeTools` | 仅注册列出的工具 |
| `excludeTools` | 排除列出的工具 |
| `disabled` | 禁用该服务器（**保留配置不删除**） |
| `alwaysAllow` | 无需确认、始终允许的工具名列表 |
| `oauth` | OAuth 配置（`enabled`/`clientId`/`clientSecret`/`authorizationUrl`/`tokenUrl`/`scopes`/`callbackPort`） |

## 作用范围与覆盖顺序

| 层级 | 位置 | 说明 |
|---|---|---|
| 用户级 | `~/.qoder/settings.json` → `mcpServers` | 所有项目可用 |
| 项目级 | `<项目>/.qoder/settings.json` → `mcpServers` | **需批准后可用** |
| 项目级 | **`<项目>/.mcp.json`** | 需带顶层 `mcpServers` 键；需批准 |
| 本地级 | `<项目>/.qoder/settings.local.json` → `mcpServers` | 仅本机当前项目；`-s` 默认作用域，**仅目录受信任时加载** |
| 插件 | 插件目录下 `.mcp.json` 或 `mcp.json` | 随插件安装加载 |
| CLI 参数 | `--mcp-config <path>`、`--settings` | **仅本次会话有效** |

同名覆盖顺序（后覆盖前）：
用户级 → 项目级 `settings.json` → 项目级 `.mcp.json` → 本地级 → CLI 参数

### 项目级默认需逐个批准，两种跳过方式

```json
{
  "mcp": {
    "enableAllProjectMcpServers": true,
    "enabledProjectMcpServers": ["playwright", "context7"]
  }
}
```
（`mcp` 分组下，**修改后需重启**）

## 权限与安全

- MCP 工具与内置工具一样受权限系统管理，调用前需确认（除非 `auto` 或 `bypass_permissions` 模式）
- `--allowed-mcp-server-names`：仅加载指定名称的服务器
- `--strict-mcp-config`：**仅加载 `--mcp-config` 指定文件**中的服务器
- `mcp.allowed` / `mcp.excluded`：配置中控制允许/排除列表

## ⭐ 懒加载模式（省 token）

连了多个 MCP 时默认启动即注册全部工具 schema，占用较多首轮 prompt token。
开启 `mcp.lazyLoad: true` 或 `QODER_MCP_LAZY=1` 后，只暴露三个 meta 工具
（**`mcp_list` / `mcp_get` / `mcp_call`**），按需加载实际工具。

> 🎯 本项目接了 Confluence / 设计稿 / XMind 等多个 MCP，开懒加载能明显省上下文。

## 管理命令

**交互式**：
- `/mcp` — 查看已连接服务器与状态
- **`/mcp reload`**（别名 `/mcp refresh`）— 重新发现服务器与工具，改配置后先试这个再考虑重启

**命令行**：
- `qoder mcp add <name> -- <command>`
- `qoder mcp list`
- `qoder mcp remove <name>`
