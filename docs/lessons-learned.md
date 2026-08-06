# 踩坑记录

> 按时间倒序，最新在上。每条记录遵循 `.trae/steering/self-improvement.md` 中的格式。
> Stop Hook 会自动检查每日是否有新踩坑记录。

---

## 2026-08-06 工具能力：GLM-5.2 不支持视觉识别

- **问题**：用户要求识别蓝湖设计稿、墨刀原型稿、Confluence/飞书文档中的截图，但当前 GLM-5.2 模型不支持视觉识别（非 VLM），上传图片会报错 code:20041 "The model is not a VLM"
- **根因**：Trae IDE 支持多模态输入（拖图片到对话框），但能否"看到"图片取决于所用模型。GLM-5.2 是纯文本模型，无视觉能力
- **解决方案**：
  1. 创建 `design-extractor` agent 统一收口视觉类输入
  2. 优先走结构化数据路径（蓝湖 MCP/导出 JSON、墨刀导出 HTML、Confluence HTML）
  3. 图片下载到本地后，提示用户拖入对话（需切换到支持视觉的模型如 Kimi-K2.7-Code）
  4. OCR 脚本作为兜底（提取文字，但无法理解布局/交互）
- **关联文件**：`.trae/agents/design-extractor/agent.md`
- **知识库更新**：`references/llm-wiki/trae-docs/` 补充多模态输入文档
- **Agent更新**：新增 design-extractor agent
- **脚本更新**：待创建 `extract_confluence_images.py`、`ocr_images.py`（按需）

---

## 2026-08-06 需求分析：只看简版需求做过度推测

- **问题**：分析买A赠B二期需求时，只看了 Confluence 上的简版需求文档（4.6KB），就基于一期经验做了大量推测性分析，列了8个"待确认问题"和7个"风险点"。用户补充了飞书 wiki 上的完整技术方案（29.7KB）后，发现其中 6 个"待确认问题"已被技术方案明确解答，根本不阻塞
- **根因**：
  1. 只看了 Confluence 上的需求 PRD，没有主动询问是否有技术设计文档
  2. 基于一期经验做了过度推测，把"二期可能改的"当成"二期不确定的"
  3. 没有区分"需求文档未明确"和"技术方案已确认"两种情况
- **解决方案**：
  1. 需求分析时，主动询问是否有技术设计文档
  2. 区分"需求文档层面"和"技术方案层面"的确认点
  3. 先读完整技术方案再列待确认问题，避免无意义的阻塞项
- **关联文件**：`docs/requirements/买A赠B二期_需求分析.md`（基于完整技术方案重写）
- **知识库更新**：无
- **Agent更新**：requirements-analysis skill 应补充"需求分析前先问有没有技术设计文档"
- **脚本更新**：无

---

## 2026-08-06 机制建立：误判 Trae 不支持项目级 Hook

- **问题**：初期判断 Trae 只支持企业版 HTTP Hook，不支持项目级 `.trae/hooks.json`，导致自改进机制设计成"靠 AI 自觉检查"
- **根因**：查文档时只看到"企业 Hook"页面，没有找到"项目 Hook"的文档；实际上 Trae 有独立的项目级 Hook 文档 `https://docs.trae.cn/ide_automate-actions-with-hooks`
- **解决方案**：
  1. 创建 `.trae/hooks.json` 配置 Stop / SessionStart / PostToolUse 事件
  2. 创建 `.trae/hooks/` 目录存放执行脚本
  3. 重写 `self-improvement.md` 为基于 Hook 的自动触发机制
- **关联文件**：`.trae/hooks.json`、`.trae/hooks/on-stop-check-lessons.sh`、`.trae/steering/self-improvement.md`
- **知识库更新**：无
- **Agent更新**：无
- **脚本更新**：新增 `.trae/hooks/on-stop-check-lessons.sh`、`session-start.sh`、`post-tool-feishu-auth.sh`

---

## 2026-08-06 项目初始化：skill 和脚本缺失

- **问题**：项目记忆里记录了 `.trae/skills/` 有4个测试技能，但实际目录不存在；case-writing agent.md 中引用了 XMind 生成逻辑，但没有独立脚本，每次都要临时写
- **根因**：从 ssos 项目拆分 test-agent 时，只迁移了 agents/steering/wiki，遗漏了 skills 和工具脚本；脚本原本嵌在 wiki 和 agent.md 里作为代码片段，不是独立可执行文件
- **解决方案**：
  1. 从 `ssos/.trae/skills/` 复制 4 个 skill 到 `test-agent/.trae/skills/`
  2. 新建 `.trae/scripts/` 目录，抽取 xmind 生成/解析、yapi 解析、飞书解析为独立 .py 文件
  3. 更新 case-writing agent.md 和 utils agent.md 改为脚本调用方式
- **关联文件**：
  - `.trae/skills/*/SKILL.md`
  - `.trae/agents/case-writing/agent.md`
  - `.trae/agents/utils/agent.md`
  - `references/llm-wiki/wiki/xmind.md`
- **知识库更新**：无（本次是结构问题，不是知识问题）
- **Agent更新**：case-writing、utils（改为脚本调用）
- **脚本更新**：新增 `.trae/scripts/gen_xmind.py`、`parse_xmind.py`、`parse_yapi.py`、`parse_feishu.py`

---

## 2026-08-06 一期用例解析：单行JSON无法直接读取

- **问题**：`docs/test-cases/买 a 赠 b 一期用例.json` 是 XMind 导出的单行 JSON，超过 20KB 读取限制，无法直接用 Read 工具查看完整结构
- **根因**：XMind 导出的 JSON 没有换行格式化，整个文件是一行
- **解决方案**：用 Python 脚本解析 JSON 并按树形结构打印到临时文件，再读取
- **关联文件**：`docs/test-cases/买 a 赠 b 一期用例.json`、`/private/tmp/parse_case.py`
- **知识库更新**：`references/llm-wiki/wiki/xmind.md` 应补充"一期用例是单行JSON，需用脚本解析"
- **Agent更新**：无
- **脚本更新**：`parse_xmind.py`（将此能力固化为常驻脚本）
