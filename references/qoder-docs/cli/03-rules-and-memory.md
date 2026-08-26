# 规则与记忆（Qoder CLI，权威版）

> 来源：https://docs.qoder.com/zh/cli/memory + https://docs.qoder.com/zh/cli/how-memory-works
> ⚠️ **这一篇修正了 `ide/01-rules.md` 的说法**：官方原话「Qoder CLI 的 rules frontmatter
> **兼容 Qoder Desktop 中配置的 rules 设置**；从 Qoder Desktop 同步或复制的规则文件可以继续使用原有触发配置。」
> 也就是说 **rules 的生效方式可以直接写在 frontmatter 里，不必只靠 IDE 设置界面点选**。

## 三层信息模型

| 层面 | 生命周期 | 谁维护 | 典型内容 |
|---|---|---|---|
| 对话上下文 | 当前会话内 | Qoder 自动累积 | 历史消息、工具调用、结果 |
| **项目说明**（静态记忆） | 长期，随项目 | 你或团队 | `AGENTS.md`、`rules/` |
| **长期记忆**（自动记忆） | 长期，跨会话 | 团队约定 + 可选自动记忆 | 偏好、项目背景、外部资料位置 |

> 记忆是**提供给模型的上下文，不是强制策略**。要硬性阻止某类命令/工具/路径，必须用
> **权限配置**或 **Hooks**——这一条直接决定了本项目「防复发」该落在哪一层。

## 静态记忆文件位置

```text
~/.qoder/AGENTS.md                 # 用户跨项目偏好，不提交
<project>/AGENTS.md                # 团队共享项目规则，提交
<project>/AGENTS.local.md          # 本机私有说明，不提交
<project>/.qoder/rules/**/*.md     # 按主题拆分的项目规则，提交
~/.qoder/rules/**/*.md             # 用户级规则，不提交
```

可用 `context.fileName` 改默认文件名（默认 `AGENTS.md`，支持数组）。

### 加载逻辑（向上查找）

从当前工作目录向父目录逐层查找 `AGENTS.md` / `AGENTS.local.md` / `.qoder/rules/**/*.md`，
**默认到 `.git` 所在目录为止**（`context.memoryBoundaryMarkers`）。

在 `/repo/packages/app` 启动时会检查：
```text
/repo/packages/app/AGENTS.md
/repo/packages/app/.qoder/rules/*.md
/repo/packages/AGENTS.md
/repo/packages/.qoder/rules/*.md
/repo/AGENTS.md
/repo/.qoder/rules/*.md
```

**子目录记忆启动时不预加载**——只有实际读取了子目录里的文件后，才会从该文件所在目录向上补齐。

## ⭐ Rules frontmatter 四种生效方式

没有配置加载相关 frontmatter 时**默认始终生效**；`trigger` 存在时**优先于** `alwaysApply`。

| 生效方式 | 配置 | 加载行为 |
|---|---|---|
| **始终生效** | 不写 frontmatter，或 `trigger: always_on`，或 `alwaysApply: true` | 启动/刷新记忆时加载正文 |
| **手动引入** | `trigger: manual` 或 `alwaysApply: false` | 不自动注入正文 |
| **模型决策** | `trigger: model_decision` + **非空 `description`** | 只注入路径和说明，模型判断相关时再读正文 |
| **指定文件生效** | `trigger: glob` + `glob`，或直接 `paths` | 访问匹配文件后按需加载正文 |

⚠️ `model_decision` 缺 `description`、`glob` 缺 `glob` 时，**规则正文不会自动注入**。

### Frontmatter 可配置项全表

| 配置项 | 可用值 | 说明 |
|---|---|---|
| `trigger` | `always_on` / `manual` / `model_decision` / `glob` | 生效方式 |
| `alwaysApply` | `true` / `false` | 兼容配置。`true` ≡ `always_on`，`false` ≡ `manual` |
| `description` | 字符串 | `model_decision` 必填 |
| `glob` | 单个 glob 或列表 | 配合 `trigger: glob` |
| `paths` | 单个 glob 或列表 | 等价于 `trigger: glob` + `glob` |

`glob` / `paths` 说明：
- 项目级规则的 glob **相对于包含 `.qoder/` 的项目目录**匹配；用户级规则相对于当前项目根目录匹配。
- 两者都是**内部路由元数据**，只决定何时生效，**不会随正文注入模型上下文**。
- gitignore 风格匹配。`/*.md` 仅根目录，`*.md` 任意目录，`src/components/*.tsx` 不含嵌套。

### 示例

```markdown
---
trigger: model_decision
description: 修改 API handler、schema 或接口错误结构时使用。
---

# API 规则
- 使用 `src/api/schema/` 下的共享 schema 校验请求体。
```

```markdown
---
trigger: glob
glob:
  - src/api/**
  - "**/*.test.ts"
---
```

### 会话中热更新（与 Hooks/Skills 不同！）

规则加载后 **Qoder 会在本次会话剩余时间持续监视该文件**，编辑后下一轮即被感知，
**无需重启**。按路径生效的规则在首次匹配到被访问文件时也纳入监视。

## `@` 导入

`AGENTS.md` 可用 `@path/to/file` 引入其他文件，相对路径基于当前 `AGENTS.md` 所在目录。

```markdown
See @README.md for the high-level architecture.
Use @docs/testing.md for test data setup.
```

- 支持相对路径、绝对路径、`~/` 路径
- **行内代码和代码块中的 `@...` 不会被当作导入**（想纯文本提及就写 `` `@README.md` ``）
- 默认只允许导入项目边界内的文件，指向项目外需显式批准
- 递归展开，有深度限制

> 🔁 **对照**：Kiro 的引用语法是 `#[[file:xxx]]`，Qoder 是 `@path`。语义相近，写法必须改。

## 自动记忆

默认**不开启**。四类内容：

| 类型 | 用途 |
|---|---|
| `user` | 用户角色、长期偏好、跨项目工作习惯 |
| `feedback` | 用户对工作方式的纠正或确认，例如"以后不要这样做" |
| `project` | 当前项目中无法直接从代码推导出的背景、约束或决策原因 |
| `reference` | 外部系统、看板、仪表盘、文档等资料位置 |

### 启用（改后需重启）

```json
{ "autoMemoryEnabled": true }
```
或 `/settings` 搜索 **Auto Memory**，或环境变量：
```bash
QODER_MEMORY=1 qoder                      # 项目级
QODER_MEMORY=1 QODER_MEMORY_USER=1 qoder  # 追加用户级
```
显式设置的 `QODER_MEMORY` 优先于 `settings.json`。**仅交互式会话生效。**

### 存储位置

```text
~/.qoder/projects/<project>/memory/   # 项目级
~/.qoder/memory/                      # 用户级（需 QODER_MEMORY_USER）
memory/
├── MEMORY.md          # 索引，启动时读取，最多前 200 行 / ~25KB
├── user-preferences.md
├── feedback-testing.md
└── project-release-context.md
```

`MEMORY.md` 只做索引，长内容放主题文件。**自动记忆是本机文件，不随代码提交同步。**

### 管理

- `/memory` — 记忆概览 + `Open auto-memory folder` 入口
- `/memory manage` — 按主题文件查看/编辑/删除（删除会同步移除 `MEMORY.md` 索引行）
- 自然语言：「记住这个项目的集成测试需要先启动本地 Redis。」/「忘记之前关于旧部署脚本的记忆。」
- 想写成团队规则就明说：「把这条测试约定加到项目 AGENTS.md。」

## 排查

**不遵守 `AGENTS.md`**：`/memory` 确认文件在列表中 → 确认目录**已信任**（未信任目录不加载项目设置、Hooks、MCP 和 `AGENTS.md`）→ 检查各级文件冲突 → 检查 `agentsMdExcludes` → 把笼统要求改成可验证规则。

**记忆过期**：记忆反映写入时的上下文。处理当前代码/配置/外部状态时**以当前文件为准**。

## 🔁 `.trae/steering/` → `.qoder/rules/` 的机械映射

| Kiro / 当前项目写法 | Qoder 写法 |
|---|---|
| `inclusion: always` | `trigger: always_on`（或省略 frontmatter） |
| `inclusion: manual` | `trigger: manual` |
| `inclusion: fileMatch` + `fileMatchPattern` | `trigger: glob` + `glob`（或 `paths`） |
| `inclusion: auto` | 无直接对应，按意图选 `always_on` 或 `model_decision` + `description` |
| `#[[file:path]]` | `@path`（仅 `AGENTS.md` 支持导入语义） |

**结论：steering 6 篇的迁移是机械的**——移动目录 + 换 frontmatter 字段名即可，正文不用改。
