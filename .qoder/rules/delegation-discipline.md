---
trigger: model_decision
description: 主会话上下文保护与 subagent 委派纪律。需要通读外部需求材料（Confluence/飞书/长文档/多份材料）、评审整份用例、或派发 requirements-analyst / case-reviewer 时引入。
---

# 委派纪律

主会话的上下文是全流程最稀缺的资源。大材料通读放 subagent，主会话只消费浓缩结论。

## 何时必须委派

| 情况 | 动作 |
|---|---|
| 外部需求材料预计 **>300 行**，或需要通读 **≥2 份**材料做对照 | 派 `requirements-analyst`，主会话**禁止全文 Read** |
| 用例已成型，要通读全文 + 对照需求做评审 | 派 `case-reviewer` |
| 用户直接贴了短文本 / 单份小材料 | **不派**，主会话直接做更快 |

## 派发契约（提示里必须写全）

1. **必填输入**——subagent 第一轮会校验，缺了直接回「失败」：
   - `requirements-analyst`：需求名 + 至少一个需求来源（URL / 文件路径 / 贴的文本）
   - `case-reviewer`：待评审用例文件路径 + 需求分析文档路径
2. 有台账就带上台账路径（`docs/requirements/<需求名>_台账.md`），并注明「台账只读」
3. 一次派发只要一个明确产出；期望回传格式是**三行头**（结果 / 产出 / 需主会话跟进）

## 回传处理

- 先看三行头：「失败」→ 补齐输入重派，不要自己顶上去通读
- **不要重读原文验证**——抽查关键结论即可，重读等于委派白做
- 待澄清问题由**主会话**带用户逐条对齐（subagent 不能和用户对话），结果登记进台账

## 禁止

- ❌ 把需要用户确认的环节派出去（subagent 无法 AskUserQuestion）
- ❌ subagent 二次派发（frontmatter `disallowedTools: [Agent]` 兜底）
- ❌ 派发后主会话又自己去读同一批原文
