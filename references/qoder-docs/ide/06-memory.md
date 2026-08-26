# 记忆（Qoder IDE）

> 来源：https://docs.qoder.com/zh/user-guide/knowledge-engine/memory
> 完整机制见 `cli/03-rules-and-memory.md`；未加载排查见 `cli/10-troubleshoot-loading.md`

Qoder IDE 提供长期记忆。随着交互，会逐步构建一套记忆库，涵盖**个人开发者、特定项目、遇到的问题**等信息，
并**随时间自动整理更新**。

## 主动记忆

在智能会话面板切换到**智能体模式**，直接输入希望 Qoder 记住的内容 → Qoder 保存。
稍后在智能会话面板中询问即可检索。

## 查看与管理记忆

**底部栏或左侧导航 → 知识中心 → Memory 面板**：

- **搜索与筛选**：支持按**成熟度、分类、项目**筛选
- **管理**：编辑或移除条目
- 另一入口：Editor 的 **Qoder IDE 设置 → 记忆**

## 记忆范围

在项目中工作时，**全局记忆（个人偏好）与项目特定记忆同时被激活**，在所有交互中生效。

## 🎯 对本项目的意义

- `docs/lessons-learned.md` 这类手写踩坑文档没有任何机制保证被读到；
  同样的内容写成记忆（或通过 `/knowledge` 进知识卡片）才会被主动激活
- **记忆是自动整理更新的**，不需要手工维护一份「规范 md」
- ⚠️ 但记忆是**补充上下文**，不是硬约束。真正要「禁止某个行为」得靠
  Rules（`always_on`）或 Hooks（`PreToolUse` + `deny`），见 `cli/07-hooks-guide.md`
