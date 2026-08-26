# 配置项全表与环境变量（Qoder CLI settings.json）

> 来源：https://docs.qoder.com/zh/cli/settings-reference + https://docs.qoder.com/zh/cli/troubleshoot-config

## 配置文件位置

| 层级 | 路径 |
|---|---|
| 用户级 | `~/.qoder/settings.json` |
| 项目级 | `<项目>/.qoder/settings.json` |
| 本地级 | `<项目>/.qoder/settings.local.json` |

JSON Schema 位于项目 `schemas/settings.schema.json`，可用于编辑器补全校验。
**JSON 允许 `//` 与 `/* */` 注释**（解析前剥离）；开头 BOM 会被忽略但建议无 BOM UTF-8。

## 覆盖顺序（低 → 高）

1. 内置默认值
2. 用户级 `~/.qoder/settings.json`
3. 项目级 `<项目>/.qoder/settings.json`
4. 本地级 `<项目>/.qoder/settings.local.json`
5. 命令行 `--settings`

**对象按字段深度合并；单值直接覆盖；部分数组（如禁用/排除列表）取并集。**

## 顶层配置项

| 配置项 | 类型 | 默认值 | 需重启 | 说明 |
|---|---|---|---|---|
| `mcpServers` | object | `{}` | 是 | MCP 服务器配置 |
| `autoMemoryEnabled` | boolean | **`false`** | 是 | 交互式会话中启用自动记忆 |
| `outputStyle` | string | 无 | 是 | 激活的输出风格名称，兼容 `general.outputStyle`，顶层优先 |
| `language` | string | 无 | 是 | AI 回复首选语言（如 `"Chinese"`） |
| `vpcInstanceName` | string | 无 | 是 | VPC 私有部署实例名（仅 CN 版） |
| `agent` | string | 无 | 是 | **主线程使用的 Agent 名称** |
| `enabledPlugins` | object | `{}` | 是 | 插件启用状态映射（插件 ID → true/false） |
| `hooks` | object | `{}` | **否** | 按事件配置的 Hooks |
| `agentsMdExcludes` | string[] | `[]` | 是 | 按 glob 排除项目级/本地级记忆文件，**仅支持手工配置** |
| `autoMode` | object | `{}` | 否 | Auto 模式分类器软引导，**仅从用户级与本地配置读取** |
| `allowManagedPermissionRulesOnly` | boolean | `false` | 否 | 只使用托管策略的权限规则 |

## general

| 配置项 | 类型 | 默认值 | 需重启 | 说明 |
|---|---|---|---|---|
| `general.preferredEditor` | string | 无 | 否 | 打开文件的首选编辑器 |
| `general.vimMode` | boolean | `false` | 否 | Vim 键位 |
| `general.defaultPermissionMode` | enum | `default` | 否 | `default`/`accept_edits`/**`plan`**/`auto`/`bypass_permissions`/`dont_ask` |
| `general.enableAutoUpdate` | boolean | `true` | 否 | 自动更新 |
| `general.enableNotifications` | boolean | `false` | 否 | 运行事件通知 |
| `general.maxAttempts` | number | `10` | 否 | 主对话模型请求最大尝试次数（≤10） |
| `general.retryFetchErrors` | boolean | `true` | 否 | `fetch failed` 类异常自动重试 |
| `general.fileCheckpointing.enabled` | boolean | `true` | 是 | **文件检查点（代码回溯）** |
| `general.plan.enabled` | boolean | `true` | 是 | 启用 Plan 模式 |
| `general.plan.directory` | string | 系统临时目录 | 是 | 计划产物存放目录 |
| `general.plan.modelRouting` | boolean | `true` | 否 | Plan/实现阶段自动切换模型 |
| `general.sessionRetention.enabled` | boolean | `true` | 否 | 会话自动清理 |
| `general.sessionRetention.maxAge` | string | `30d` | 否 | 自动删除早于此时长的会话 |
| `general.sessionRetention.minRetention` | string | `1d` | 否 | 最小保留期（安全下限） |

## context（⭐ 与记忆加载直接相关）

| 配置项 | 类型 | 默认值 | 需重启 | 说明 |
|---|---|---|---|---|
| `context.fileName` | string/string[] | **`AGENTS.md`** | 否 | **载入记忆的上下文文件名，可改可多个** |
| `context.importFormat` | enum | 无 | 否 | 记忆导入格式：`tree`/`flat` |
| `context.discoveryMaxDirs` | number | `200` | 否 | 记忆发现的最大目录数 |
| `context.memoryBoundaryMarkers` | string[] | `['.git']` | 是 | **记忆向上发现的边界标记** |
| `context.loadMemoryFromIncludeDirectories` | boolean | `false` | 否 | 从额外可信目录加载记忆 |
| `context.fileFiltering.respectGitIgnore` | boolean | `true` | 是 | 搜索时遵循 `.gitignore` |
| `context.fileFiltering.enableRecursiveFileSearch` | boolean | `true` | 是 | `@` 引用补全递归搜索 |

> ⭐ `context.fileName` 可配成数组——**这是让 Qoder 读非标准文件名的唯一正规入口**。
> 但注意它只影响「记忆文件」，不能用来复活 `.trae/steering/`（那是目录布局问题，不是文件名问题）。

## tools

| 配置项 | 类型 | 默认值 | 需重启 | 说明 |
|---|---|---|---|---|
| `tools.sandbox` | boolean/string/object | 无 | 是 | 沙箱执行环境 |
| `tools.sandboxAllowedPaths` | string[] | `[]` | 是 | 沙箱额外可访问路径 |
| `tools.sandboxNetworkAccess` | boolean | `false` | 是 | 沙箱是否允许联网 |
| `tools.shell.pager` | string | `cat` | 否 | Shell 输出分页命令 |
| `tools.shell.inactivityTimeout` | number | `300` | 否 | Shell 无输出超时秒数 |
| `tools.core` | string[] | 无 | 是 | **内置工具白名单** |
| `tools.exclude` | string[] | 无 | 是 | 从发现中排除的工具名 |
| `tools.useRipgrep` | boolean | `true` | 否 | 用 ripgrep 搜内容 |
| `tools.disableLLMCorrection` | boolean | `true` | 是 | 禁用编辑工具的 LLM 纠错 |

## mcp

| 配置项 | 类型 | 默认值 | 需重启 | 说明 |
|---|---|---|---|---|
| `mcp.allowed` | string[] | 无 | 是 | 允许的 MCP 服务器列表 |
| `mcp.excluded` | string[] | 无 | 是 | 排除的 MCP 服务器列表 |
| `mcp.enableAllProjectMcpServers` | boolean | `false` | 是 | 自动批准所有项目级 MCP 服务器 |
| `mcp.enabledProjectMcpServers` | string[] | `[]` | 是 | 已逐个批准的项目级 MCP 服务器名 |
| `mcp.lazyLoad` | boolean | `false` | 是 | 懒加载 MCP 工具（暴露 meta 工具） |

## security

| 配置项 | 类型 | 默认值 | 需重启 | 说明 |
|---|---|---|---|---|
| `security.folderTrust.enabled` | boolean | **`true`** | 是 | 文件夹信任（**关掉它才不需要信任提示，但不建议**） |
| `security.toolSandboxing` | boolean | `false` | 是 | 工具级沙箱隔离 |
| `security.disableYoloMode` | boolean | `false` | 是 | **禁用 YOLO 权限模式** |
| `security.blockGitExtensions` | boolean | `false` | 是 | 阻止从 Git 安装/加载扩展 |
| `security.allowedExtensions` | string[] | `[]` | 是 | 扩展来源正则白名单 |
| `security.environmentVariableRedaction.enabled` | boolean | `false` | 是 | 对可能含密钥的环境变量脱敏 |
| `security.enableConseca` | boolean | `false` | 是 | 上下文感知安全检查 |

## permissions

| 配置项 | 类型 | 默认值 | 需重启 | 说明 |
|---|---|---|---|---|
| `permissions.allow` / `ask` / `deny` | string[] | `[]` | **否** | 权限规则（语法见 `06-permissions.md`） |
| `permissions.additionalDirectories` | string[] | `[]` | 否 | 额外可信目录（对应 `/add-dir`） |
| `permissions.trustDirectories` | string[] | `[]` | 否 | 显式信任目录，**存于用户级，不会被项目级覆盖** |

> ⭐ `permissions` 与 `hooks` 都是**不需重启**的——这是本项目落地防复发机制时最省事的两项。

## model / modelConfigs

| 配置项 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `model.name` | string | 无 | 对话模型 |
| `model.reasoningEffort` | enum | 无 | `disabled`/`off`/`none`/`low`/`medium`/`high`/`xhigh`/`max` |
| `model.contextWindow` | number | 无 | 显式上下文窗口（token） |
| `model.maxSessionTurns` | number | `-1` | 会话保留最大回合数，`-1` 不限 |
| `model.summarizeToolOutput` | object | 无 | 按工具设置输出摘要 token 预算 |
| `modelConfigs.aliases` / `customAliases` | object | 内置 / `{}` | 模型别名预设，自定义合并覆盖内置 |
| `modelConfigs.overrides` / `customOverrides` | array | `[]` | 按匹配条件应用配置覆盖，**最具体的匹配生效** |

## advanced

| 配置项 | 类型 | 默认值 | 需重启 | 说明 |
|---|---|---|---|---|
| `advanced.autoConfigureMemory` | boolean | `true` | 是 | 自动配置 Node.js 内存上限 |
| `advanced.dnsResolutionOrder` | string | 无 | 是 | DNS 解析顺序 |
| `advanced.excludedEnvVars` | string[] | `['DEBUG','DEBUG_MODE']` | 否 | 从项目上下文排除的环境变量 |
| `agents.overrides` | object | `{}` | 是 | **按 Agent 名覆盖其配置**（启用状态、工具、模型、运行上限等） |

## statusLine / output / ui（摘要）

- `statusLine.type`（默认 `command`）、`statusLine.command`（**经 stdin 接收会话数据 JSON**）、`padding`、`colors`
- `output.format`：`text`（默认）/ `json`
- `ui.*` 约 25 项外观类配置：`theme`、`inlineThinkingMode`（`off`/`full`）、`showLineNumbers`、
  `compactToolOutput`、`errorVerbosity`（`low`/`full`）、`accessibility.screenReader`、`showMemoryUsage` 等

## 环境变量

### Qoder 相关

| 环境变量 | 说明 |
|---|---|
| `QODER_PERSONAL_ACCESS_TOKEN` | 个人访问令牌（PAT） |
| `QODER_CONFIG_DIR` | **用户配置目录（默认 `~/.qoder`）** |
| `QODER_MODEL` | 指定模型 |
| `QODER_WORKING_DIR` | 工作目录 |
| `QODER_SESSION_ID` / `QODER_SESSION_NAME` | 会话 ID / 名称 |
| `QODER_PERMISSION_MODE` | 权限模式 |
| `QODER_APPEND_SYSTEM_PROMPT` | 追加系统提示 |
| `QODER_MCP_LAZY` | `1` 启用 MCP 懒加载 |
| `QODER_SANDBOX` / `_IMAGE` / `_IMAGE_DEFAULT` / `_PROXY_COMMAND` | 沙箱相关 |
| `SANDBOX` | 由沙箱环境注入，用于检测是否已在沙箱内避免嵌套 |
| `QODER_ASR_URL` | 语音识别服务地址 |
| `QODER_SUBAGENT_MODEL` | **子 Agent 使用的模型** |
| `QODER_MEMORY` | `1` 启用自动记忆（仅交互式会话） |
| `QODER_MEMORY_USER` | `1` 同时启用用户级自动记忆，需 `QODER_MEMORY` 已启用 |

### 网络代理

`HTTP_PROXY` / `HTTPS_PROXY` / `NO_PROXY`（逗号分隔）/ `NODE_EXTRA_CA_CERTS`（PEM 路径）/ `SSL_CERT_FILE`

## 🔧 配置不生效排查清单

1. **需要重启**：对照上表「需重启」列。`hooks` 和 `permissions` 不用，其余大多要
2. **被更高优先级覆盖**：本地级 > 项目级 > 用户级
3. **命令行覆盖**：`--settings` 优先于所有文件
4. **项目配置被忽略 = 目录未被信任**（`security.folderTrust.enabled` 默认开启）
   - 未信任时**仅加载用户级配置**
   - 信任由**启动时的信任提示**决定（「仅本次会话」/「记住」，后者写入 `settings.local.json`）
   - ⚠️ **`/add-dir` 与 `--add-dir` 只增加额外可信目录，不能把未信任的项目目录变可信**
5. **格式错误**：多余逗号、引号不匹配、括号未闭合；字段放错分组（`ui.theme` 而非顶层 `theme`）
6. **验证手段**：运行 `/settings` 查看当前生效配置；逐层临时移除本地级/项目级文件定位问题层
