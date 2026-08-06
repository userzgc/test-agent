# 自改进机制

## 机制概述

通过 Trae 原生 Hook 机制实现自动化自改进：
- `Stop` 事件触发：自动检查本次会话是否有踩坑经验需要记录
- `SessionStart` 事件触发：自动加载项目上下文摘要
- `PostToolUse` 事件触发：工具调用后做特定检查（如飞书授权）

## Hook 配置

配置文件：`.trae/hooks.json`
脚本目录：`.trae/hooks/`

### 已启用 Hook

| Hook 名 | 事件 | 作用 | 脚本 |
|---------|------|------|------|
| auto-check-lessons-learned | Stop | 检查踩坑记录 | `.trae/hooks/on-stop-check-lessons.sh` |
| load-project-context | SessionStart | 加载项目上下文 | `.trae/hooks/session-start.sh` |
| check-feishu-auth | PostToolUse | 飞书授权检查（默认禁用） | `.trae/hooks/post-tool-feishu-auth.sh` |

## 踩坑识别流程

```
用户提问 → Agent 执行任务 → Stop 事件触发
                                │
                                ▼
                   on-stop-check-lessons.sh 执行
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
            今日已有记录               今日无记录
            → 静默通过              → 输出检查清单
                                    │
                                    ▼
                            Agent 读取清单，判断：
                            ├── 有踩坑 → 按格式追加到 docs/lessons-learned.md
                            │           → 判断是否更新 wiki / agent / skill / script
                            └── 无踩坑 → 忽略提醒
```

## 踩坑识别标准

**以下场景必须记录踩坑**：
- 需求分析遗漏关键点，被用户纠正
- 用例评审发现覆盖盲区
- 脚本/工具执行失败，找到根因
- 工具调用方式与文档不一致
- 业务规则理解偏差
- 流程中某个环节反复出错
- Agent 能力缺失，需要补充脚本或工具

**以下场景不需要记录**：
- 简单的代码语法错误（已修复且非系统性问题）
- 用户临时性问题（与项目无关）
- 已有踩坑记录的重复问题

## 踩坑记录格式

追加到 `docs/lessons-learned.md`（按时间倒序，最新在上）：

```markdown
## YYYY-MM-DD 场景简述
- **问题**：具体发生了什么
- **根因**：为什么发生
- **解决方案**：怎么解决的
- **关联文件**：涉及的代码/文档路径
- **知识库更新**：更新了哪些 wiki 页面（无则填"无"）
- **Agent更新**：更新了哪些 agent/skill（无则填"无"）
- **脚本更新**：新增/修改了哪些脚本（无则填"无"）
```

## 更新流程

记录踩坑后，按以下顺序检查是否需要更新：

1. **知识库** — `references/llm-wiki/wiki/` 对应页面是否需要补充
2. **Agent** — `.trae/agents/*/agent.md` 能力定义是否需要修改
3. **Skill** — `.trae/skills/*/SKILL.md` 是否需要补充
4. **脚本** — `.trae/scripts/` 是否需要新增/修改工具脚本
5. **Hook** — `.trae/hooks.json` 或 `.trae/hooks/` 是否需要新增检查规则

## 更新原则

- **小步迭代**：每次只更新与当前问题直接相关的内容，不扩大范围
- **就地更新**：直接修改 agent.md / SKILL.md / wiki，不创建新版本文件
- **保持引用一致**：更新脚本路径后，所有 agent.md 中的引用同步修改
- **验证可用**：新增脚本必须自测验证后再写入 agent.md
- **记录变更**：在 `docs/CHANGELOG.md` 记录本次自改进的内容

## 新增 Hook 流程

1. 在 `.trae/hooks/` 新建 `.sh` 脚本
2. 在 `.trae/hooks.json` 对应事件下添加配置
3. `chmod +x` 脚本
4. 手动执行一次验证脚本输出
5. 在本文件的"已启用 Hook"表格中记录

## 禁止

- ❌ 不要在没有明确根因的情况下盲目修改 agent/skill
- ❌ 不要为了"完善"而添加未经验证的内容
- ❌ 不要创建冗余的新文件，优先更新现有文件
- ❌ 不要用 AI 自觉代替 Hook 自动检查，Hook 是第一道防线
