# 插件参考（Qoder CLI）

> 来源：https://docs.qoder.com/zh/cli/plugins-reference
> IDE 侧概览见 `ide/05-plugins.md`

插件是可安装的扩展包，为 Qoder 添加**命令、Agent、Skills、Hooks、输出风格、工作流和 MCP 服务器**。

## Manifest：`.qoder-plugin/plugin.json`

⚠️ **manifest 放在 `.qoder-plugin/` 子目录下，不是插件根目录。**
该文件**可以省略** —— 未声明时按约定目录加载组件，以插件目录名作为插件名。
建议声明以获得稳定的 `name`、`version`。

**唯一必填字段**：`name`（kebab-case，不含空格）。

### 可选元信息

`version` / `displayName` / `description` / `author`(name/email/url) / `homepage` /
`repository` / `license`(SPDX) / `keywords` / `dependencies`（依赖的其他插件，可指定 marketplace）

### 组件声明字段（覆盖约定目录或内联声明）

| 字段 | 说明 |
|---|---|
| `commands` | 命令定义 |
| `agents` | Agent 定义文件路径 |
| `skills` | 技能目录路径 |
| `outputStyles` | 输出风格定义 |
| `workflowsPath` / `workflowsPaths` | 工作流文件路径 |
| `hooks` | Hook 配置（相对路径 JSON 或**内联配置**） |
| `mcpServers` | MCP 服务器配置（相对路径 JSON 或内联） |
| `userConfig` | 用户可配置选项定义 |
| `settings` | 插件启用时合并的配置。**当前仅支持 `agent` 键，其余键被忽略** |

## 约定目录结构

```text
plugin-name/
├── .qoder-plugin/
│   └── plugin.json      # 推荐：manifest（可省略）
├── commands/            # 命令定义（.md），支持嵌套目录
├── agents/              # Agent 定义（.md）
├── skills/
│   └── skill-name/
│       └── SKILL.md
├── hooks/
│   └── hooks.json       # Hook 配置
├── output-styles/
├── workflows/
├── bin/                 # 可执行文件（加入 PATH）
└── .mcp.json            # MCP 服务器配置
```

> 兼容 `mcp.json`（无前导点）作为回退。两者同存时 **`.mcp.json` 优先，且不会合并**。

## ⭐ 这是本项目 `.trae/` 资产的最佳落点

`.trae/` 下同时有 agents / skills / steering / hooks / mcp-servers / scripts —— 
**结构上与插件的约定目录几乎一一对应**：

| `.trae/` 现有 | 插件对应目录 |
|---|---|
| `.trae/agents/*/agent.md` | `agents/*.md`（需改成单文件 + frontmatter） |
| `.trae/skills/*/SKILL.md` | `skills/*/SKILL.md`（**结构不用改**） |
| `.trae/steering/*.md` | 无直接对应 → 转成 `commands/` 或项目 `rules/` |
| `.trae/hooks.json` | `hooks/hooks.json`（需按 Qoder 事件名重写） |
| `.trae/mcp-servers/` | `.mcp.json` |
| `.trae/scripts/` | `bin/`（自动加入 PATH） |

打成一个插件的好处：**整套资产可版本化、可分发给团队、可一键 enable/disable**，
比散落在项目目录里更可控。代价是要维护 manifest。

## Marketplace（`marketplace.json`）

**必需**：`name` / `owner`(name/email/url) / `plugins`（插件条目数组）
**可选**：`forceRemoveDeletedPlugins`（市场中删除的插件自动卸载）/ `metadata.pluginRoot` /
`metadata.version` / `metadata.description` / `allowCrossMarketplaceDependenciesOn`

**插件条目**：`name`（须与 `plugin.json` 的 `name` 一致）/ `source`（相对路径、npm、git、github、url）/
`category` / `tags` / `strict`（是否要求存在 manifest，默认 `true`）

## 管理命令

**交互式 `/plugins`**（别名 `/plugin`，不带子命令时打开插件浏览器）：
`install`(i) / `uninstall`(remove,rm) / `enable` / `disable` / `update`* /
**`validate <path>`**（校验插件目录或 plugin.json）/ `marketplace`(market)* / **`reload`**

**命令行 `qoder plugins`**（别名 `plugin`）：
`list` / `install`(i) / `uninstall` / `enable` / `disable` / `update`* / `validate` / `marketplace`(mp)*

\* 受插件市场功能开关控制，未启用时不可用。

启动参数：`--plugin-dir <path>` 附加插件搜索目录。

## 安全

```json
{
  "security": {
    "blockGitExtensions": true,
    "allowedExtensions": ["^https://github\\.com/my-org/"]
  }
}
```
（`security` 分组，**需重启**）

- `blockGitExtensions: true` 阻止从 Git 安装/加载插件
- `allowedExtensions` 是来源正则白名单，**非空时仅允许匹配的来源（覆盖 `blockGitExtensions`）**
