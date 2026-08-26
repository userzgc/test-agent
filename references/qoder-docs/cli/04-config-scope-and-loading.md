# 配置作用范围与加载排查（Qoder CLI）

> 来源：https://docs.qoder.com/zh/cli/config-scope + https://docs.qoder.com/zh/cli/troubleshoot-loading

## 三个配置作用范围

| 范围 | 文件 | 适合内容 | 随项目提交 |
|---|---|---|:-:|
| **个人** | `~/.qoder/settings.json` | 跨所有项目的个人偏好：主题、界面、个人默认模型 | ❌ |
| **项目** | `<项目>/.qoder/settings.json` | 团队共享约定：权限规则、项目级模型选择、MCP/Hooks | ✅ |
| **本地** | `<项目>/.qoder/settings.local.json` | 当前机器私有：本地服务地址、个人临时覆盖 | ❌ 应加 `.gitignore` |

选择顺序：
1. 跨所有项目都想要的个人偏好 → 个人配置
2. 团队应当统一的项目约定 → **项目配置，提交到仓库**
3. 只在我这台机器上、不影响他人 → 本地配置 + `.gitignore`

## `.qoder/` 目录结构（官方）

```text
<项目>/.qoder/
├── settings.json          # 项目级配置（可提交）
├── settings.local.json    # 本地项目配置（不提交）
├── rules/                 # 项目级规则文件（*.md）
├── skills/                # 项目级 Skills
├── worktrees/             # --worktree 创建的隔离工作树
└── scheduled_tasks.json   # 定时任务定义
```

补充（其他文档提到但此表未列的）：
- `agents/` — 项目级 Subagent（`.qoder/agents/<name>.md`）
- `repowiki/` — Repo Wiki 产物 + `wiki_plan.yaml` 前置干预配置

用户级数据（`settings.json`、认证状态、插件）在 `~/.qoder`。
可用 **`QODER_CONFIG_DIR`** 环境变量自定义用户配置目录位置；
**项目级 `.qoder` 目录始终位于项目根目录下**（不可改）。

---

# 加载排查：Memory / Skills / Agent 未生效

## 记忆 / 项目说明未加载

- **文件名**：确认与 `context.fileName` 一致（默认 `AGENTS.md`）
- **发现边界**：向上查找会在遇到 `context.memoryBoundaryMarkers`（**默认 `.git`**）的目录时停止。
  文件在边界之外**不会被发现**
- **额外目录**：默认仅扫描当前目录。要从额外可信目录加载，开启 `context.loadMemoryFromIncludeDirectories`
- **发现上限**：`context.discoveryMaxDirs`（默认 **200**）限制搜索目录数，超大仓库可能触及上限
- **文件夹信任**：**未信任的目录不会加载项目内容**
- `/memory` 查看当前加载的记忆来源

## Skills 未加载

- `/skills` 查看已加载列表
- **目录结构**必须是 `skills/<name>/SKILL.md`
- **来源优先级**：内置 < 插件 < 项目级 < 用户级，同名时高优先级覆盖
- **条件 Skill** 仅在文件路径匹配时激活
- `/skills` 需要 Skills 支持与管理员权限开启

## Agent 未加载

- `/agents` 查看已加载的 Agent
- 确认位于 `agents/<name>.md`，frontmatter 至少含 `name` 和 `description`
- 确认**当前项目已被信任**
- 检查 `agents.overrides` 是否把目标 Agent 设为 `enabled: false`
- 通过 `--agents` 加载的额外定义**仅本次会话有效**

## 重新加载方式对照

| 对象 | 刷新方式 |
|---|---|
| 记忆 / `AGENTS.md` | `/memory` |
| Rules | **自动热更新**（加载后持续监视文件，下一轮生效） |
| Skills | `/skills reload`（IDE 侧需重启） |
| Agent | `/agents reload` |
| 自定义命令 | `/commands` |
| 以上都无效 | **重启 Qoder**；部分配置标注"需重启" |

> ⚠️ **文件夹信任是所有加载问题的共同前提**：未信任目录不加载项目设置、Hooks、MCP 和 `AGENTS.md`。
> 排查任何"配置不生效"先确认这一条。
