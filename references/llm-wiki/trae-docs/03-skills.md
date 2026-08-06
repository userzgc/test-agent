# 技能（Skill）

> 来源：https://docs.trae.cn/ide/skills

## 是什么
技能通过 `SKILL.md` 文件定义，封装指令、脚本和资源，为智能体提供可复用的专业能力。
类似"操作指南"或"用户手册"，按需加载。

## 核心特点
- **结构化**：一个技能对应一个 `SKILL.md`，含任务目标、适用场景、约束、步骤、脚本
- **动态按需加载**：Agent 先扫描所有技能简要描述，仅在判断相关时才加载详细内容，节省 Token
- **与规则的区别**：规则全量加载持续占上下文，技能按需加载
- **与 MCP 的区别**：技能告诉 Agent"怎么做"，MCP 提供"可调用的工具"

## 技能类型
| 类型 | 路径 | 用途 |
|------|------|------|
| 全局技能 | `~/.trae/skills/<name>/SKILL.md` | 跨项目通用规范、通用工具链 |
| 项目技能 | `.trae/skills/<name>/SKILL.md` | 项目业务知识、技术栈约束、与项目 MCP 协同 |

## SKILL.md 文件格式
```
skill-name/
├── SKILL.md        # 必须：核心指令
├── examples/       # 可选：输入/输出示例
├── templates/      # 可选：可复用模板
└── resources/      # 可选：参考文件、运行脚本、素材
```

### SKILL.md 内容结构
```markdown
---
name: 技能名称
description: 简要描述功能和场景
---
# 技能名称
## 描述
## 使用场景
## 指令
## 示例（可选）
```

## 内置技能（部分）
- TRAE-generate-mini-app — 基于 Taro 生成多端小程序
- TRAE-code-review — 代码审查
- TRAE-security-review — 代码安全扫描
- TRAE-debugger — 运行时调试
- skill-creator — 创建新技能

## 优先级
项目技能 (`.trae/skills/`) > 全局技能 (`~/.trae/skills/`) > 内置技能
同名时项目技能优先。

## 管理
- 创建：设置 > Skills > + 创建
- 编辑：点齿轮图标在编辑器打开
- 启用/禁用：开关控制
- 禁用的全局技能不会在项目中加载

## 注意
- 项目技能与 `.agents/skills/` 重名时，`.trae/skills/` 优先
- 内置技能可在项目中被禁用
