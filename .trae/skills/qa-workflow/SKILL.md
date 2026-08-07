---
name: "qa-workflow"
description: "QA 事务式工作流：需求分析→测试场景对齐→用例编写→用例评审，4 步串行，每步用户确认后才进下一步。Invoke when user mentions 测试工作流/用例全流程/qa workflow/对齐测试场景, or when starting a new feature test from requirements."
---

# QA 事务式工作流

## 何时使用

- 接到新需求要做测试设计时（需求分析 → 用例输出全流程）
- 用户说"走工作流"、"对齐测试场景"、"完整输出用例"
- 单个 skill（requirements-analysis / test-case-writing / test-case-reviewer）不能覆盖端到端流程时

## 工作流模型（事务式，4 步串行）

```
Step 1: 需求分析       → 产出 requirements-analysis.md
   ↓ [用户确认]
Step 2: 测试场景对齐    → 产出 test-scenarios.md（按模块/优先级/类型分组）
   ↓ [用户确认]
Step 3: 测试用例编写    → 产出 XMind/JSON 用例
   ↓ [用户确认]
Step 4: 测试用例评审     → 产出 review 报告 + 修订记录
   ↓ [用户确认]
✅ 流程结束
```

**关键原则**：每一步结束必须用 `AskUserQuestion` 让用户确认（通过/打回/调整），用户确认前**禁止**进入下一步。这是"事务"语义——要么全部完成，要么在某个 checkpoint 挂起等待。

## 各 Step 详细要求

### Step 1: 需求分析

- 调用 `requirements-analysis` skill
- 产出：`docs/requirements/<需求名>_需求分析.md`
- 准出：范围/风险/待澄清问题明确，用户口头或选项确认"通过"

### Step 2: 测试场景对齐（新增 checkpoint）

- **目的**：把 Step 1 抽象的"测试影响"细化为可对齐的场景清单，避免直接跳到用例编写后才发现理解偏差
- **产出**：`docs/requirements/<需求名>_测试场景.md`
- **格式要求**：按模块分组（如"配置侧/C端算价/分账回归"），每场景标注优先级、类型、覆盖点
- **对齐方式**：用 `AskUserQuestion` 推送场景分类清单，让用户确认覆盖维度是否完整、场景数是否合理、是否有遗漏
- 准出：用户确认"场景清单通过"，记录确认时间

### Step 3: 测试用例编写

- 调用 `test-case-writing` skill
- 产出：`docs/test-cases/<需求名>_测试用例_v<n>.xmind`（或 JSON）
- 准入：Step 2 已确认
- 准出：用例覆盖所有 Step 2 场景，每场景至少 1 个用例

### Step 4: 测试用例评审

- 调用 `test-case-reviewer` skill
- 产出：`docs/test-cases/<需求名>_评审报告.md` + 修订后的用例
- 准入：Step 3 产出已完成
- 准出：评审通过，或用户明确接受当前用例状态

## 状态管理

工作流状态用 todo 列表维护，每个 Step 是一个 todo：

```
[ ] Step 1: 需求分析
[ ] Step 2: 测试场景对齐
[ ] Step 3: 测试用例编写
[ ] Step 4: 测试用例评审
```

进入某 Step 时标记 in_progress，完成并经用户确认后标记 completed。

## 多动作推送选项机制（每个 checkpoint）

每个 Step 结束时，**不要让用户手动敲指令**，用 `AskUserQuestion` 推送选项：
- 通过，进入下一步
- 需要调整（让用户指出调整点）
- 打回到上一步
- 暂停工作流（保存当前状态）

## 工作流产出物索引

每次工作流启动，在产出文档头部维护索引：

```markdown
> QA Workflow: <需求名>
> 当前 Step: Step 2（测试场景对齐）
> Step 1 产出: docs/requirements/xxx_需求分析.md（2026-08-06 确认）
> Step 2 产出: 进行中
```

## 异常处理

- 用户中途要插队做别的任务：暂停当前 Step，标记状态，回来后从挂起 Step 继续
- 信息不全卡在某 Step：在 checkpoint 标注"待澄清"，列清单让用户补全，不强行往下走
- 用户要求跳过某 Step：明确告知风险（跳过 Step 2 容易在 Step 3 才发现理解偏差，返工成本高），但最终尊重用户决定
