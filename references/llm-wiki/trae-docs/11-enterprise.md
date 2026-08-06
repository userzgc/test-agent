# Trae 企业版能力

> 来源：https://www.volcengine.com/docs/86677/2558676

## 套餐要求
- 旗舰版（企业版最高档）

## 环境要求
- TRAE IDE：3.3.70+
- TRAE CLI：0.120.42+
- TraeWork 桌面版：0.1.38+
- TraeCode Plugin（JetBrains）：1.7.0.2+
- TraeCode Plugin（VS Code）：1.7.3+

## 企业 Hook（HTTP 类型）
与项目级 Hook（Shell 类型）不同，企业 Hook 是 HTTP 类型：
- Trae 将事件数据以 POST 请求发送到指定 HTTP 端点
- 端点返回 JSON 结果决定是否附加上下文/拦截/继续
- 在企业控制台配置：`企业配置 > 企业 Hooks`

### 支持事件
- SessionStart / UserPromptSubmit / PreToolUse / PostToolUse / Stop / Notification

### 适用场景
- 敏感操作上报到企业风控服务
- 统一审批或拦截
- 跨项目统一规范检查

## 其他企业版能力
- **企业智能体** — 企业专属智能体配置
- **企业文档集** — 内置文档作为 AI 对话上下文
- **SOLO 模式**
- **技能（Skill）** — 企业级技能管理
- **项目级 MCP Server**
- **Token 用量限额** — 按模型或人均维度配置
- **成员与权限管理**
- **资源用量监控**
- **企业级数据可视化看板**
- **企业内部 AI 模型接入**
- **SSO 登录**
- **审计日志**

## 个人版 vs 企业版
| 能力 | 个人版 | 企业版 |
|------|--------|--------|
| IDE 核心能力 | ✅ | ✅ |
| 自定义 Agent/Skill/Rules | ✅ | ✅ |
| 项目级 Hook（Shell） | ✅ | ✅ |
| 企业 Hook（HTTP） | ❌ | ✅ |
| 企业智能体 | ❌ | ✅ |
| 企业文档集 | ❌ | ✅ |
| 企业 MCP 管理 | ❌ | ✅ |
| Token 限额 | ❌ | ✅ |
| 成员/权限/审计 | ❌ | ✅ |
| 企业模型接入 | ❌ | ✅ |

## 创建企业 Hook
1. 准备 HTTP 服务端点（可被 Trae 访问）
2. 登录企业控制台 > 企业配置 > 企业 Hooks
3. 找到目标事件 > 编辑
4. 填入 Hook 配置 > 保存
5. 启用该 Hook 事件

## 注意
- 阻塞主流程的 Hook 如果服务端不可访问/超时/异常，会阻塞用户问答
- 需保障 Hook 服务端点稳定性和可用性
