# 知识中心与 Repo Wiki（Qoder IDE）

> 来源：https://docs.qoder.com/zh/user-guide/knowledge-engine/overview
> + https://docs.qoder.com/zh/user-guide/repo-wiki

## 知识中心的三类知识来源

| 来源 | 说明 |
|---|---|
| **Repo Wiki** | 基于代码库自动生成的结构化文档，覆盖项目架构、模块关系与实现细节 |
| **知识卡片 Knowledge Card** | 从代码中提炼的高密度知识单元，含架构文档、代码规约（Spec）和技术栈信息 |
| **对话记忆 Memory** | 从每次对话中自动提炼的踩坑记录、决策依据和项目经验，持久化沉淀为可复用知识 |

两条自动沉淀路径：
- **代码侧**：生成 Repo Wiki 时，系统自动把代码意图、设计方案和上下文讨论提炼为知识卡片
- **对话侧**：与 Agent 交互中的踩坑记录、决策依据和项目经验，自动提炼为 Memory 知识

> ⭐ **对本项目的意义**：`docs/lessons-learned.md` 这种手写踩坑记录，在 Qoder 里
> 本来就有原生承载体（对话侧 Memory 自动沉淀）。手写文档没有任何机制保证它会被读到，
> 而 Memory 是框架层注入的。

## Repo Wiki

本项目 `.qoder/repowiki/` 就是它的产物——**已经在工作了**，是当前唯一真正生效的 Qoder 原生资产。

### 使用场景

- **架构与实现相关查询**：凭预构建的架构知识，几乎无需调工具即可回答
  「X 是如何实现的？」「哪些服务依赖此模块？」
- **智能体驱动的开发任务**：上下文宽度受限时加速代码定位（加功能、修 bug）

### 生成与更新的四种情形

1. **初次生成** — 首次打开项目时默认不存在，一键从零生成
2. **检测到代码变更** — 修改了 Wiki 已记录的内容（函数签名、类定义、API 端点）时，
   系统检测到不一致，点 **更新** 仅重新生成受影响部分
3. **Git 目录同步** — 直接在 Git 目录中编辑 Markdown 时，系统检测到不一致，点 **同步**
4. **生成限制** —
   - 每个项目**最多 10,000 个文件**（超出请在 设置 → 代码库索引 → 索引排除 中排除非必要路径）
   - **仅支持 Git 仓库且至少有一次提交**

### `/knowledge` 命令 — 生成后干预

| 操作 | 说明 |
|---|---|
| **生成** | 首次为项目生成 Wiki 或知识卡片 |
| **修改** | 对已有知识内容做局部修改 |
| **补充** | 向已有知识追加新内容 |
| **重写** | 完全重写某个知识页面或卡片 |

用法：唤起 `/knowledge` → 描述变更 → **可配合上传本地文件作为参考**（设计文档、API 文档等）。

⭐ **人工修改的内容会被系统标记和保护——下次自动更新时不会被覆盖**，
而是**反向同步到对应的知识卡片**中。

### ⭐ `wiki_plan.yaml` — 生成前置干预配置

`/knowledge-plan` 命令创建或编辑。**位置**：

```text
<项目根目录>/.qoder/repowiki/wiki_plan.yaml
```

该文件**随 Git 提交共享给团队**。

```yaml
version: 1

repowiki:
  template: ""           # 预制模板：architecture / product_requirement
  notes:                 # 注入规划阶段的引导提示
    - text: "提示文本"
      author: "署名"
  documents:             # 页面白名单（提供时严格按列表输出）
    - title: "页面标题"
      goal: "该页面的写作意图"
      parent: ""         # 可选，父页面标题
      hints: ""          # 可选，额外写作提示

knowledgecard:
  notes:                 # 注入知识卡规划阶段的引导提示
    - text: "提示文本"

scope:
  include: []            # 文件白名单（.gitignore 语法）
  exclude: []            # 文件黑名单（.gitignore 语法）
```

| 配置项 | 说明 |
|---|---|
| `repowiki.template` | `architecture`（全面分析技术架构）或 `product_requirement`（按产品需求格式输出） |
| `repowiki.notes` | 引导提示，注入规划阶段引导 AI 关注指定重点 |
| `repowiki.documents` | 页面白名单，**提供时严格按列表生成** |
| `knowledgecard.notes` | 知识卡引导提示，影响**模块划分方向** |
| `scope.include / exclude` | 控制生成时可见的文件范围 |

示例：
```yaml
version: 1
repowiki:
  notes:
    - text: "文档应聚焦业务流程而非代码细节，面向新入职工程师"
  documents:
    - title: "系统架构概览"
      goal: "描述系统整体架构、核心模块及其交互关系"
    - title: "订单系统"
      goal: "说明订单全生命周期"
      parent: "系统架构概览"
knowledgecard:
  notes:
    - text: "重点建模支付和订单两个核心子系统"
scope:
  include: ["src/**"]
  exclude: ["**/test/**"]
```

⚠️ **改完 `wiki_plan.yaml` 后需手动触发「生成」或「重新生成」才生效。**

> ⭐ **对本项目的意义**：当前 `.qoder/repowiki/` 是自动生成的、内容偏"代码架构"，
> 但本项目其实是**文档/流程仓库**而非代码仓库。用 `wiki_plan.yaml` 的
> `template: product_requirement` + `documents` 白名单 + `notes`，
> 可以把 Wiki 引导成"测试工作流说明书"而不是"代码架构文档"。

### 共享

- **Teams 版**：管理员在 Web 控制台开启**知识中心**开关后，任何成员生成的 Repo Wiki
  自动同步至团队；其他成员打开相同仓库相同分支点**生成**即自动获取团队最新知识
- **其他版本**：走 Git 同步——`.qoder/repowiki` 提交推送，成员 `git pull` 即可

### 多语言

生成时可选语言（目前 **English** 和 **中文**），会自动创建独立目录
`repowiki/zh/`、`repowiki/en/`。

### 计费

生成和更新**消耗 Credits**，可在 用量详情-Credits 查看。
