# Hook 机制

> 来源：https://docs.trae.cn/ide_automate-actions-with-hooks

## 是什么
Hook 是 Trae IDE 的自动化扩展机制，在智能体执行过程的特定事件节点运行自定义 Shell 命令，用于：
- 补充上下文
- 执行校验
- 记录日志
- 拦截高风险操作

## 重要说明
Trae **原生支持项目级 Hook**，不需要企业版。配置文件在项目根目录 `.trae/hooks.json`。
企业版额外支持 HTTP Hook（控制台配置，POST 到外部服务）。

## 6 种 Hook 事件

| 事件 | 触发时机 | 主要用途 |
|------|---------|---------|
| SessionStart | 创建 Session 后、第一个对话前 | 初始化环境、注入环境变量、补充上下文 |
| UserPromptSubmit | 用户发送 Query 后、Agent 处理前 | 拦截请求、附加上下文 |
| PreToolUse | Agent 发起工具调用后、执行前 | 校验、拦截、修改参数、要求确认 |
| PostToolUse | 工具调用执行完成后 | 检查结果、附加上下文 |
| **Stop** | Agent 完成输出、准备结束 Query 时 | 检查产出、阻断停止让 Agent 继续 |
| Notification | 工具调用等待确认或任务完成时（异步） | 发送通知（不阻塞主流程） |

## Hook 类型
| 类型 | 生效范围 | 配置位置 |
|------|---------|---------|
| 全局 Hook | 本机当前用户所有工作区 | `~/.trae/hooks.json` |
| 项目 Hook | 当前项目/工作区 | `<项目根>/.trae/hooks.json` |

## 配置格式
```json
{
  "hooks": {
    "事件名": [
      {
        "name": "hook名称",
        "enabled": true,
        "command": "shell命令",
        "matcher": "可选，工具名匹配（PreToolUse/PostToolUse）"
      }
    ]
  }
}
```

## 配置文件位置
- 项目 Hook：`<项目根>/.trae/hooks.json`
- 全局 Hook：`~/.trae/hooks.json`
- 兼容 Claude Code 的 `.claude/hooks.json`（可导入）

## 在 IDE 中管理
1. 设置 > Hooks
2. 选择全局或项目
3. 点击"创建"，确认安全警示后启用
4. Trae 自动创建 `hooks.json` 并启用
5. 可用齿轮图标编辑、开关启用/禁用

## Hook 生命周期
```
Session 创建
  → SessionStart Hook（注入环境变量/上下文）
用户提交 Prompt
  → UserPromptSubmit Hook（拦截/附加上下文）
Agent 调用工具
  → PreToolUse Hook（校验/拦截/修改参数）
  → 工具执行
  → PostToolUse Hook（检查结果/附加上下文）
Agent 完成输出
  → Stop Hook（检查产出，可阻断停止）
异步
  → Notification Hook（发通知）
```

## 适用场景
- **安全合规**：拦截敏感请求、保护关键文件、阻止高风险命令 → UserPromptSubmit / PreToolUse
- **研发流程自动化**：代码格式化、日志审计 → PreToolUse / PostToolUse
- **上下文增强**：会话开始注入背景信息 → SessionStart
- **任务验收**：任务结束前检查产出质量 → Stop
- **工具链联动**：接入脚本/审查/规范检查 → 按需选择

## 兼容 Claude Code
Trae 支持读取 Claude Code 的 Hook 配置。同名事件的输入输出参数可能有差异，导入后需检查调整。

## 当前项目已配置 Hook
参考 `.trae/steering/self-improvement.md` 的"已启用 Hook"表格。
