# 记忆 与 Rules 完整规格（Qoder CLI）

> 来源：https://docs.qoder.com/zh/cli/memory
> ⭐ **本文是 rules / AGENTS.md / 自动记忆的权威完整规格**，
> 与 `cli/03-rules-and-memory.md`、`ide/01-rules.md` 冲突时以本文为准。

## 两类记忆

| 机制 | 谁来写 | 适合内容 | 作用域 | 查看入口 |
|---|---|---|---|---|
| **静态记忆** | 用户或团队 | 明确、稳定、每次会话都要遵守的说明。`AGENTS.md` 放整体说明，**rules 按主题或文件范围拆分** | 用户级、项目级、本地项目级、插件提供 | `/memory` |
| **自动记忆** | Qoder CLI | 从对话中学到的可复用信息：偏好、反馈、项目背景、**外部资料位置** | 项目级；可选用户级 | `/memory` 打开 auto-memory folder；`/memory manage` |

> ⚠️ **记忆是上下文，不是强制策略。** 硬性阻止某类命令/工具/路径 → 用权限配置或 Hooks。

## 静态记忆文件位置

```text
~/.qoder/AGENTS.md
<project>/AGENTS.md
<project>/AGENTS.local.md
<project>/.qoder/rules/**/*.md
```

| 位置 | 用途 | 适合提交 |
|---|---|---|
| `~/.qoder/AGENTS.md` | 用户跨项目通用偏好和工作习惯 | 否 |
| `<project>/AGENTS.md` | **团队共享的项目规则、架构说明、常用命令** | 是 |
| `<project>/AGENTS.local.md` | 本机私有说明（本地服务地址、个人测试数据） | 否 |
| `<project>/.qoder/rules/**/*.md` | **按主题或文件范围拆分的项目规则** | 是 |

用其他文件名 → `context.fileName`（单个文件名或数组，默认 `AGENTS.md`）。

## ⭐ 加载逻辑（本项目失效的根因就在这里）

- **用户级**：加载用户配置目录中的 `AGENTS.md`
- **项目/本地项目**：在**可信工作区**内，从当前工作区目录**向父目录查找** `AGENTS.md`、`AGENTS.local.md`、`.qoder/rules/**/*.md`，**默认到 `.git` 所在目录为止**
- **规则的 frontmatter 决定加载方式**：
  - 始终生效 → 随项目记忆一起加载
  - 指定文件生效 → 只在访问匹配文件后按需加载
  - **手动规则和模型决策规则不会在启动时注入正文**
- **子目录记忆启动时不预加载**：只有成功读取子目录里的文件后，才会从该文件所在目录向上补充此前未加载的记忆。按需加载的内容会显示在 `/memory` 中

在 `/repo/packages/app` 启动时检查：
```text
/repo/packages/app/AGENTS.md
/repo/packages/app/.qoder/rules/*.md
/repo/packages/AGENTS.md
/repo/packages/.qoder/rules/*.md
/repo/AGENTS.md
/repo/.qoder/rules/*.md
```
从 `/repo` 启动则**不会**预加载 `/repo/packages/app/` 下的，需访问该目录文件后才按需加载。

## Rules 完整规格

### 作用域

| 作用域 | 位置 | 范围 | 提交 |
|---|---|---|---|
| 项目级 | `<project>/.qoder/rules/**/*.md` | 文件所在项目，与团队共享 | 是 |
| 用户级 | `~/.qoder/rules/**/*.md` | 你打开的每个项目，仅本机 | 否 |

项目级规则**可位于工作区任意层级（含嵌套子目录）**，通过向上查找发现。

> Qoder CLI 的 rules frontmatter **兼容 Qoder Desktop 中配置的 rules 设置**，
> 从 Desktop 同步或复制的规则文件可继续使用原有触发配置。

### 四种生效方式

没配加载相关 frontmatter 时**默认始终生效**；**`trigger` 存在时优先于 `alwaysApply`**。

| 生效方式 | 适合场景 | 配置 | 加载行为 |
|---|---|---|---|
| **始终生效** | 每次会话都要遵守的通用规则 | 不写 frontmatter，或 `trigger: always_on`，或 `alwaysApply: true` | 启动/刷新记忆时加载**正文** |
| **手动引入** | 偶尔使用需明确引入 | `trigger: manual` 或 `alwaysApply: false` | **不自动注入正文** |
| **模型决策** | 可用一句描述判断是否相关 | `trigger: model_decision` + **非空 `description`** | 只注入**路径和说明**，模型判断相关时再读正文 |
| **指定文件生效** | 只对某些文件/目录生效 | `trigger: glob` + `glob`，或直接 `paths` | 访问匹配文件后按需加载正文 |

⚠️ `model_decision` 缺 `description`、`glob` 缺有效 `glob` → **规则正文不会自动注入**。

### Frontmatter 字段

| 配置项 | 可用值 | 说明 |
|---|---|---|
| `trigger` | `always_on` / `manual` / `model_decision` / `glob` | 生效方式 |
| `alwaysApply` | `true` / `false` | 兼容配置。`true` ≡ `always_on`，`false` ≡ `manual` |
| `description` | 字符串 | 模型决策规则的说明 |
| `glob` | 单个 glob 或列表 | 与 `trigger: glob` 搭配 |
| `paths` | 单个 glob 或列表 | **等价于 `trigger: glob` + `glob`** |

关于 glob / paths：
- **项目级规则的 glob 相对于包含 `.qoder/` 目录的项目目录**匹配；**用户级规则的 glob 相对于当前项目根目录**匹配
- 两者都是**内部路由元数据**：只决定何时生效，**不会随正文注入模型上下文**
- **gitignore 风格匹配**

| 模式 | 匹配 |
|---|---|
| `**/*.ts` | 任意目录下所有 TS 文件 |
| `src/**/*` | `src/` 下任意深度所有文件 |
| `*.md` | 任意目录下的 md |
| `/*.md` | **仅项目根目录**的 md |
| `src/components/*.tsx` | 直接位于该目录下（**不含嵌套**） |

### ⭐ 会话中更新规则（不用重启）

规则加载后，Qoder CLI 会在**本次会话剩余时间持续监视该文件**。
编辑规则（任何加载方式、项目级或用户级）**会在下一轮被感知**，无需重启即遵循新版本。
按路径生效的规则在首次匹配到被访问文件时也会被纳入监视。

> ⚠️ 这一条修正了 `README.md` 里「配置改动大多需要重启，Hooks、Skills 均不支持热加载」的表述 ——
> **Rules 是支持热更新的**，Hooks/Skills 也各有 `reload` 命令（见 `cli/14-troubleshoot-extensions.md`）。

## `AGENTS.md` 编写建议

**适合写**：
- 构建、测试、格式化和发布命令
- 项目目录结构和关键模块边界
- 代码风格、命名规则和评审要求
- 团队约定的工作流（提交、分支、**测试数据准备**）
- 对当前仓库长期有效的安全或合规注意事项

**不适合写**：
- 只对当前这次任务有用的临时状态
- **会很快过期的排期和进度**
- 已能从代码或 README 直接看出的长篇重复内容
- **必须强制执行的安全策略**（→ 权限配置或 Hooks）

> **指令越具体越稳定。**

## `@` 导入其他文件

`AGENTS.md` 可用 `@path/to/file` 引入其他文件，相对路径基于当前 `AGENTS.md` 所在目录。

```markdown
See @README.md for the high-level architecture.
Use @docs/testing.md for test data setup.
```

规则：
- 支持相对路径、绝对路径和 `~/` 路径
- **Markdown 行内代码和代码块中的 `@...` 不会被当作导入**（想纯文本提及就写成 `` `@README.md` ``）
- 项目和本地项目记忆**默认只允许导入项目边界内的文件**；指向项目外需显式批准或安全设置允许
- **递归展开，有深度限制**避免循环导入

> ⭐ 这解决了本项目一个实际问题：`docs/interface-matrix.csv`、`docs/api-reference/ssos-接口清单.csv`
> 这类必须被读到的资产，可以在 `AGENTS.md` 里用 `@` 显式导入，而不是指望模型自己去找。

## 自动记忆

启用后把值得跨会话复用的信息存为本机 Markdown。**不是每段对话都保存**，按内容判断。

### 四类内容

| 类型 | 用途 |
|---|---|
| `user` | 用户角色、长期偏好、跨项目工作习惯 |
| `feedback` | **用户对工作方式的纠正或确认**，例如「以后不要这样做」 |
| `project` | 当前项目中无法从代码推导的背景、约束或决策原因 |
| `reference` | 外部系统、看板、仪表盘、文档等**资料位置** |

> 自动记忆是**本机文件，不会因为提交代码同步到其他机器**。也可能过期 ——
> 涉及文件、函数、配置或外部状态时应**先核对当前事实再行动**。

### 启用（需重启）

只在**交互式会话**中运行。

```json
{ "autoMemoryEnabled": true }
```
或 `/settings` 搜 **Auto Memory** 打开开关。

环境变量临时覆盖（**显式设置的 `QODER_MEMORY` 优先于 settings.json**）：
```bash
QODER_MEMORY=1 qoder
QODER_MEMORY=1 QODER_MEMORY_USER=1 qoder   # 同时启用跨项目用户级自动记忆根
```
`QODER_MEMORY_USER` 只在自动记忆已启用时生效。

### 存储位置

```text
~/.qoder/projects/<project>/memory/     # 项目级
~/.qoder/memory/                        # 用户级（启用后）
```

每个目录含一个 `MEMORY.md` 索引 + 若干主题文件：
```text
memory/
├── MEMORY.md
├── user-preferences.md
├── feedback-testing.md
└── project-release-context.md
```

⚠️ **`MEMORY.md` 是索引，不应写长篇正文。**
启动时读取每个活跃根的 `MEMORY.md`，**最多前 200 行或约 25KB**，详细内容放主题文件由索引指向。

### 管理

- `/memory` — 记忆概览（用户级/项目级/本地项目级文件 + `Open auto-memory folder` 入口）
- `/memory manage` — 自动记忆管理器：查看、打开、编辑、删除主题文件。**删除时同步移除 `MEMORY.md` 索引行**

自然语言操作：
```
记住这个项目的集成测试需要先启动本地 Redis。
忘记之前关于旧部署脚本的记忆。
把这条测试约定加到项目 AGENTS.md。   ← 内容更像团队规则时，明确要求写入
```

## 排查

### 没遵守 `AGENTS.md`
1. `/memory` 确认目标文件出现在列表中
2. 确认当前目录在**可信工作区**内（未信任不加载项目设置、Hooks、MCP 和 `AGENTS.md`）
3. 检查**用户级/项目级/本地项目级之间的冲突指令**
4. 检查 **`agentsMdExcludes`** 是否排除了目标文件
5. 把笼统要求改成**具体、可验证**的规则

### `@` 导入没生效
- 路径真实存在，且**不在代码块或行内代码中**
- 项目外导入默认被阻止
- npm 包名、普通提及、没有文件特征的 `@word` 不按导入处理

### 自动记忆没出现
- 确认是 TUI 交互式会话；确认启动时设了 `QODER_MEMORY=1`
- **不是每轮都会保存；没有值得复用的信息时创建 0 条是正常结果**

### 记忆过期
记忆反映的是**写入时**的上下文。处理当前代码/配置/外部状态时**以当前文件和系统为准**，
发现过期就更新或删除。

## 🎯 本项目的落地结论

`.trae/steering/` 那 6 个规范文件应该迁到 `.qoder/rules/`，并按内容分配 trigger：

| 原 steering 内容性质 | 应配 trigger |
|---|---|
| 「每次都必须遵守」的通用约定（如产出物必须是 XMind） | `always_on` |
| 「写用例时」才需要的规范 | `glob` + `docs/test-cases/**` |
| 「涉及接口覆盖时」才相关的规范 | `model_decision` + 一句 description |
| 发布/交付检查清单 | `manual` |

⚠️ 但**「禁止写 md 交付物」这条不能靠 rules** —— 它是硬约束，必须用 Hooks（`PreToolUse` + `deny`）。
