# 配置文件与生效顺序（Qoder CLI）

> 来源：https://docs.qoder.com/zh/cli/settings
> 配套：`cli/08-settings-reference.md`（全部配置项与环境变量）、`cli/04-config-scope-and-loading.md`

## 三层配置文件

| 层级 | 路径 | 说明 |
|---|---|---|
| **用户级** | `~/.qoder/settings.json` | 个人偏好，对当前用户所有项目生效 |
| **项目级** | `<项目>/.qoder/settings.json` | 项目共享配置，**随版本库提交**，团队共用 |
| **本地级** | `<项目>/.qoder/settings.local.json` | 个人的项目内覆盖，**通常不提交** |

配置目录默认 `~/.qoder`，可用环境变量 `QODER_CONFIG_DIR` 改。

## 合并优先级（低 → 高，高覆盖低）

1. 内置默认值（Schema 默认）
2. 用户级 `~/.qoder/settings.json`
3. 项目级 `<项目>/.qoder/settings.json`
4. 本地级 `<项目>/.qoder/settings.local.json`
5. **命令行 `--settings` 指定的配置（最高）**

### 合并方式是深度合并（deep merge），不是整体替换

| 类型 | 行为 |
|---|---|
| **对象** | 逐字段递归合并，**只覆盖出现的字段**，其余保留低优先级的值 |
| **单值**（字符串/数字/布尔） | 高优先级直接覆盖 |
| **数组** | 部分配置项（禁用列表、排除列表）走「**并集合并**」去重；其余数组**默认覆盖** |

> ⭐ 因此项目级只需写想覆盖的字段，**不必复制整份用户配置**。

### ⚠️ 文件夹信任的影响

项目级与本地级配置**只在当前工作目录被信任时才应用**。
未信任 → **只加载用户级配置**，忽略项目内 `settings.json` 与 `settings.local.json`。
由 `security.folderTrust.enabled`（默认开启）控制。

## 文件格式

JSON，顶层是对象，大多按分组嵌套；少数直接在顶层（`outputStyle`、`language`、`agent`）。

- **允许 `//` 注释**（解析时忽略）——可以给团队约定写说明
- **值中可引用环境变量**，运行时解析替换
- 部分配置项需重启

```json
{
  "outputStyle": "concise",
  "ui": { "theme": "Tokyo Night", "autoThemeSwitching": true },
  "model": { "name": "auto", "maxSessionTurns": -1 },
  "tools": { "useRipgrep": true }
}
```

## 顶层配置项（不属于任何分组）

| 配置项 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `outputStyle` | string | 无 | 激活的输出风格名（**需重启**）。兼容 `general.outputStyle`，顶层优先 |
| `language` | string | 无 | AI 回复的首选语言（**需重启**） |
| `agent` | string | 无 | **主线程使用的 Agent 名称**（需重启） |

> ⭐ `agent` 这一项值得注意：可以把主线程整体换成某个自定义 Agent，
> 而不是每次靠 `@` 或模型自主判断去调子智能体。

## 常调分组（摘要，全量见 08）

**ui**：`theme` / `autoThemeSwitching`(true) / `hideBanner` / `showLineNumbers`(true) / `loadingPhrases`(off) / `accessibility.screenReader`(需重启)

**model**：`name` / `reasoningEffort`(low|medium|high) / `maxSessionTurns`(-1 不限)

**tools**：`sandbox`(需重启) / `sandboxAllowedPaths` / `sandboxNetworkAccess`(false) / `useRipgrep`(true) / `shell.inactivityTimeout`(300 秒无输出超时) / `core`（内置工具白名单，需重启）/ `exclude`（需重启）

**security**：`folderTrust.enabled`(true) / `toolSandboxing`(false) / `disableYoloMode`(false) / `blockGitExtensions`(false) / `environmentVariableRedaction.enabled`(false) —— **全部需重启**

**mcp**：`mcpServers`(需重启) / `mcp.allowed` / `mcp.excluded`

**statusLine**：`type`(仅 `command`) / `command`（Shell 命令，**通过 stdin 接收会话数据 JSON**）/ `padding`

## 编辑方式

- 交互界面：`/settings` 打开设置面板
- 手动编辑对应层级的 `settings.json`

未标「需重启」的项通常即时生效。
