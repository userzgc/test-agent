# test-agent

**QA 测试资产库** —— 把「需求 → 需求分析 → 测试用例 → 用例评审」这条链路固化成可复用的
AI 工作流，产出物是文档与 XMind 用例资产。

> 这不是代码仓库。没有 `package.json`，没有可构建/可运行的应用，也没有单元测试。
> 唯一的「代码」是 `scripts/` 下 10 个独立可执行的 Python 工具脚本。

运行平台：**Qoder**（历经 Kiro → Trae → Qoder 三代，扩展资产已全部迁移到 `.qoder/`）。

## 快速开始

### 新成员上手（首次 clone 必做）

1. **填凭据**：`cp config/credentials.json.example config/credentials.json`，填入自己的账号（已 gitignore，不会被提交）
2. **重启 Qoder IDE**：Hooks 不支持热加载，首次打开项目后重启一次才生效
3. **验证 hook 生效**：对话框里让 AI 往 `docs/test-cases/` 写一个 `.md` 文件，被拒绝即正常
4. **跑一条冒烟指令**：输入 `评审这份用例：docs/test-cases/买A赠B二期_测试用例.xmind`，确认能正确路由到 case-reviewer

> ⚠️ **团队约定**：`.qoder/` 下的任何修改 = 修改全员的 agent 行为，请走 PR review；
> 改过 hooks/settings.json 的，在 PR 描述里注明「需重启 IDE」。
> Qoder 本机记忆不随 git 同步，团队要用的口径/经验必须落在仓库内资产（rules / docs）。

### 跑一个完整 QA 工作流

在 Qoder 对话框输入斜杠命令：

```
/qa-flow
```

然后贴上需求文档链接或内容。工作流按 5 个 checkpoint 串行推进，**每步等你确认才进下一步**：

```
Step 1    需求分析        → docs/requirements/<需求名>_需求分析.md
   ↓ [确认]
Step 1.5  判定链路对齐     ≤8 行讲清核心链路，硬 gate，不落文件
   ↓ [确认]
Step 2    测试场景对齐     对齐场景清单，纯对话，不落文件
   ↓ [确认]
Step 3    测试用例编写     → docs/test-cases/<需求名>_测试用例.xmind
   ↓ [确认]
Step 4    测试用例评审     → docs/test-cases/<需求名>_用例评审报告.md
```

**对齐阶段一律不落中间态 md** —— 理解还在偏差期就写文件必然返工，只在结论稳定后落盘一次。
Step 1.5 是不能跳的硬 gate：链路错一环，Step 2 的几十条场景全部作废。

用例评审通过后，用 `/exec-plan` 制定执行计划与数据准备清单。

### 单步使用

不走全流程时直接说人话，对应 Skill 会自动触发：

| 你想做什么 | 对话框输入 |
|---|---|
| 分析需求 | `分析这个需求：[Confluence 链接 / 内容]` |
| 提取设计稿测试点 | `分析这个设计稿：[蓝湖/墨刀链接 或 图片路径]` |
| 生成 XMind 用例 | `生成 XMind 用例` |
| 评审用例 | `评审这份用例：docs/test-cases/xxx.xmind` |
| 禅道补工时 | `补录工时` |

## 能力一览

### 自定义命令（2 个）

位于 `.qoder/commands/<name>.md`。

| 命令 | 用途 |
|---|---|
| `/qa-flow` | 启动 QA 事务式工作流（5 个 checkpoint 串行，逐步确认） |
| `/exec-plan` | 承接已评审用例，产出执行计划与数据准备清单 |

### Subagent（2 个）

位于 `.qoder/agents/<name>.md`（单文件格式）。适合「读得多、写得少」的重上下文场景。

| Subagent | 何时派它 |
|---|---|
| `requirements-analyst` | 需求材料多，要通读 Confluence / 飞书 / 蓝湖 原文 |
| `case-reviewer` | 用例已成型，要通读用例全文 + 需求分析做对照评审 |

> ⚠️ Subagent **无法与用户对话**。需要你确认口径的环节不要派出去 ——
> 这也是「制定执行计划」做成 `/exec-plan` 命令而非 subagent 的原因。

### Skill（8 个）

位于 `.qoder/skills/<name>/SKILL.md`，按 description 里的触发词自动激活。

| Skill | 触发词 |
|---|---|
| `qa-workflow` | 测试工作流、用例全流程、对齐测试场景 |
| `requirements-analysis` | 需求分析、requirements analysis |
| `test-case-writing` | 编写测试用例、test case writing |
| `test-case-reviewer` | 测试用例评审、test case review |
| `functional-testing` | 功能测试、测试方案设计 |
| `design-extraction` | 设计稿、原型稿、截图识别、UI 提取 |
| `tool-usage` | 工具调用、Confluence、飞书、YAPI、脚本 |
| `zentao-operation` | 禅道、拆任务、补工时 |

### 规则（4 条）

位于 `.qoder/rules/*.md`，按场景自动引入（**支持热更新**）。

| 规则 | 何时生效 |
|---|---|
| `qoder-platform.md` | 新建/修改 Qoder 扩展资产，或排查「配置不生效」 |
| `test-case-authoring.md` | 读写 `docs/test-cases/**` |
| `failure-protocol.md` | 工具调用失败 / 空数据 / 格式不符需要处置 |
| `memory-discipline.md` | 要记业务口径、被纠正的理解、关键决策 |

### Hooks（3 个）

脚本在 `.qoder/hooks/`，注册在 `.qoder/settings.json`。

| 事件 | 脚本 | 作用 | 状态 |
|---|---|---|---|
| `SessionStart` | `session-start.sh` | 注入项目现状（用例数、脚本、凭据状态）与开工提醒 | ✅ 已实测 |
| `PreToolUse` | `block-md-testcase.sh` | 拦截往 `docs/test-cases/` 写 `.md` 交付物 | ✅ 已实测 |
| `PostToolUseFailure` | `post-tool-failure.sh` | 工具级失败时注入处置协议 | ⚠️ 未实测 |

`block-md-testcase.sh` 白名单：文件名含「评审报告 / 评审 / 说明 / review」或 `README.md` 的放行
（评审报告是给人读的合法 md 产物）。

> ⚠️ **Hooks 不支持热加载**，改 `.qoder/settings.json` 后必须重启 IDE。
> ⚠️ shell 命令返回非零退出码**不触发** `PostToolUseFailure` —— 终端工具本身是成功的
> （它成功执行了命令并捕获了报错），走的是 `failure-protocol.md` 规则兜底。

### 脚本工具（10 个）

全部在 `scripts/`，独立可执行，纯 Python 标准库为主（OCR / Playwright 需按需安装）。

| 脚本 | 用途 | 用法 |
|---|---|---|
| `gen_xmind.py` | JSON 场景树 → XMind | `python3 scripts/gen_xmind.py <input.json> <output.xmind>` |
| `parse_xmind.py` | XMind/JSON → 树形文本 | `python3 scripts/parse_xmind.py <input> [--output <out.txt>]` |
| `md_to_xmind_tree.py` | Markdown → XMind 树 JSON | `python3 scripts/md_to_xmind_tree.py <input.md> <output_tree.json>` |
| `gen_buyagiftb_xmind.py` | 买A赠B二期场景树直构 | `python3 scripts/gen_buyagiftb_xmind.py` |
| `gen_adbanner_xmind.py` | 资源位关联商品场景树直构 | `python3 scripts/gen_adbanner_xmind.py` |
| `parse_yapi.py` | 解析 YAPI 导出的 Markdown | `python3 scripts/parse_yapi.py <input.md> [--output <out.json>]` |
| `parse_feishu.py` | 解析飞书导出的 CSV | `python3 scripts/parse_feishu.py <input.csv> [--output <out.json>] [--group-by <字段>]` |
| `extract_confluence_images.py` | 下载 Confluence 页面图片 | `python3 scripts/extract_confluence_images.py <pageId> [--output <dir>]` |
| `ocr_images.py` | 目录批量图片 OCR | `python3 scripts/ocr_images.py <image_dir> [--lang <lang>]` |
| `zentao_login.py` | 禅道登录 / session 管理 | `python3 scripts/zentao_login.py {login\|check\|screenshot}` |

`gen_buyagiftb_xmind.py` 与 `gen_adbanner_xmind.py` 是把已确认口径硬编码成场景树的一次性生成器，
口径来源写在各自文件头部注释里。

## 项目结构

```
test-agent/
├── AGENTS.md                # 项目说明，每次会话自动注入 ★ 改动前先读
├── .qoder/                  # ← 当前生效的扩展资产
│   ├── settings.json        #   hooks 注册
│   ├── rules/               #   4 条规则（热更新）
│   ├── skills/<name>/SKILL.md   #   8 个 Skill
│   ├── agents/<name>.md     #   2 个 Subagent（单文件）
│   ├── commands/<name>.md   #   2 个命令：qa-flow、exec-plan
│   ├── hooks/*.sh           #   3 个 hook 脚本
│   └── repowiki/            #   ⛔ 生成于 Trae 时代，内容已过期
├── docs/                    # 产出物
│   ├── requirements/        #   需求分析 + <需求名>_设计图/ 图片
│   ├── test-cases/          #   XMind 用例 + 评审报告
│   ├── reports/             #   测试知识库 / 报告
│   ├── api-reference/       #   接口清单 CSV
│   ├── historical-cases/    #   历史用例归档
│   ├── interface-matrix.csv
│   ├── lessons-learned.md   #   历史台账（不自动加载）
│   └── memory/              #   历史台账（不自动加载）
├── scripts/                 # 10 个工具脚本
├── config/credentials.json  # 凭据（已 gitignore）
├── references/              # 外部参考资料（只读）
│   ├── qoder-docs/          #   Qoder 官方文档镜像（41 篇，按需查证）
│   ├── llm-wiki/            #   Quarto 知识库 + Trae 文档镜像（21 篇）
│   └── yapi-oss-api.md
└── .trae/                   # ⛔ 纯归档，无活文件
```

### 执行链路

```
用户输入（/qa-flow 或自然语言）
  │
  ├─ SessionStart hook 已注入项目现状
  ▼
Skill 按触发词激活 + Rules 按场景引入
  │
  ├─ 材料多且无需对话 → 派 Subagent 通读
  ▼
调用 scripts/ 脚本产出 → 落 docs/
  │
  ├─ PreToolUse hook 拦截违规格式（docs/test-cases/*.md）
  ▼
业务口径 / 踩坑 → UpdateMemory 落 Qoder 原生记忆
```

## 交互铁律

1. **涉及测试用例产出时，先用 `AskUserQuestion` 确认输出格式**，默认推荐 XMind 场景树。
   禁止不问就输出 Markdown 用例文档。
2. **有 ≥2 个后续动作时，用 `AskUserQuestion` 推送选项**，不要让用户手打数字回复。
3. **记忆落 Qoder 原生记忆（`UpdateMemory`），不是写 md**。
   只写进 `docs/` 下的 md 等于没记 —— 没有任何机制保证它会被读到。

## 质量约束

- 用例编写前必须先完成需求分析
- 用例编写后必须经过评审才能标记为最终版
- 评审发现的问题必须修改后重新生成
- XMind 场景树遵循「大类 → 小场景 → 数据/预期」，不带字段头（参考城市徽章 v2 风格）

## 已有资产

| 需求 | 需求分析 | 用例 | 评审报告 |
|---|---|---|---|
| 买A赠B二期 | ✅ | ✅ 测试用例 + 冒烟 | ✅ |
| 资源位关联商品 | ✅ 设计图字段说明 | ✅ 测试用例 + 冒烟 | — |
| 品牌投放H5 | ✅ | — | — |
| 雪王游南方·点亮城市徽章 | — | ✅ v2 | — |
| 买A赠B一期 | — | ✅（JSON，历史格式） | — |

其他：`docs/reports/` 下 3 篇买A赠B测试知识库；`docs/historical-cases/城市徽章_v1.xmind`。

## 已知待办

- `ORDER-07`（关联商品不在该门店餐单中）待产品确认，用例中标记为悬挂项。
- Qoder 迁移的全部改动尚未提交（最后一个 commit `d45aec5` 仍是 Trae 时代）。
- MCP 未配置（仓库根无 `.mcp.json`）。
- `references/{llm-wiki/wiki}/` 是一次 shell 花括号展开失误留下的空目录，待清理。

## ⛔ 别拿过期信息源当现状

| 来源 | 为什么不能信 |
|---|---|
| `.trae/**` | 纯归档。里面的 `.trae/agents/<name>/agent.md`、`.trae/mcp.json` 等格式在 Qoder 下全是错的 |
| `.qoder/repowiki/**` | 生成于 Trae 时代 commit（2026-08-17），通篇按 `.trae/` 目录、「6 Agent / 7 Skill」描述架构 |
| `docs/lessons-learned.md`、`docs/memory/**` | 历史台账，写的是当时的旧路径，且不会自动加载 |

判断架构请直接看文件系统，或以 `AGENTS.md` 为准。
新建/修改扩展资产前**先读 `.qoder/rules/qoder-platform.md`** —— 三代格式互不兼容，这是踩过的坑。
