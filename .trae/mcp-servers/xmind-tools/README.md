# XMind Tools MCP Server

> 状态：**骨架，未实装**。当前为占位，未来对外赋能时启用。

## 作用

把项目里的 `gen_xmind.py` / `parse_xmind.py` 包装成 MCP Server，同事在他们的 Trae/Cursor 里配置即可复用，不用 clone 整个项目。

## 为什么单独抽

| 方式 | 优点 | 缺点 |
|------|------|------|
| clone 整个项目 | 完整能力 | 同事要装 lark-cli/Confluence 凭据等，重 |
| 抽成 MCP Server | 轻量，同事只配一个 MCP | 要写包装层 |

XMind 生成/解析是纯本地能力，无外部依赖，最适合先抽。

## 启用步骤

1. 安装 mcp python sdk：
   ```bash
   pip install mcp
   ```

2. 替换 `server.py` 里的 stdio 入口为 mcp sdk 标准 Server 实现（标注了 TODO）

3. 在 `.trae/mcp.json` 添加：
   ```json
   {
     "mcpServers": {
       "xmind-tools": {
         "command": "python3",
         "args": [".trae/mcp-servers/xmind-tools/server.py"]
       }
     }
   }
   ```

4. 重启 Trae

## 当前状态

- ✅ 目录结构占位
- ✅ 工具 schema 定义
- ✅ 工具调用分发逻辑
- ⚠️ stdio 入口是简化版，未接 mcp sdk
- ⚠️ 未实装，未测试

## 后续可扩展

| 工具 | 来源脚本 |
|------|---------|
| parse_yapi | `.trae/scripts/parse_yapi.py` |
| parse_feishu | `.trae/scripts/parse_feishu.py` |
| extract_confluence_images | `.trae/scripts/extract_confluence_images.py` |
| ocr_images | `.trae/scripts/ocr_images.py` |

需要外部凭据的工具（Confluence/飞书）不适合直接抽 MCP Server，因为凭据管理复杂。
