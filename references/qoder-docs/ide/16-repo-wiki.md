# Repo Wiki（Qoder IDE）

> 来源：https://docs.qoder.com/zh/user-guide/repo-wiki

自动为项目生成结构化文档，并**持续跟踪代码与文档的变更**。让智能体具备更深入的代码库认知：
架构类问题（「X 是如何实现的」「哪些服务依赖此模块」）几乎不用调工具就能答；
上下文宽度受限时可加速代码定位。

## 生成与更新的四种情形

| 情形 | 触发 | 操作 |
|---|---|---|
| **初次生成** | 首次打开项目时默认无 Wiki | 一键从零生成 |
| **检测到代码变更** | 已被 Wiki 记录的内容（函数签名、类定义、API 端点）被改 | 点「**更新**」只重生成受影响部分 |
| **Git 目录同步** | 你直接在 Git 目录里改了 Wiki 的 md | 点「**同步**」把 Git 变更并回 Wiki |
| **限制** | 每项目最多 **10,000 个文件**；**仅支持 Git 仓库且至少一次提交** | 超限时到 设置 → 代码库索引 → 索引排除 排掉非必要路径 |

## `/knowledge` — 生成后的人工干预

| 操作 | 说明 |
|---|---|
| **生成** | 首次为项目生成 Wiki 或知识卡片 |
| **修改** | 对已有知识内容局部修改 |
| **补充** | 向已有知识追加新内容 |
| **重写** | 完全重写某个知识页面或卡片 |

用法：输入框唤起 `/knowledge` → 描述变更 → **可配合上传本地文件作为参考**（设计文档、API 文档等）。

> ⭐ **人工修改的内容会被系统标记和保护，下次自动更新不会覆盖**，
> 而是反向同步到对应知识卡片。这是「把人的判断写进知识资产」的官方机制。

## ⭐ `wiki_plan.yaml` — 生成**前**的干预（本项目最该用的一项）

用 **`/knowledge-plan`** 命令创建或编辑。

**文件位置**（本项目已存在 `.qoder/repowiki/`，可直接加这个文件）：
```text
<项目根目录>/.qoder/repowiki/wiki_plan.yaml
```
该文件**随 Git 提交共享给团队**。

```yaml
version: 1

repowiki:
  template: ""           # 预制模板（architecture / product_requirement）
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
| `repowiki.template` | `architecture`（全面分析技术架构）/ `product_requirement`（按产品需求格式输出） |
| `repowiki.notes` | 引导提示，注入规划阶段引导 AI 关注指定重点 |
| `repowiki.documents` | 页面白名单，**提供时严格按列表生成** |
| `knowledgecard.notes` | 知识卡引导提示，影响**模块划分方向** |
| `scope.include / exclude` | 控制生成时可见的文件范围 |

> ⚠️ 改完 `wiki_plan.yaml` 后**需手动触发「生成」或「重新生成」**才生效。

### 🎯 对本项目的直接价值

本项目 `.qoder/repowiki/zh/content/` 下已有一批自动生成的文档（API 参考 / Agent 系统 / 工作流管理…），
但内容是**按代码仓库视角**生成的，而本项目本质是「测试工作流资产库」不是代码库，
所以生成结果里大量条目（如「Agent调用接口」「部署运维」）名不副实。

正确做法：写 `.qoder/repowiki/wiki_plan.yaml`
- `repowiki.template: product_requirement`（本项目是需求/用例资产，不是技术架构）
- `repowiki.documents` 用白名单锁定真正需要的页面（需求分析产物、用例资产清单、接口矩阵、踩坑与规范）
- `scope.exclude` 排掉 `references/**`（那是外部文档镜像，不是本项目知识）
- `repowiki.notes` 写明「本仓库是 QA 测试资产库，文档应聚焦需求→用例→评审链路，不要按代码架构组织」

## 共享

团队管理员在 Web 控制台开启**知识中心**开关后，成员生成的 Repo Wiki 自动同步至团队
（**仅 Teams 版支持**）；否则走 Git 同步——`.qoder/repowiki` 目录提交推送，成员 `git pull` 即可。

## 多语言

生成时选语言，按语言分目录：`repowiki/zh/`、`repowiki/en/`。目前支持 English 和中文。

## 计费

生成和更新**消耗 Credits**。
