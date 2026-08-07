---
inclusion: manual
description: Graphify 知识图谱运行规则，手动 #graphify 引用
---

# Graphify 知识图谱

## 何时用

当 Wiki 膨胀到 30+ 页面时，运行 Graphify 做语义分析，生成交互式知识图谱，发现知识关联和缺口。

当前 Wiki 页面数 < 15，直接读 Wiki 更高效。**等膨胀到 30+ 页面后再运行**。

## 运行方式

在 Trae 对话中输入：

```
/graphify references/llm-wiki/wiki/
```

**不能在终端直接跑**，必须通过 Trae 对话触发。

## 产出

| 文件 | 说明 |
|------|------|
| `graphify-out/GRAPH_REPORT.md` | 核心节点报告 |
| `graphify-out/graph.html` | 交互式图谱 |
| `graphify-out/graph.json` | 可查询数据 |

## 使用规则

- 运行后 Agent 优先读 `graphify-out/GRAPH_REPORT.md`，再决定查哪些 Wiki 文件
- 当前产出保留但不刻意维护（69 节点、86 边、13 个社区）
- 等 Wiki 膨胀到 100+ 页面后定期更新
