# 自改进机制

## 机制概述

通过 Trae 原生 Hook 机制实现自动化自改进：
- `Stop` 事件触发：自动检查本次会话是否有踩坑经验需要记录、是否有业务口径需要沉淀
- `SessionStart` 事件触发：自动加载项目上下文摘要 + 记忆索引
- `PostToolUse` 事件触发：工具调用后做特定检查（如飞书授权）

## 两套并行的沉淀体系

| 体系 | 落在哪 | 记什么 | 规则文件 |
|------|--------|--------|---------|
| **踩坑** | `docs/lessons-learned.md` | 我们做错了什么、根因、怎么避免 | 本文件 |
| **记忆** | `docs/memory/`（decisions / sessions / index） | 业务口径是什么、下次同类需求直接复用 | `.trae/skills/memory-keeping/SKILL.md` |

两者**不要互相复制**：同一事项只写一边。判断依据是“这条是我们的教训，还是业务的事实”。

> 硬约束：Hook **无法感知对话内容**，所以踩坑和记忆都不可能自动录制。Hook 只能做两件事：SessionStart 加载已有沉淀、Stop 输出检查清单提醒 Agent 自查。实际写入必须由 Agent 主动完成。

## Hook 配置

配置文件：`.trae/hooks.json`
脚本目录：`.trae/hooks/`

### 已启用 Hook

| Hook 名 | 事件 | 作用 | 脚本 |
|---------|------|------|------|
| auto-check-lessons-learned | Stop | 输出双清单：踩坑记录 + 记忆沉淀 | `.trae/hooks/on-stop-check-lessons.sh` |
| error-detect-lessons | PostToolUse | RunCommand 返回错误时强提醒记录踩坑 | `.trae/hooks/post-tool-error-detect.sh` |
| load-project-context | SessionStart | 加载项目上下文 + 记忆索引最近 3 条 | `.trae/hooks/session-start.sh` |
| check-feishu-auth | PostToolUse | 飞书授权检查（默认禁用） | `.trae/hooks/post-tool-feishu-auth.sh` |

## 踩坑识别流程

```
用户提问 → Agent 执行任务
              │
              ├── 工具调用失败（401/超时/连接失败）
              │   → ⚠️ 必须当场记录踩坑到 docs/lessons-learned.md
              │   → 通知用户（AskUserQuestion 推送选项）
              │   → 不跳过继续推进，先处理失败
              │
              └── 任务完成 → Stop 事件触发
                                │
                                ▼
                   on-stop-check-lessons.sh 执行
                                │
                    ▼                       ▼
            今日已有 N 条               今日 0 条
            → 输出检查清单              → 输出检查清单
            + 今日已N条               （每次都提醒）
                                    │
                                    ▼
                            Agent 读取清单，判断：
                            ├── 有踩坑 → 按格式追加到 docs/lessons-learned.md
                            │           → 判断是否更新 wiki / agent / skill / script
                            └── 无踩坑 → 忽略提醒
```

### 即时记录规则（最高优先级，不可跳过）

**工具调用失败时必须当场记录踩坑，不等 Stop Hook，不等用户提醒**：

这是**硬性规则**，违反属于最严重的执行偏差。执行顺序如下：

```
工具调用 → 返回错误（401/403/timeout/Unauthorized/连接失败/空数据/异常）
  │
  ▼ 【必须】下一步操作只能是记录踩坑
  │
  ├─ 1. 当场写入 docs/lessons-learned.md（按格式）
  ├─ 2. 分析根因
  ├─ 3. 通知用户（AskUserQuestion 推送选项：记录踩坑 / 更新skill / 继续推进）
  └─ 4. 用户确认后才继续推进任务
```

**绝对禁止的行为**：
- ❌ 工具失败后跳过，转而给方法论建议
- ❌ 不记录踩坑就继续推进任务
- ❌ 等用户批评后才补记
- ❌ 一次会话累积多个坑后才批量记录
- ❌ 把"记录踩坑"当作可选步骤

**判断标准**：如果工具调用的返回结果不符合预期（报错、空数据、401、超时、格式不对），就是"失败"，必须记录。

## 踩坑识别标准

**以下场景必须记录踩坑**：
- 需求分析遗漏关键点，被用户纠正
- 用例评审发现覆盖盲区
- **脚本/工具执行失败（401/超时/连接失败）→ 当场记录，不等 Stop Hook**
- 工具调用方式与文档不一致
- 业务规则理解偏差
- 流程中某个环节反复出错
- Agent 能力缺失，需要补充脚本或工具
- **跳过错误继续推进任务 → 回头补记踩坑**

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
2. **记忆** — `docs/memory/decisions.md` 是否有需要沉淀的业务口径（详见 memory-keeping skill）
3. **Agent** — `.trae/agents/*/agent.md` 能力定义是否需要修改
4. **Skill** — `.trae/skills/*/SKILL.md` 是否需要补充
5. **脚本** — `.trae/scripts/` 是否需要新增/修改工具脚本
6. **Hook** — `.trae/hooks.json` 或 `.trae/hooks/` 是否需要新增检查规则

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
