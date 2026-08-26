# Skills（Qoder IDE）

> 来源：https://docs.qoder.com/zh/extensions/skills
> **完整指南在 CLI 文档下**：https://docs.qoder.com/zh/cli/Skills
> 官方原话：「无论是在 Qoder IDE 还是 CLI 中，Skills 的使用方式完全一致。」

## 是什么

把专业知识打包成可复用功能。每个 Skill 一个 `SKILL.md`，定义描述、指令和可选辅助文件。

**核心特点**：
- **智能调用**：模型根据用户请求和 Skill 描述**自主决定何时使用**
- **模块化**：每个 Skill 专注一类任务
- **灵活扩展**：支持用户级和项目级

## 存放位置

| 位置 | 路径 | 作用域 |
|------|------|--------|
| 用户级 | `~/.qoder/skills/{skill-name}/SKILL.md` | 当前用户的所有项目 |
| 项目级 | `.qoder/skills/{skill-name}/SKILL.md` | 仅当前项目 |

**同名时项目级优先。**

> ⚠️ **优先级官方文档自相矛盾**：上面这句来自 IDE 页面，但两篇 CLI 文档都写的是
> 「**用户级覆盖项目级**」（完整优先链：内置 < 插件 < 项目级 < 用户级）。
> 详见 `cli/01-skills.md`。**实操建议：不要依赖同名覆盖，避开同名即可。**

⚠️ **创建后必须重启 Qoder IDE**，然后在对话框输入 `/` 才能看到已加载的 Skills 列表。

## 触发方式

1. **自动触发**：直接描述需求，模型自动判断
   例：「分析这个日志文件中的错误」→ 自动调用 `log-analyzer`
2. **手动触发**：`/skill-name`

## 三种创建方式

### 1. 内置 `/create-skill`（推荐新手）

```
/create-skill <技能描述，例如：将 Word 文档转换为 PDF>
```

交互式对话引导，生成符合规范的 SKILL.md。

### 2. Skills CLI 安装第三方

```bash
# 从 skills.sh 市场
npx skills add vercel-labs/agent-browser -a qoder

# 从 GitHub 仓库安装指定技能
npx skills add https://github.com/anthropics/skills --skill skill-creator -a qoder
```

> 注意 `-a qoder` 参数指定目标工具。详见 https://github.com/vercel-labs/skills

### 3. 手动创建

建目录 + `SKILL.md` → 放到上表两个路径之一 → **重启 IDE**。

## 适用场景

- **复杂专业任务**：需要领域知识的工作流（代码审查、PDF 处理、API 设计）
- **标准化流程**：固定步骤的任务（提交规范、部署流程）
- **团队知识共享**：打包最佳实践
- **重复性工作**：频繁执行且需专业指导的任务

## 内置 Skills（部分）

| 名称 | 用途 |
|------|------|
| `/create-skill` | 引导创建新 Skill |
| `/create-skill-ui` | 为 Skill 生成交互式 HTML Widget |
| `/create-subagent` | 脚手架自定义子智能体 |
| `/vercel-deploy` | 一键 Vercel 部署（OAuth + 构建） |
| `/canvas` | 在 Canvas 预览中创建/编辑 `.canvas.tsx` 视觉产物 |

### Skill UI

Agent 可在执行过程中直接渲染可交互 HTML 组件（表单、图表、配置面板），内嵌在对话流中，
无需跳外部页面。用 `/create-skill-ui` 为指定 Skill 创建界面，实时预览迭代后存为模板文件。
（在 Quest 的 Agent 模式中使用。）

## 与 Trae / Kiro 的对照

| | 路径 | frontmatter |
|---|---|---|
| **Kiro** | `.kiro/skills/{name}/SKILL.md` | `name`（kebab-case，与目录同名）、`description`（**必须以 "Use when" 开头**，否则 skill-check 扣 15 分）、可选 `inclusion` |
| **Trae** | `.trae/skills/{name}/SKILL.md` | `name`、`description` |
| **Qoder** | `.qoder/skills/{name}/SKILL.md` | `name`、`description` |

✅ **三代路径结构一致**，所以 Skill 是唯一「改目录名即可迁移」的资产。
`description` 决定模型能否自动选中该 Skill，因此 Kiro 时代的 "Use when ..." 写法在 Qoder 下依然有实际价值（虽非强制）。
