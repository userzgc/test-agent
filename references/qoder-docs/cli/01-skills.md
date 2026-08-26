# Skills（Qoder CLI，权威版）

> 来源：https://docs.qoder.com/zh/cli/Skills
> IDE 摘要见 `ide/02-skills.md`。官方原话：「无论是在 Qoder IDE 还是 CLI 中，Skills 的使用方式完全一致。」

## ⚠️ 优先级：官方文档自相矛盾，以此处为准

- **CLI Skills 页**：「同名时，**用户级 Skill 覆盖项目级 Skill**。」（两处重复声明）
- **CLI troubleshoot-loading 页**：「Skills 来源为 **内置 < 插件 < 项目级 < 用户级**，同名时高优先级覆盖低优先级。」
- **IDE Skills 页**：「同名时**项目级优先**。」← 与上面两处冲突

两份 CLI 文档一致指向「**用户级最高**」，`ide/02-skills.md` 里记的"项目级优先"来自 IDE 页面。
**实操建议：不要依赖同名覆盖，直接避免用户级和项目级 Skill 同名。**

注意这与 Subagent 相反——Subagent 是 `Built-in < User < Project < Plugin < Flag`（**项目级高于用户级**）。

## 存放位置

| 位置 | 路径 | 适用场景 |
|---|---|---|
| 用户级 | `~/.qoder/skills/{skill-name}/SKILL.md` | 个人工作流、实验性 Skill、个人工具 |
| 项目级 | `.qoder/skills/{skill-name}/SKILL.md` | 团队工作流、项目特定知识、共享脚本 |

## 工作原理（渐进式加载）

1. **启动时只加载每个 Skill 的 `name` 和 `description`**，保持快速启动
2. 请求与 `description` 匹配时，模型请求使用该 Skill 并**加载完整 `SKILL.md`**
3. 模型按指令执行，**按需**加载引用文件或运行脚本

→ 所以 `description` 里必须包含**用户常用的关键词**，否则永远不会被选中。

## Frontmatter

| 字段 | 必需 | 说明 | 限制 |
|---|---|---|---|
| `name` | **是** | 唯一标识符 | 仅小写字母、数字、连字符，**最多 64 字符** |
| `description` | **是** | 功能描述，模型据此判断何时使用 | **最多 1024 字符** |

## 目录结构与渐进式披露

```
{skill-name}/
├── SKILL.md              # 必需：唯一必需文件
├── REFERENCE.md          # 可选：详细参考文档
├── EXAMPLES.md           # 可选：文档示例
├── scripts/              # 可选：辅助脚本
│   └── helper.py
└── templates/            # 可选：模板文件
    └── template.txt
```

在 `SKILL.md` 中引用辅助文件实现渐进式披露：
```markdown
For better usage, see [REFERENCE.md]. For examples, see [EXAMPLES.md].
Run the helper script: python scripts/helper.py input.txt
```

## Skill vs Command

| 特性 | Skill | Command |
|---|---|---|
| 触发方式 | **模型自动判断**或 `/skill-name` | 只能 `/command-name` |
| 主要用途 | 专业领域知识、复杂工作流 | 快速执行预设任务 |
| 存储位置 | `skills/` | `commands/` |
| 权限确认 | 视能力而定，可能需要授权 | 不需要 |

> Skill 内部转换为特殊类型的 Command，两者共享执行机制。

## 加载与刷新

- 新会话启动时加载
- 已在运行时用 **`/skills reload`** 刷新（IDE 侧则需重启）
- `/skills` 查看已加载列表（需 Skills 支持与管理员权限开启）
- 「What Skills are available?」也能问出来

## 排查未触发

```bash
ls ~/.qoder/skills/*/SKILL.md
ls .qoder/skills/*/SKILL.md
chmod +x .qoder/skills/my-skill/scripts/*.py   # 脚本权限
```

1. 确认 `SKILL.md` 存在且路径层级正确（必须是 `skills/<name>/SKILL.md`）
2. 检查 YAML frontmatter 无语法错误（缩进、引号）
3. `description` 是否够具体
4. **条件 Skill** 仅在文件路径匹配时激活，未匹配则不出现
5. 多个 Skill 相似导致混淆时，在 `description` 中用不同触发词区分

## description 写法对比（官方示例）

```yaml
# ❌ 模糊
description: Helps with logs

# ✅ 具体：功能 + 使用时机 + 触发关键词
description: Analyze log files to identify errors, patterns, and performance issues. Use when debugging logs, investigating errors, or monitoring application behavior.
```

```yaml
# ✅ 还可以声明依赖
description: Generate and manage database migrations, schema changes, and data transformations. Use when creating migrations, modifying database schema, or managing database versions. Requires sqlalchemy and alembic packages.
```

> 官方推荐格式与 Kiro 时代的 `Use when ...` 写法**完全一致**，
> 所以当前项目 9 个 skill 的 `description` 不用改。

## 其他最佳实践

- **保持专注**：`log-analyzer` / `security-auditor` / `database-migrator` ✅；`coding-helper` ❌ 太宽泛
- 共享前测试：预期场景能触发、指令清晰、覆盖边界情况
- 在 SKILL.md 里记版本历史

## 🔁 结论：Skill 是唯一「改目录名即可迁移」的资产

`.trae/skills/{name}/SKILL.md` → `.qoder/skills/{name}/SKILL.md`，结构、frontmatter、
description 约定全部一致。**9 个 skill 直接搬即可。**
