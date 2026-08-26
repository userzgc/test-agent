# 项目说明

## 这是什么项目

**QA 测试资产库**，不是代码仓库。核心链路是：需求 → 需求分析 → 测试用例 → 用例评审。
没有可构建、可运行的应用；不要试图找 `package.json`、跑测试、起服务。

产出物是**文档与用例资产**，主要格式是 **XMind**。

## 运行平台：Qoder

本项目历经 Kiro → Trae → **Qoder** 三代工具。当前运行在 **Qoder**。

**已完成迁移（生效中）**：

| 资产 | 位置 | 内容 |
|---|---|---|
| 项目说明 | `AGENTS.md` | 本文件，每次会话自动注入 |
| 规则 | `.qoder/rules/*.md` | 4 篇，见下方导航 |
| Skills | `.qoder/skills/<name>/SKILL.md` | 8 个 |
| Subagent | `.qoder/agents/<name>.md` | 2 个（单文件） |
| 自定义命令 | `.qoder/commands/<name>.md` | 2 个：`/qa-flow`、`/exec-plan` |
| 脚本工具 | `scripts/*.py`（仓库根） | 10 个，显式调用 |
| 凭据 | `config/credentials.json` | 已 gitignore |
| Hooks | `.qoder/settings.json` + `.qoder/hooks/*.sh` | 3 个，已生效 |
| MCP | — | **未配置**，仓库根没有 `.mcp.json`，需要时新建 |

## ⛔ 三个「过期信息源」，别拿它们当现状

本项目历史包袱重，有三处内容看起来权威、实际全是 Trae 时代快照：

| 来源 | 状态 | 风险 |
|---|---|---|
| `.trae/**` | 纯归档，**一个活文件都没有** | 有 Trae 机制速查表（`.trae/agents/<name>/agent.md`、`.trae/mcp.json`），Qoder 下全是错的，照抄直接写出加载不了的配置 |
| `.qoder/repowiki/**` | 生成于 commit `d45aec5`（2026-08-17，**Trae 时代**） | 通篇按 `.trae/` 目录、「6 个 Agent / 7 个 Skill」描述架构，与现状不符 |
| `docs/lessons-learned.md`、`docs/memory/**` | 历史台账，**不会自动加载** | 里面写的是当时的旧路径（`.trae/scripts/`、`.trae/settings/credentials.json`），作为台账没错，但别当现状 |

遇到这三处与本文件冲突时，**以本文件 + 实际文件系统为准**。
RepoWiki 里的架构描述、以及注入上下文里那几张 Knowledge Card 同理 —— 判断架构请直接 `ls`。

> 路径迁移对照：`.trae/scripts/` → `scripts/`；`.trae/settings/credentials.json` → `config/credentials.json`。

⚠️ Qoder 迁移的全部改动**尚未提交**（`d45aec5` 之后无新 commit）。

⚠️ 需要新建或修改任何扩展资产时，**先读 `.qoder/rules/qoder-platform.md`**，
不要凭 Trae/Kiro/Claude Code 的经验推测格式 —— 三代格式互不兼容，这是已经踩过的坑。

## 工作入口

| 命令 | 用于 |
|---|---|
| `/qa-flow` | 启动完整 QA 工作流（需求分析 → 链路对齐 → 场景对齐 → 用例编写 → 评审） |
| `/exec-plan` | 用例评审通过后，制定执行计划与数据准备清单 |

两个 subagent（**注意：它们无法与用户对话**，不要把需要你确认的环节派出去）：

- `requirements-analyst` —— 需求材料多、要通读 Confluence/飞书时派它
- `case-reviewer` —— 用例已成型，要通读全文做评审时派它

## 交互铁律

### 1. 涉及测试用例产出时，先确认输出格式

用 `AskUserQuestion` 问，**默认推荐 XMind 场景树**。

❌ 禁止不问就输出 Markdown 用例文档。
（实证：2026-08-06 直出 63 条 MD 用例，用户反馈「MD 没人看，直接输出 XMind」。）

### 2. 有 ≥2 个后续动作时，用 AskUserQuestion 推送选项

❌ 禁止用文字罗列选项让用户手打数字回复。
（实证：用户反馈「搞个选择框，不然我每次都要重新给你打字」。）

单个动作、或用户已明确指令时，不要多问。

### 3. 记忆落 Qoder 原生记忆，不是写 md

业务口径、被纠正的理解、踩坑 —— 用 `UpdateMemory`。
只写进 `docs/` 下的 md = 等于没记（没任何机制保证会被读到）。详见 `memory-discipline.md`。

## 文件落位

| 内容 | 位置 |
|---|---|
| 测试用例（`.xmind` 为主） | `docs/test-cases/` |
| 需求分析（含 `<需求名>_设计图/` 图片目录） | `docs/requirements/` |
| 测试报告 / 知识库 | `docs/reports/` |
| 接口清单 | `docs/interface-matrix.csv`、`docs/api-reference/ssos-接口清单.csv` |
| 历史案例 | `docs/historical-cases/` |
| 历史台账（不自动加载，需要时手动读） | `docs/lessons-learned.md`、`docs/memory/` |
| 外部参考资料（只读，勿当作本项目产出） | `references/` |
| 脚本工具 | `scripts/` |
| 凭据 | `config/credentials.json` |
| 历史归档 / 过期快照（勿参照，见上文） | `.trae/`、`.qoder/repowiki/` |
| 临时文件 | `/tmp/`，不污染项目目录 |

凭据在 `config/credentials.json`（已 gitignore）。代码中不硬编码密码，
引用时每次从文件读，不要从记忆里取。

## 质量约束

- 用例编写前必须先完成需求分析
- 用例编写后必须经过评审才能标记为最终版
- 评审发现的问题必须修改后重新生成

## 已知待办

- `ORDER-07`（关联商品不在该门店餐单中）待产品确认，用例中标记为悬挂项。

## 规则导航

`.qoder/rules/` 下的专题规格，按需自动引入：

| 文件 | 何时生效 |
|---|---|
| `qoder-platform.md` | 需要新建/修改 Qoder 扩展资产时 |
| `test-case-authoring.md` | 读写 `docs/test-cases/**` 时 |
| `failure-protocol.md` | 工具调用失败需要处置时 |
| `memory-discipline.md` | 要记业务口径 / 被纠正的理解时 |

原始官方文档镜像在 `references/qoder-docs/`（41 篇，按需查证，非自动加载）。

## ⚠️ 本文件的效力边界

官方明确：项目说明是**上下文，不是强制策略**。下面的硬约束按职责分工兜底：

| 约束 | 兜底手段 | 行为 | 验证状态 |
|---|---|---|---|
| 禁止在 `docs/test-cases/` 下写 `.md` 交付物 | `PreToolUse` + `deny` hook | **直接写不进去** | ✅ 已实测生效（指纹 B9K2） |
| 真实工具失败（fetch 拿 401/403、超时、MCP 崩） | `PostToolUseFailure` hook | 注入处置协议 | ⚠️ 未实测（shell 非零退出不触发） |
| shell 命令非零退出 / 空数据 / 格式不符 | `failure-protocol.md` 规则 | 模型按协议处置 | ✅ 已实测生效 |

> ⚠️ **关键区分**：一条 shell 命令返回非零退出码，**不算「工具调用失败」**——
> `run_in_terminal` 工具本身成功了（它成功跑了命令并捕获了报错），触发的是 `PostToolUse`，
> 不是 `PostToolUseFailure`。所以命令失败的处置靠 `failure-protocol.md` 规则，不靠 hook。

脚本在 `.qoder/hooks/`，注册在 `.qoder/settings.json`。

**白名单**：文件名含「评审报告 / 评审 / 说明 / review」或 `README.md` 的放行
（评审报告是给人读的合法 md 产物）。

⚠️ **Hooks 不支持热加载，改 `.qoder/settings.json` 后必须重启 IDE 才生效。**
（Rules 相反，是自动热更新的。）
