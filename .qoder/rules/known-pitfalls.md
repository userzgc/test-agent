---
trigger: model_decision
description: 已实测验证的工程踩坑库（团队共享）。调用 lark-cli 写飞书文档、生成或重生成 XMind、编写排查 hooks、新建迁移扩展资产、用脚本抓取 Confluence/禅道页面时引入。
---

# 已验证踩坑库

来源：实际执行中踩过并验证过修复的坑。个人 Qoder 记忆不随 git 同步，团队要用的经验以本文件为准。
新增踩坑：按「现象 / 根因 / 处置」三段追加，**条目末尾署名 `——<踩坑人>，YYYY-MM-DD`**
（踩坑人执行 `git config user.name` 获取，不要问用户），并同步落一条 `common_pitfalls_experience` 个人记忆。

> 第 1–5 类为 2026-08 自个人记忆批量迁入，踩坑人均为 userzgc，此后新增逐条署名。

## 1. 飞书 lark-cli

- **`partial_success` 必须当失败处理**。`ok=true` 具有误导性——写入后必须回读校验，且要核对「正文行数」而不只是标题存在。
- **sequenceDiagram 里的 `<br/>` 导致整图静默丢失**（`degrade_code=2107`，标题保留、图表正文整块丢弃）。写入前把 sequenceDiagram 块内 `<br/>` 替换为空格；`flowchart` / `graph` 不受影响。
- 定位这类渲染缺陷用**最小化用例二分**：追加带唯一标记的小块逐个试，`docs +fetch --detail with-ids` 取块 ID 后 `block_delete` 清理；补内容用 `block_insert_after` 锚定标题块 ID，别用 append。
- **lark-cli 是飞书取数的唯一权威工具**（`docs +fetch` / `docs +update --command overwrite`，`--doc-format markdown`）；`scripts/parse_feishu.py` 只是 CSV 解析器，抓不了 wiki 页。

## 2. XMind 产物

- **脚本重新生成的 XMind 会被桌面客户端「保存回旧版」**：客户端持有旧快照，一次自动保存就整体覆盖脚本产物，新增大类整片消失。
- 识别：`scripts/gen_xmind.py` 产物 zip 只有 3 个条目（content.json / metadata.json / manifest.json）；出现 `content.xml`、`Thumbnails/` 共 6 条目 = 被客户端保存过。文件 mtime 晚于脚本执行时间是第二信号。
- 处置：重生成前**让用户先关闭 XMind 里的该文件**；生成后用 `zipfile.namelist()` 校验条目数为 3、根节点子节点数与预期一致。用户反馈「看不到新增内容」时，先验磁盘文件真实内容，别默认是没刷新视图。

## 3. Qoder hooks

- **hook 脚本不能信 cwd**：平台触发时 cwd 不保证是仓库根，`git rev-parse` / `$PWD` 都会翻车且手动测试时不暴露。脚本一律用 `SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"` 按固定层级上溯出仓库根。
- **验证 hook 真触发用指纹法**：脚本里埋全仓唯一字符串，重启后看模型是否原样输出——指纹无法被「自觉」编出来。
- **`PostToolUseFailure` 只在工具层失败时触发**（fetch 拿 401/403、超时、MCP 崩）。shell 命令非零退出**不算**——Bash 工具本身成功了，走的是 `PostToolUse`。命令失败的处置靠 `failure-protocol.md` 规则，别指望 hook。
- Hooks 不热加载，改完必须重启 IDE；Rules 相反是自动热更新。

## 4. 扩展资产静默失效

- 配置写得再对，**放错目录就永不加载且无任何报错**。本项目历经  Trae → Qoder ，目录名和 frontmatter 全不兼容（Kiro `inclusion:` vs Qoder `trigger:`）。
- 排查「不生效」不要猜：先查目录信任，再跑 `/memory` `/skills` `/agents` `/hooks` `/mcp` 看实际加载结果。详见 `qoder-platform.md`。
- 同一失效模式的变体：知识写进 `docs/*.md` 或 `references/**` = 没有任何机制保证被读到，等于没写。要被自动加载就挂 AGENTS.md / rules。

## 5. Confluence / 动态页面抓取

- `scripts/extract_confluence_images.py` 的正则匹配的是 `<ri:filename ri:content-attr>`，但 Confluence 实际 HTML 是 `<ri:attachment ri:filename>`；且匹配不到时 **exit 0 静默成功**。拿不到图先怀疑脚本，再用 Playwright 兜底抓渲染后页面。
- Playwright 抓禅道等动态页：关键元素（如 table tbody）必须显式等待 + 重试 + 备用选择器，否则以 `user cancelled (40441)` 静默中断。
