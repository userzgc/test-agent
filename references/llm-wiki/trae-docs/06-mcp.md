# MCP Server（模型上下文协议）

> 来源：https://docs.trae.cn/ide/model-context-protocol

## 是什么
MCP（Model Context Protocol）让 LLM 访问自定义工具和服务。Trae 中的智能体作为 MCP 客户端，可向 MCP Server 发起请求调用工具。

## 传输类型
- **stdio** — 标准输入输出
- **SSE** — Server-Sent Events
- **Streamable HTTP** — 流式 HTTP

## 环境依赖
- **Node.js 18+**（npx）— 大部分 MCP Server 需要
- **Python 3.8+ + uvx**（基于 uv）— Python 类 MCP Server 需要
- **Docker**（可选）— GitHub MCP Server 等需要

## 添加 MCP Server
### 方式一：从市场添加
设置 > MCP > + 添加 > 从市场添加 → 找到 MCP Server → 填配置（env 中的 key/token 需替换为真实值）→ 确认

### 方式二：手动添加
设置 > MCP > + 添加 > 手动添加 → 填 JSON 配置 → 确认

**优先使用 NPX 或 UVX 配置**，避免全局安装依赖冲突。

## 在智能体中使用
- **Builder with MCP** — 自动加载所有已配置 MCP Server（不可编辑）
- **自定义智能体** — 创建时勾选 MCP Server，或在 MCP 列表中点 + 添加到指定 Agent

## 配置文件
项目级：`.trae/mcp.json`

## 管理
- 编辑：齿轮图标
- 删除：删除按钮
- 启用/禁用：开关

## 常见场景
- Figma 设计稿转前端代码（Figma MCP）
- 网页自动化测试（Playwright MCP）
- 地图/位置服务（高德 MCP）
- 数据库查询
- 企业内部工具集成

## 注意
- MCP Server 由第三方构建维护，Trae 不审查
- 部分 Server 可能因网络/法规在部分地区不可用
- env 字段（API Key/Token）需替换为真实值
