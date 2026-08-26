# Qoder 官方文档本地知识库

> 抓取日期：2026-08-20
> 来源：https://docs.qoder.com/zh
> 抓取方式：Mintlify 站点支持在任意页面 URL 后加 `.md` 直接取 Markdown 原文，例如
> `https://docs.qoder.com/zh/user-guide/rules.md`。已验证 45+ 次全部成功。
> ⚠️ `llms.txt` 是 gzip 二进制，WebFetch 不解压，此路不通。`sitemap.xml` 和 `docs.json` 均 404。

## 本目录的定位（2026-08-20 策略变更）

**这里是「原文备查层」，不是生效层。** 本目录下的 43 篇文档**不会自动进入模型上下文**，
只在需要精确引用官方原文时按需 Read。

真正生效的是蒸馏产物：

| 层 | 位置 | 何时进上下文 |
|---|---|---|
| **L1 硬约束** | `AGENTS.md`（仓库根） | **每次会话自动** |
| **L2 专题规格** | `.qoder/rules/*.md` | 按 `trigger` 条件引入 |
| **L3 原文备查** | 本目录 + 现场 WebFetch | 只在需要逐字引用时 |

> 停止「抓全部文档」的原因：囤在本地的 md 不会自动被读到 —— 这正是 `.trae/steering/` 六个规范
> 从 Kiro→Trae→Qoder 一次都没生效的同一个失效模式。且本地镜像会随官方更新而过期，
> 而现场抓一页只要几秒。

## ⚠️ 使用本目录前必读

1. **本项目实际运行在 Qoder 上，不是 Trae。**
   `references/llm-wiki/trae-docs/` 是另一个产品（Trae IDE）的文档，**规格不通用**。
   历史上曾把 Trae 文档当成当前环境的规格来用，导致给出的方案（`.trae/rules/`、6 个 hook 事件）全错。
   查扩展机制规格时，**只能查本目录**。

2. **Qoder IDE 与 Qoder CLI 是两个入口，能力不同。**
   - Hooks：IDE/JB 插件支持 **12 个事件** + `command`/`http` 两种类型；CLI 另有单独文档。
     两者**共用同一份配置文件**，但各入口只执行自身支持的事件。
   - Skills / Subagent 的**完整指南写在 CLI 文档下**（IDE 页面只是摘要 + 指向 CLI）。
   - **内置能力集不重叠**：IDE 侧 6 个 skill（`better-harness`/`canvas`/`create-plugin`/
     `create-skill`/`create-subagent`/`vercel-deploy`）与 CLI 侧 11 个内置 skill 完全是两套。
   - 引用规格时必须标明来源是 `ide/` 还是 `cli/`。

3. **✅ 已修正：Rules 支持会话内热更新。**
   ~~配置改动大多需要重启 IDE。Hooks、Skills 均不支持热加载。~~
   官方 `cli/memory` 明确：规则加载后 Qoder 持续监视该文件，编辑后**下一轮即感知，无需重启**。
   Hooks/Skills/MCP/Agent 也各有 reload 命令：
   `/mcp reload` `/plugins reload` `/skills reload` `/agents reload` `/commands`。
   仅少数标注「需重启」的配置项才要重启。

4. **已知文档内部矛盾（以后者为准）**
   | 议题 | 早期落盘说法 | 权威说法 |
   |---|---|---|
   | Skills 同名优先级 | `ide/02-skills.md`：项目级优先 | `cli/10-troubleshoot-loading.md`：**用户级优先** |
   | Rules 类型如何指定 | `ide/01-rules.md`：IDE 界面选择 | `cli/17-memory.md`：**frontmatter `trigger`** |
   | Hooks 事件与类型 | `ide/04-hooks.md`：12 事件、2 类型 | `cli/05-hooks-reference.md`（CLI 侧另有集合） |

## 目录（共 43 篇）

### ide/ — Qoder IDE

| 文件 | 主题 |
|---|---|
| `01-rules.md` | 规则（⚠️ 类型指定以 `cli/17` 为准） |
| `02-skills.md` | Skills（⚠️ 优先级以 `cli/10` 为准） |
| `03-subagent.md` | 自定义智能体 `.qoder/agents/{name}.md` |
| `04-hooks.md` | Hooks（12 事件、settings.json、脚本协议） |
| `05-plugins.md` | Plugins 组合套件 |
| `06-memory.md` | 记忆（长期记忆、主动记忆） |
| `07-knowledge-engine.md` | 知识中心概览 |
| `08-better-harness.md` | Better Harness |
| `09-commands.md` | 指令 |
| `10-mcp.md` | MCP |
| `11-context-mention.md` | @Mention 上下文引用 |
| `12-quest.md` | Quest 概览 |
| `13-knowledge-cards.md` | 知识卡片 |
| `14-tools-and-review.md` | 工具与审查 |
| `15-planning-and-schedule.md` | 规划与定时 |
| `16-repo-wiki.md` | **Repo Wiki + `wiki_plan.yaml` 前置干预** |
| `17-context-and-indexing.md` | 200K 上下文、`.qoderignore`、索引上限 |
| `18-review-and-sandbox.md` | Ultra Review 三视角、沙箱、Shell 主题干扰 |
| `19-quest-task-and-env.md` | Quest 四状态、Fork、Worktree |
| `20-agent-mode.md` | Agent 模式、Revert、自动执行允许列表 |

### cli/ — Qoder CLI（多数机制的权威版本在这里）

| 文件 | 主题 |
|---|---|
| `01-skills.md` | Skills 完整指南 |
| `02-subagent.md` | Subagent 完整指南 |
| `03-rules-and-memory.md` | 规则与记忆（⚠️ 以 `17-memory.md` 为准） |
| `04-config-scope-and-loading.md` | 三个配置范围 + `.qoder/` 目录结构 + 加载排查 |
| `05-hooks-reference.md` | Hooks 参考 |
| `06-permissions.md` | 权限 |
| `07-hooks-guide.md` | Hooks 指南 |
| `08-settings-reference.md` | 配置项、环境变量、文件路径 |
| `09-settings-layering.md` | 5 级优先级 + **深度合并规则** |
| `10-troubleshoot-loading.md` | **Memory/Skills/Agent 未加载排查（优先级权威）** |
| `11-mcp-reference.md` | MCP 5 种传输 + **懒加载省 token** |
| `12-builtins.md` | 内置 5 Subagent + 11 Skills |
| `13-plugins-reference.md` | **插件约定目录 ←→ `.trae/` 映射表** |
| `14-troubleshoot-extensions.md` | 扩展排查 + 6 条自查命令 |
| `15-how-memory-works.md` | 记忆三层面总纲 |
| `16-output-styles.md` | 输出风格 |
| `17-memory.md` | **⭐ rules/AGENTS.md/自动记忆的权威完整规格（245 行）** |
| `18-cli-reference.md` | 全部启动参数与子命令 |
| `19-slash-reference.md` | 斜杠命令全表 + 条件性命令 |
| `20-run-in-scripts.md` | Headless 模式、CI/CD、细粒度工具白名单 |

## 覆盖度

官方导航共 **IDE 52 页 + CLI 59 页 = 111 页**。已抓约 **45 页**，剩余约 **66 页**。

**剩余的基本都是长尾**，不影响本项目决策，需要时现场抓：

| 类别 | 页面 |
|---|---|
| CLI 周边 | `goal-reference` `scheduled-reference` `loop-reference` `loop` `commands` `authentication` `run-tasks` `parallel-tasks` `scheduled-tasks` `troubleshoot-performance` `interface` `custom-models` `network` `statusline` `built-ins` |
| IDE 会话 | `chat/overview` `ask` `browser-agent` `computer-use-agent` `custom-models` `model-tier-selector` `plan-agent` `ultra-review` |
| Quest | `agent-mode` `experts-mode` `goal-driven` `spec-driven` `supabase` `qoder-voice` |
| 其他 | `troubleshooting/*`（4 页）`keyboard-shortcuts` `deeplink` `remote-control` `configure-network-proxy` `qoder-security-guide` `extensions/canvas` |

> 已抓但因策略变更未单独落盘的 4 页，其要点已直接吸收进 `.qoder/rules/qoder-platform.md`：
> `cli/commands`（自定义命令格式、`SKILL.md` 覆盖兄弟文件的坑）、`cli/config-scope`、
> `cli/loop-reference`（`/loop` 参数、`.qoder/loop.md`、预算上限）、
> `quest/spec-driven` + `chat/plan-agent`（Spec 五步流程、`/plan` 显式调用）。
