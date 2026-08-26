---
trigger: model_decision
description: Qoder 平台扩展资产的正确格式与挂载位置。需要新建或修改 rules / skills / subagent / hooks / commands / plugins / MCP / settings 配置时，或排查「配置不生效」时引入。也用于把 .trae/ 或 Kiro 时代的历史资产迁移到 Qoder。
---

# Qoder 平台扩展资产规格

来源：`references/qoder-docs/` 下 41 篇官方文档镜像的蒸馏。需要逐字引用时去读原篇。

## 第一原则：三代格式互不兼容

本项目历经 Kiro → Trae → Qoder。同名概念的格式**完全不同**。
凭 Kiro / Trae / Claude Code 的经验推测 Qoder 格式，是本项目已经反复踩过的坑。

`.trae/` 下 39 个文件 Qoder 一个都不加载。

## 排查「不生效」的固定顺序

不要猜，按这个顺序查：

1. **目录信任** —— 未信任的目录**只加载用户级配置**，项目内的 settings / hooks / MCP / AGENTS.md 全部不加载。这是所有加载问题的共同前提。
2. **跑自查命令**（CLI）：`/memory` `/skills` `/agents` `/hooks` `/mcp` `/plugins` `/tools`
   —— 用实际加载结果代替猜测。
3. **功能开关**：`/agents` `/plan` `/workflows` `/marketplace` 需对应开关开启；
   `/skills` 需管理员权限开启。命令不可见 ≠ 配置写错。
4. **热重载**：`/mcp reload` `/plugins reload` `/skills reload` `/agents reload` `/commands`。
   Rules 是**自动热更新**的（加载后持续监视文件，编辑下一轮生效，无需重启）。
5. 仍不行 → 重启。

## Rules

位置：`.qoder/rules/**/*.md`（项目级，可提交）、`~/.qoder/rules/`（用户级）。

### 四种 trigger

| trigger | 何时用 | 必填 | 加载行为 |
|---|---|---|---|
| `always_on` | 每次会话都要遵守 | — | 启动时加载**正文** |
| `manual` | 偶尔用，需明确引入 | — | **不自动注入正文** |
| `model_decision` | 一句描述能判断是否相关 | **非空 `description`** | 只注入**路径 + 描述**，判定相关才读正文 |
| `glob` | 只对某些文件/目录生效 | **有效 `glob`** | 访问匹配文件后按需加载正文 |

- 不写 frontmatter ≡ `always_on`
- `paths: [...]` ≡ `trigger: glob` + `glob`
- `trigger` 存在时**优先于** `alwaysApply`
- **glob / paths 是内部路由元数据，不注入模型上下文**

### glob 的相对基准（容易搞错）

- **项目级规则**：glob 相对于**包含 `.qoder/` 的项目目录**（本项目 = 仓库根）
  → 写 `docs/test-cases/**`，不要写 `/Users/.../docs/test-cases/**`
- **用户级规则**：相对于当前项目根目录

### Kiro `inclusion:` → Qoder `trigger:` 映射

迁移 `.trae/steering/` 时按此换：

| Kiro | Qoder |
|---|---|
| 无 frontmatter / `always` | `always_on` |
| `manual` | `manual` |
| `auto` + description | `model_decision` + description |
| `fileMatch` + `fileMatchPattern` | `glob` + `glob` |

### AGENTS.md 加载逻辑

- 从工作区目录**向父目录查找**，**默认到 `.git` 所在目录为止**（`context.memoryBoundaryMarkers`）
- 边界之外的文件**不会被发现**
- 文件名由 `context.fileName` 决定（默认 `AGENTS.md`）
- `agentsMdExcludes` 可排除特定文件 —— 排查「没遵守 AGENTS.md」时要查这一项
- **子目录记忆启动时不预加载**：只有读了子目录里的文件，才会从该目录向上补充
- 默认只扫当前目录；要从额外可信目录加载需开 `context.loadMemoryFromIncludeDirectories`
- `context.discoveryMaxDirs` 默认 200

### `@` 导入

`AGENTS.md` 与规则正文中可写 `@path/to/file` 显式导入。
递归展开有深度限制；**代码块里的 `@` 不算导入**；项目外导入需批准。

> 本项目用途：`docs/interface-matrix.csv` 这类必须被读到的资产，
> 用 `@` 显式导入，而不是指望模型自己去找。注意大文件会挤占上下文，按需权衡。

## Skills

位置：`.qoder/skills/<name>/SKILL.md` —— **目录结构必须是这样**，少一层都不行。

- 来源优先级：内置 < 插件 < 项目级 < **用户级**（**用户级覆盖项目级**）
- 条件 Skill 仅在文件路径匹配时激活
- `/skills reload` 重载

> ⚠️ IDE 与 CLI 的内置 Skill 集是**两套**。
> IDE 侧本会话实际可用：`better-harness` / `canvas` / `create-plugin` / `create-skill` /
> `create-subagent` / `vercel-deploy`。
> CLI 侧内置 11 个：`loop` `remember` `run` `run-skill-generator` `batch` `debug`
> `quest` `verify` `security-scan` `simplify` `mcp-config`。
> 引用「内置能力」时必须区分入口，不能拿 CLI 清单当 IDE 现状。

## Subagent

位置：`.qoder/agents/<name>.md` —— **单文件**，不是 `<name>/agent.md`。

frontmatter 至少含 `name` 和 `description`。
`--agents`（JSON）加载的定义**仅本次会话有效**。
检查 `agents.overrides` 是否把目标设成 `enabled: false`。

CLI 内置 5 个：`general-purpose`、`Explore`（只读+轻量模型）、`Plan`（只读+继承会话模型）、
`statusline-setup`、`qoder-guide`。

## 自定义命令

位置：`.qoder/commands/<name>.md`（项目级，建议提交）、`~/.qoder/commands/`（用户级）。

frontmatter：`description` **必填**，`name` 选填（**仅作 TUI 展示名**）。

- **调用名由文件路径推导**，与 `name` 字段无关
- 子目录用 `:` 作命名空间：`commands/git/commit.md` → `/git:commit`
- ⚠️ **同目录下若存在 `SKILL.md`，该目录注册为单个命令，目录内其它 `.md` 会被忽略**
- 优先级：**用户级覆盖项目级**
- `/commands` 重载
- Headless 下可用：`qoder -p '/git-commit'`
- 只有 **Prompt 类型**命令支持自定义；TUI 类型是系统内置

## Hooks

配置：`hooks/hooks.json`（插件内）或 settings 中的 hooks 配置。

三个最容易漏的点：

1. **Hook 从 stdin 接收 JSON**（含 `session_id`、`cwd`、`hook_event_name`）—— 脚本必须从 stdin 读
2. **脚本需有可执行权限**（`chmod +x`）且路径正确
3. **Shell 主题干扰**：Powerlevel9k / Powerlevel10k 等可能污染终端输出导致截断或格式错乱
   （本机 shell 是 `/bin/zsh`，这是一个隐蔽的失效原因）

硬约束要用 `PreToolUse` + `deny` —— 文档写在 AGENTS.md 里**不是**强制策略。

## MCP

5 种传输：`stdio`（默认）/ `sse` / `http`(streamable-http) / `ws` / `sdk`。

覆盖顺序：用户级 → 项目级 `settings.json` → 项目级 `.mcp.json` → 本地级 → CLI 参数。

- 项目级 MCP **默认需逐个批准**；用 `mcp.enableAllProjectMcpServers` 或
  `mcp.enabledProjectMcpServers` 跳过
- **懒加载省 token**：`mcp.lazyLoad: true` 或 `QODER_MCP_LAZY=1`
  → 只暴露 `mcp_list` / `mcp_get` / `mcp_call` 三个 meta 工具

## 配置分层

| 范围 | 文件 | 提交 |
|---|---|:-:|
| 个人 | `~/.qoder/settings.json` | ❌ |
| 项目 | `<项目>/.qoder/settings.json` | ✅ |
| 本地 | `<项目>/.qoder/settings.local.json` | ❌ 加 gitignore |

优先级：内置默认 < 用户级 < 项目级 < 本地级 < `--settings`。

**深度合并规则**：对象逐字段递归（只覆盖出现的字段）；单值直接覆盖；
部分数组（禁用/排除列表）走**并集合并**，其余数组默认覆盖。

允许 `//` 注释；值中可引用环境变量。
顶层三项：`outputStyle` / `language` / **`agent`（把主线程整体换成某个自定义 Agent）**。

`QODER_CONFIG_DIR` 可改用户配置目录；**项目级 `.qoder/` 始终在项目根，不可改**。

### `.qoder/` 目录结构（官方）

```text
<项目>/.qoder/
├── settings.json          # 项目级配置（可提交）
├── settings.local.json    # 本地配置（不提交）
├── rules/                 # 项目级规则 *.md
├── skills/                # 项目级 Skills
├── agents/                # 项目级 Subagent（单文件）
├── commands/              # 自定义命令
├── repowiki/              # Repo Wiki 产物 + wiki_plan.yaml
├── worktrees/             # --worktree 创建的隔离工作树
├── loop.md                # /loop 无参时的任务清单
└── scheduled_tasks.json   # 定时任务定义
```

## 插件：`.trae/` 资产的最佳落点

插件 manifest 在 **`.qoder-plugin/plugin.json`**（不是根目录），可省略，唯一必填 `name`。
`settings` 字段**当前仅支持 `agent` 键，其余被忽略**。

约定目录与 `.trae/` 几乎一一对应：

| `.trae/` 现有 | 插件对应 | 改动量 |
|---|---|---|
| `skills/*/SKILL.md` | `skills/*/SKILL.md` | **结构不用改** |
| `agents/*/agent.md` | `agents/*.md` | 改成单文件 + frontmatter |
| `hooks.json` | `hooks/hooks.json` | 按 Qoder 事件名重写 |
| `mcp-servers/` | `.mcp.json` | 重写 |
| `scripts/` | `bin/` | **自动加入 PATH** |
| `steering/*.md` | 无直接对应 | 转 `.qoder/rules/` 或 `commands/` |

打成插件的好处：整套资产可版本化、可分发给团队、可一键 enable/disable。

## 索引与上下文

- `.qoderignore` + `.gitignore` 决定索引排除；最多 100,000 文件
- 排除模式支持 `dist/`、`*.log`、`**/logs`、**`!app/`（取反）**
- Repo Wiki：每项目最多 10,000 文件，仅支持 Git 仓库且至少一次提交
- `wiki_plan.yaml` 在 `.qoder/repowiki/wiki_plan.yaml`，用 `/knowledge-plan` 创建，
  可在生成**前**注入引导（`template` / `notes` / `documents` 白名单 / `scope.include-exclude`）
- 人工修改的知识内容会被**标记保护**，下次自动更新不覆盖

## 已知文档内部矛盾

`ide/02-skills.md`（早期落盘）说「Skills 同名时项目级优先」，
官方 `cli/troubleshoot-loading` 说「内置 < 插件 < 项目级 < 用户级」即**用户级优先**。
**以 troubleshoot-loading 为准**（见 `references/qoder-docs/cli/10-troubleshoot-loading.md`）。
