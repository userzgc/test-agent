# 规则 Rules（Qoder IDE）

> 来源：https://docs.qoder.com/zh/user-guide/rules
>
> ⚠️ **本篇已被 `cli/03-rules-and-memory.md` 部分修正**：
> IDE 页面只讲「类型通过 IDE 设置界面选择」，但 CLI 文档明确说
> 「Qoder CLI 的 rules frontmatter **兼容 Qoder Desktop 中配置的 rules 设置**」，
> 即四种生效方式**可以直接写 frontmatter**（`trigger: always_on|manual|model_decision|glob`、
> `alwaysApply`、`description`、`glob`、`paths`）。写规则文件时以 CLI 那篇为准。

## 存放位置

**`.qoder/rules/` 目录，仅对当前项目生效。**

- 规则文件直接放在项目目录，随代码库一起用 Git 与团队共享
- 只想本地用（不共享）→ 把 `.qoder/rules` 加进 `.gitignore`

## 限制

- **所有活跃规则文件合计最多 100,000 字符**（超出部分被截断）
- **仅支持自然语言，不支持图片或链接**

## 4 种规则类型

| 类型 | 描述 | 使用场景 |
|------|------|---------|
| **手动引入** | 在智能会话面板或行间会话用 `@rule` 手动应用 | 按需工作流、自定义提示词 |
| **模型决策** | 模型在智能体模式下评估规则描述，自行决定何时应用 | 场景化任务（生成单测、代码注释） |
| **始终生效** | 适用于所有智能会话和行间会话请求 | 强制项目级标准（编码风格、文档格式） |
| **指定文件生效** | 适用于匹配通配符的所有文件（如 `*.js`、`src/**/*.ts`） | 语言或目录特定规则 |

## AGENTS.md 兼容性

Qoder IDE 规则**原生兼容 `AGENTS.md`**：

1. 把 `AGENTS.md` 复制到项目目录
2. Agent 自动识别并使用其中定义的规则
3. **无需额外配置，集成无缝**

> **冲突时 `.qoder/rules/` 的规则内容优先于 AGENTS.md。**

## 配置方式（通过 UI，不是 frontmatter）

1. 右上角用户图标 或 `⌘⇧,`（macOS）/ `Ctrl Shift ,`（Win）→ **Qoder IDE 设置**
2. 左侧导航 → **规则**
3. 点 **添加**
4. 顶部搜索栏输入唯一的规则名称 → **确认**
5. 选择规则类型：
   - **手动引入**
   - **模型决策** → 需输入场景描述，例："生成一个单元测试"
   - **指定文件生效** → 提供逗号分隔的通配符，例：`*.md`、`src/*.java`
   - **始终生效**
6. 关闭窗口保存

> 编辑/删除现有规则：在**规则**页面点对应图标。

## 与其他框架的对照（重要）

| | 声明方式 |
|---|---|
| **Kiro** | `.kiro/steering/*.md` + frontmatter `inclusion: auto\|manual\|fileMatch` |
| **Trae** | `.trae/rules/{user,project}_rules.md` + frontmatter `paths:` |
| **Qoder** | `.qoder/rules/*.md`，类型通过 **IDE 设置界面**选择；或直接用 `AGENTS.md` |

⚠️ `inclusion:` 是 Kiro 语法，Qoder **不识别**。`#[[file:xxx]]` 引用语法同样是 Kiro 专有。

## 最佳实践

- **保持简洁**：规则聚焦、无歧义
- **结构清晰**：用项目符号、编号列表、Markdown 格式
- **包含示例**：给出"良好"代码示例
- **迭代优化**：根据模型输出和反馈持续完善
