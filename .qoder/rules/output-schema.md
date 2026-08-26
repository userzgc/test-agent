---
trigger: always_on
---

# 产出物格式矩阵（唯一权威）

任何产物只有一种合法格式与落位。其他文件与本表冲突时，**以本表为准**。

| 产物 | 唯一格式 | 落位 | 禁止 |
|---|---|---|---|
| 需求分析 | `.md` | `docs/requirements/<需求名>_需求分析.md` | — |
| 需求台账 | `.md`（**只追加，不改写历史**；模板见 `docs/requirements/_台账模板.md`） | `docs/requirements/<需求名>_台账.md` | — |
| 测试用例 | `.xmind`（直构 JSON → `scripts/gen_xmind.py`） | `docs/test-cases/` | ❌ `.md` / `.txt` 用例（hook 强制拦截） |
| 评审报告 | `.md`（文件名须含「评审」，走 hook 白名单） | `docs/test-cases/` | — |
| 执行计划 / 测试报告 / 知识库 | `.md` | `docs/reports/` | — |
| 使用日志 | `.csv`（SessionStart hook 自动追加，只追加不改历史行） | `docs/usage-log.csv` | ❌ 手工编造 / 删改历史行 |
| 中间产物（解析文本、草稿、脚本临时输出） | 任意 | `/tmp/` | ❌ 任何 `docs/` 目录 |

## 硬规则

1. 用例产出前先用 `AskUserQuestion` 确认格式，默认推荐 **XMind 场景树**；未经确认禁止输出 md 用例
2. 禁止新建 per-需求生成脚本，一律「直构 JSON + `scripts/gen_xmind.py`」（XMind 即源）
3. md 文档必须精简：结论先行、表格优先、不复制需求原文（写来源引用：pageId+version / doc token+rev）
4. 落位不在上表内的新产物类型，先问用户落位，再补进本表——不许现场发明目录
