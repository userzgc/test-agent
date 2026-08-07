# 踩坑记录

> 按时间倒序，最新在上。每条记录遵循 `.trae/steering/self-improvement.md` 中的格式。
> Stop Hook 会自动检查每日是否有新踩坑记录。

---

## 2026-08-06 墨刀原型解析：技术方案 `max=100` 与原型标注「1~30 个」不一致 + 墨刀 SPA 不能 curl

- **问题**：
  1. 墨刀分享页是 SPA（`<div id="workspace"></div>`），直接 `curl` 拿到的是空壳，无法获取原型内容
  2. 墨刀无公开的「读取已有项目」API（只有生成 API），尝试 `/api/oembed`、`/proto/{id}/sharing.json`、`/api/share/{id}` 全部 404 或返回 SPA 空壳
  3. 解析用户用浏览器「另存为网页」保存的 HTML 后，发现原型标注「赠品数量可为 1~30 个」，但 V2 技术方案 §3.3.2 写的是 `@Size(min=1, max=100)`，两个文档口径不一致
- **根因**：
  1. 墨刀是 SPA，所有内容靠 JS 渲染，curl 抓不到
  2. 墨刀没有公开 API 读取项目内容，只能依赖用户配合（导出 HTML 或截图）
  3. 技术方案写的是**接口防御边界**（max=100），原型标注写的是**产品业务边界**（1~30），两份文档没有对齐
- **解决方案**：
  1. 墨刀/蓝湖等 SPA 设计稿工具，**直接 curl 拿不到内容**，让用户用浏览器「另存为网页（完整 HTML）」保存，再解析 DOM 提取可见文本（设计稿的标注文字在 DOM 里）
  2. 解析 HTML 时，用 Python `HTMLParser` 提取 `handle_data` 的中文文本，配合 `handle_starttag` 提取 `img alt`、`input placeholder`、`button class` 等结构化信息
  3. **技术方案与原型/PRD 的数值/口径不一致时，必须当作待确认问题**（不能默认以技术方案为准），找开发/产品对齐
  4. 数值边界用例按业务边界（30）和接口边界（100）分别设计，避免漏测
- **关联文件**：`/tmp/extract_modao.py`（HTML 解析脚本）、`docs/requirements/买A赠B二期_需求分析.md`（Q9 待确认）
- **知识库更新**：无
- **Agent更新**：design-extractor agent 补充「墨刀 SPA 不能直接 curl，需用户配合导出 HTML 或截图」+ 「技术方案与原型口径不一致时必须标为待确认问题」
- **脚本更新**：`/tmp/extract_modao.py` 可复用为通用 HTML 设计稿解析工具

---

## 2026-08-06 需求分析：技术方案写"完全不变"不等于不需要回归 + 分账场景设计维度错误

- **问题**：
  1. 分析买A赠B二期技术方案时，看到"寄存券/发券/核销/补贴/订单履约/退款任何改动""赠品发放/核销/补贴 现有链路完全不变"就判定"不需要专项测试"，遗漏了分账链路回归
  2. 补分账场景时，按"主品组合模式（单组/多组）× 周边赠品"维度设计，被用户纠正：分账基于**赠品的结算比例配置**，与主品组合模式无关
- **根因**：
  1. 技术方案写"完全不变"是从代码改动角度说的（无代码变更），但从测试角度，商品类型新增了 BRAND_MERCH=12，下游分账逻辑是否能正确识别新类型，必须验证
  2. 只看技术方案的"改动矩阵"标记"不改"就跳过了，但商品类型枚举变更是全局影响，即使链路代码不改，新值传过去也可能出问题
  3. 遗漏了"专享价同享"价格叠加场景和"C端多主品展示样式"，这些是用户测试侧重点但技术方案没有单独列出
  4. 分账场景设计时没搞清业务维度——分账只跟赠品结算比例配置有关（无补贴/固定/比例100%/比例90%有上限/不超优惠金额），跟主品怎么组合无关
- **解决方案**：
  1. 区分"代码零改动"和"数据流新增枚举值"——枚举值新增即使链路不改，也要回归下游是否兼容
  2. 需求分析完后，主动问用户"测试侧重点是什么"，不要只靠文档推断
  3. 改动矩阵中标记"不改"的维度，要判断是否有新增枚举/参数传入，有则必须列回归场景
  4. C端展示样式不要等设计稿，先基于需求文档列出基础展示场景，设计稿到手后补充细节
  5. 设计回归场景时，先搞清业务驱动维度（如分账=赠品结算比例配置），不要按代码改动点机械拆分
- **关联文件**：`docs/requirements/买A赠B二期_需求分析.md`（分账场景改为6种结算模式 × 赠品类型 × 下单/退款）
- **知识库更新**：无
- **Agent更新**：requirements-analysis skill 补充"改动矩阵标记'不改'但有枚举新增时仍需回归"+"回归场景按业务驱动维度设计，不按代码改动点拆分"
- **脚本更新**：无

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
