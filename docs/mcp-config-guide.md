# MCP Server 配置指南

> 本文件指导用户手动配置 `.trae/mcp.json`（该文件受保护，模型不可直接修改）。

## 配置位置

项目级：`.trae/mcp.json`（需用户手动创建/编辑，Trae 设置 > MCP > 手动添加）

## 预留 MCP Server 清单

| MCP Server | 用途 | 安装方式 | 状态 |
|-----------|------|---------|------|
| MongoDB | 查询 config/online/settle 数据库 | npx 自动安装 | 🔲 待配置 |
| Playwright | 浏览器自动化，UI 测试 | npx 自动安装 | 🔲 待配置 |
| 阿里云 SLS | 查询阿里云日志服务 | 手动安装二进制 | 🔲 待配置 |
| 蓝湖 | 获取蓝湖设计稿结构化数据 | npm 全局安装 | 🔲 待配置 |

## 配置模板

在 `.trae/mcp.json` 中填入以下内容（替换 `<TODO>` 为真实值）：

```json
{
  "mcpServers": {
    "mongodb": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-mongodb"],
      "env": {
        "MONGODB_URI": "mongodb://user:pass@host:port/db"
      }
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-playwright"],
      "env": {}
    },
    "aliyun-sls": {
      "command": "/Users/zhangguichang/bin/alibabacloud-observability-mcp-server",
      "args": [],
      "env": {
        "ACCESS_KEY_ID": "<填真实AK>",
        "ACCESS_KEY_SECRET": "<填真实SK>"
      }
    },
    "lanhu": {
      "command": "npx",
      "args": ["-y", "@star_work/lanhu-mcp"],
      "env": {
        "LANHU_COOKIE": "<浏览器开发者工具获取Cookie>"
      }
    }
  }
}
```

## 安装说明

### MongoDB
- npx 自动安装，无需额外步骤
- 需确认 MongoDB 连接串（config/online/settle 库）

### Playwright
- npx 自动安装，无需额外配置

### 阿里云 SLS
```bash
# macOS arm64
curl -sL https://github.com/aliyun/alibabacloud-observability-mcp-server/releases/latest/download/alibabacloud-observability-mcp-server-darwin-arm64.tar.gz -o /tmp/aliyun-mcp.tar.gz
mkdir -p ~/bin && tar -xzf /tmp/aliyun-mcp.tar.gz -C ~/bin/
```
- AK/SK 管理：密钥通过加密机加密后存储在 `.trae/settings/.env` 的 `[aliyun_sls]` section
- 前提：内网加密机服务（`192.168.1.200:8000`）可访问
- 加密新密钥：`python3 .trae/agents/utils/decrypt.py --encrypt --section aliyun_sls --key access_key_id --value "明文AK"`

### 蓝湖
```bash
npm install -g @star_work/lanhu-mcp
```
- 获取蓝湖 Cookie：浏览器开发者工具 → Network → `/api/` 请求 → 复制 Cookie
- Cookie 过期需重新获取

## 在智能体中使用

配置 MCP Server 后，在 Trae 中：
1. Builder with MCP：自动加载所有已配置 MCP Server
2. 自定义智能体：创建时勾选 MCP Server

## 安全注意

- **不要把真实 AK/SK/Cookie 提交到 Git**
- `.trae/mcp.json` 加入 `.gitignore`（如已含敏感值）
- 密钥通过加密机加密后存储在 `.trae/settings/.env`
