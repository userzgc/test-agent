# `.trae/` 目录结构与作用域

> 来源：社区整理 + 官方文档

## 作用域层级（从内到外）

| 层级 | 路径 | 用途 | Git 提交 |
|------|------|------|---------|
| 项目级（团队共享） | `<项目>/.trae/` | 团队配置，提交 Git | ✅ |
| 用户级（个人全局） | `~/.trae/` | 个人偏好，跨项目复用 | 不提交 |
| 本地覆盖（仅本机） | `.trae/settings.local.json` | 临时实验，不污染团队 | 🟡 gitignored |

## 项目级 `.trae/` 目录结构

```
your-repo/
├── CLAUDE.md                  # 兼容 Claude Code 的团队共享规则
├── CLAUDE.local.md            # 本地有效（gitignored）
└── .trae/
    ├── settings.json          # 团队共享行为配置
    ├── settings.local.json    # 本地有效（gitignored）
    ├── mcp.json               # MCP Server 配置
    ├── hooks.json             # Hook 配置（项目级）
    ├── rules/                 # 规则
    │   ├── user_rules.md     # 个人规则（项目级）
    │   └── project_rules.md  # 项目规则
    ├── skills/                # 技能
    │   └── <skill-name>/
    │       └── SKILL.md
    ├── agents/                # 自定义智能体
    │   └── <agent-name>/
    │       └── agent.md
    └── hooks/                 # Hook 执行脚本（自定义约定）
        └── *.sh
```

## 配置优先级
**项目 rules > 用户 rules > 默认行为**

项目级配置 > 用户级配置，确保团队规范不被个人偏好覆盖。

## settings.json vs settings.local.json
| 文件 | 用途 | Git |
|------|------|-----|
| `.trae/settings.json` | 行为配置（团队共享） | ✅ 提交 |
| `.trae/settings.local.json` | 本地实验/临时调整 | 🟡 gitignored |
| `~/.trae/settings.json` | UI 状态、用户偏好 | 不在项目内 |

## 常见误区
1. **全局生效的 project_rules.md** — project_rules.md 是项目级，不跨项目生效
2. **MCP 配置位置** — MCP 在 `.trae/mcp.json`，不是 settings.json
3. **skills 作用域** — 项目级 skills 是团队协作最佳实践，即使有全局 skills
4. **Hook 目录** — `.trae/hooks/` 不是 Trae 强制约定，是脚本目录的约定。配置必须放在 `.trae/hooks.json`

## 最佳实践
- **团队共享配置提交 Git**：rules、agents、skills、mcp.json、settings.json
- **个人偏好留本地**：settings.local.json、CLAUDE.local.md
- **按目录分规则**：用 `paths` frontmatter 让规则只在特定路径生效
- **项目级优先**：需要团队一致的配置放项目级，个人习惯放用户级
