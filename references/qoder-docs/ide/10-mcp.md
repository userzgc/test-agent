# MCP（Qoder IDE）

> 来源：https://docs.qoder.com/zh/user-guide/chat/model-context-protocol

## 支持的两种传输方式

| 传输 | 通信方式 | 适用 |
|---|---|---|
| **STDIO** | stdin/stdout 流 | 本地工具、命令行集成；需本地环境配置 |
| **SSE** | 客户端 HTTP POST 发请求，服务端事件流返回 | 远程托管，易配置；**也支持 Streamable HTTP** |

> Streamable HTTP 与 SSE **用同样的 `url` 字段配置**，Qoder 自动识别。

## 配置入口

设置快捷键 `⌘⇧,`（macOS）/ `Ctrl+Shift+,` → 左侧 **MCP**。

### 方式一：手写配置（我的服务 → + 添加）

STDIO：
```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "<YOUR_TOKEN>" }
    }
  }
}
```

SSE / Streamable HTTP：
```json
{
  "mcpServers": {
    "fetch": { "type": "sse", "url": "https://mcp.api-inference.modelscope.net/******/sse" }
  }
}
```

关闭文件 → 提示时点保存。**链接图标表示连接成功**，展开条目可看可用工具。

服务详情里有 **服务超时时长（Request Timeout）** 下拉框，超时后本次调用自动终止并在会话中提示。

### 方式二：MCP 广场安装

浏览列表 → 点「安装」→ 到「我的服务」确认。
- 部分服务需手动配置环境变量（`API_KEY` / `ACCESS_TOKEN`）
- 因缺依赖启动失败时可点**一键修复**，仍失败需手动装依赖

## 调用行为

Qoder 根据**输入提示 + 工具名称和描述**自动选择 MCP 工具。
调用前会请求确认（`⌘⏎` / `Ctrl+Enter` 执行），**勾选确认框可自动运行后续所有 MCP 服务**。

## 🔁 与当前项目的关系

当前项目有 `.trae/mcp-servers/` 目录和 `docs/mcp-config-guide.md`。

- `.trae/mcp-servers/` 这个目录 Qoder **不读**——Qoder 的 MCP 配置在
  `settings.json` 的 `mcpServers` 字段，或通过 IDE MCP 设置界面维护
- 相关的 CLI 侧控制项见 `cli/08-settings-reference.md` 的 `mcp.*` 分组，
  其中 `mcp.enableAllProjectMcpServers` / `mcp.enabledProjectMcpServers`
  决定项目级 MCP 服务器是否被批准——**项目级 MCP 默认不自动批准**
- 权限侧可用 `mcp__<server>__<tool>` 规则精确控制（见 `cli/06-permissions.md`），
  也可在 server 配置里用 `alwaysAllow`

本项目实际依赖的 MCP（Confluence / 设计稿 / XMind 相关）**必须落在 `mcpServers` 里才生效**，
`.trae/mcp-servers/` 里的内容至多是文档，不是配置。
