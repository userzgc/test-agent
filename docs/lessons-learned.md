# 踩坑记录

> 按时间倒序，最新在上。每条记录遵循 `.trae/steering/self-improvement.md` 中的格式。
> Stop Hook 会自动检查每日是否有新踩坑记录。

---

## 2026-08-20 流程偏差：对齐阶段写了没人看的中间态 md，skill 里早已明文禁止

- **问题**：
  1. 需求对齐过程中落了 `docs/requirements/资源位关联商品_测试场景.md`（第一版 56 条测试点），用户两次反馈：“能不能先别写 md 文件 这样每次对话的回复都好慢呀”、“因为我不会看这种东西”
  2. `资源位关联商品_设计图字段说明.md` 里的“展示时不检测、点击时才检测”在被用户纠正后没同步回文件，遗留错误结论
- **根因**：
  1. `.trae/skills/test-case-writing/SKILL.md` 开头就写了「**直接输出 XMind 文件，不再写 MD 用例文档**（用户反馈：MD 没人看）」，我未先读 skill 就开工
  2. 中间态 md 一旦落盘就成了“双份真相”，对齐口径变更时必需同步 N 份文件，必然遗漏
- **解决方案**：
  1. 任务开工前先读对应 skill，尤其是已带“用户反馈”标注的硬规则
  2. 对齐阶段全部在对话里进行，结论稳定后只落盘一次（已写入 `qa-workflow` 落盘时机原则）
  3. 业务口径只以 `docs/memory/decisions.md` 为单一权威源，其余文件引用而不复制
  4. 已删除 `资源位关联商品_测试场景.md`；`设计图字段说明.md` 的过期章节已标注纠正并指向 decisions.md
- **关联文件**：`.trae/skills/test-case-writing/SKILL.md`、`.trae/skills/qa-workflow/SKILL.md`、`docs/memory/decisions.md`
- **知识库更新**：无
- **Agent更新**：无
- **脚本更新**：新增 `.trae/scripts/gen_adbanner_xmind.py`

---

## 2026-08-20 脚本缺陷：on-stop-check-lessons.sh 的 `grep -c || echo "0"` 产生双值，输出折行

- **问题**：手动验证 Stop Hook 时输出为 `今日(2026-08-20)已有 0\n0 条踩坑记录`，`TODAY_COUNT` 变成了两行
- **根因**：
  1. `grep -c` 无匹配时**本身已经输出 `0`**，同时返回退出码 1
  2. 写成 `$(grep -c ... || echo "0")` 后，`||` 分支又追加一个 `0`，命令替换结果变成 `"0\n0"`
  3. 该写法在有匹配时不暂露（新加的 `MEMORY_COUNT` 因有 2 条匹配就没报错），属于**只在边界值暴露的隐患**
- **解决方案**：
  1. 改为 `$(grep -c ... || true)` 只吞退出码，不重复输出
  2. 另用 `VAR=${VAR:-0}` 兜文件不存在（grep 无任何输出）的情况
  3. 通用规则：**对 `grep -c` / `wc -l` 这类本身就会输出数字的命令，永远不要用 `|| echo <默认值>` 兜底**
  4. 新增/修改 Hook 后必须手动执行一次并看完整输出，不能只看退出码
- **关联文件**：`.trae/hooks/on-stop-check-lessons.sh`
- **知识库更新**：无
- **Agent更新**：无
- **脚本更新**：已修复并验证输出正常

---

## 2026-08-19 脚本缺陷：extract_confluence_images.py 正则与 Confluence 实际 storage 格式不匹配，下载 0 张图片

- **问题**：
  1. 执行 `python3 .trae/scripts/extract_confluence_images.py 120671446` 返回「找到 0 个 ac:image 附件, 0 个 img 标签」，实际页面有 6 处 `ac:image` 引用、9 个附件
  2. HTTP 200、认证正常、HTML 长度 3373 字符均正常，**脚本静默返回 0 且退出码为 0**，不报错，极易被误判为「页面没有图片」
- **根因**：
  1. `extract_ac_image_filenames()` 的正则写的是 `<ri:filename ri:content-attr="([^"]+)"/>`，即把 `ri:filename` 当作**标签名**、`ri:content-attr` 当作属性名
  2. Confluence 实际 storage 格式是 `<ac:image><ri:attachment ri:filename="xxx.png" /></ac:image>`，即 `ri:attachment` 是标签、`ri:filename` 是**属性**
  3. 两处正则（`pattern` 和 `pattern2`）犯的是同一个错，说明当初是凭猜测写的，没有拿真实页面 HTML 验证过
  4. 找不到图片时走「下载 0 张」的正常分支，没有「引用数为 0 但 HTML 非空」的异常告警
- **解决方案**：
  1. 正则改为匹配属性形式：`r'<ri:attachment[^>]*\sri:filename="([^"]+)"'`，并对结果去重（正文可能重复引用同一张图）
  2. 兜底改用附件 REST API：`GET /rest/api/content/{pageId}/child/attachment?limit=50`，从 `results[].title` 与 `_links.download` 取文件名和下载地址，比解析 HTML 更稳（本次即用此法成功下载 5 张）
  3. 注意区分「附件总数」与「当前正文引用数」：本页 9 个附件里有 4 个是历史版本遗留，全量下载会混入无关图片
  4. 增加异常告警：HTML 非空但提取到 0 个图片引用时，打印警告并以非 0 退出码结束，避免静默失败
- **关联文件**：`.trae/scripts/extract_confluence_images.py`、`.trae/skills/tool-usage/SKILL.md`、`docs/requirements/资源位关联商品_设计图字段说明.md`
- **知识库更新**：无
- **Agent更新**：无
- **脚本更新**：`extract_confluence_images.py` 正则修复 + REST API 兜底 + 静默失败告警（**待实现**）

---

## 2026-08-19 依赖缺失：ocr_images.py 依赖 pytesseract，但 OCR 对 UI 截图的布局/交互识别能力不足

- **问题**：
  1. `ocr_images.py` 因缺少 `pytesseract` 模块直接退出，而 `tesseract` CLI 本体已装好（含 chi_sim，163 种语言）
  2. 改用 `tesseract <img> - -l chi_sim+eng` CLI 后可出文字，但结果噪声大：中文误识别（「弹窗优先级」→「漳窗优先级」、「积分兑换」→「积分交换入吕」）、表单字段与选项错行混排、布局关系全丢
- **根因**：
  1. 脚本强依赖 Python 包，但 CLI 已可满足需求，多了一层无谓依赖（`ocr_images.py` 自己的 docstring 也写明它「无法识别布局/交互，仅提取文字」）
  2. UI 截图的核心信息是**字段位置、控件类型、选中态、联动关系**，这些是空间信息，OCR 原理上拿不到
- **解决方案**：
  1. 优先用多模态视觉直接读图，OCR 仅作为文字交叉校验的辅助手段，不作为主路径
  2. `ocr_images.py` 增加 CLI 兜底：`pytesseract` 不可用时降级为 `subprocess` 调 `tesseract`，避免因缺 Python 包而完全不可用
  3. 视觉读图前先按正文引用顺序给图片重命名（如 `03_关联商品字段.png`），能显著降低图文对应的成本
- **关联文件**：`.trae/scripts/ocr_images.py`、`.trae/skills/design-extraction/SKILL.md`
- **知识库更新**：无
- **Agent更新**：建议 `design-extraction` skill 明确「视觉读图为主、OCR 为辅」的优先级（**待实现**）
- **脚本更新**：`ocr_images.py` 增加 tesseract CLI 降级路径（**待实现**）

---

## 2026-08-10 机制失效：踩坑记录全靠用户提醒，自改进机制"即时记录"规则未执行

- **问题**：
  1. 禅道操作过程中遇到 7+ 个技术坑（SPA 渲染、iframe、API 401、URL 参数不生效等），全部没有即时记录
  2. 用户两次沟通后质问"为什么没有记录踩坑"，才补记了禅道技术坑
  3. 用户进一步追问"为什么没有自动记录？这是不是也是一个坑？"，暴露出自改进机制本身失效
  4. `self-improvement.md` 明确规定"工具失败必须当场记录，不等 Stop Hook"，但 Agent 完全没有执行
- **根因**：
  1. **规则是"软约束"不是"硬触发"**：self-improvement.md 写了"必须当场记录"，但没有任何机制在工具失败时强制插入"记录检查点"，全靠 Agent 自觉
  2. **Agent 执行模式偏差**：Agent 在连续解决技术问题时，会进入"推进任务"模式，把"记录过程"当作低优先级事项忽略
  3. **Stop Hook 检查时机太晚**：on-stop-check-lessons.sh 在会话结束时才输出检查清单，此时已经累积了多个坑，而且 Agent 可能直接结束不再处理
  4. **PostToolUse Hook 未启用**：虽然 self-improvement.md 提到 PostToolUse 可用于工具后检查，但只配了飞书授权检查（默认禁用），没有配"工具失败检测"
  5. **Hook 输出被忽略**：即使 Stop Hook 输出了检查清单，Agent 在"任务完成"心态下会忽略提醒
- **解决方案**：
  1. **增加 PostToolUse Hook 做工具失败检测**：工具返回包含 error/401/403/timeout/Unauthorized/连接失败 时，输出强提醒"⚠️ 工具失败，请立即记录踩坑到 docs/lessons-learned.md"
  2. **self-improvement.md 增加硬性规则**：在任何工具调用返回错误后的下一步操作，**必须**是记录踩坑（不是继续推进任务），违反此规则属于最严重的执行偏差
  3. **steering/interaction-rules.md 增加流程约束**：工具失败 → 记录踩坑 → 通知用户 → 再继续，这个顺序不可打乱
  4. **Agent 内化**：在每次工具调用前，Agent 应该预判"这个调用可能失败"，失败后立即触发记录流程
- **关联文件**：`.trae/steering/self-improvement.md`、`.trae/hooks/on-stop-check-lessons.sh`、`.trae/hooks.json`、`.trae/steering/interaction-rules.md`
- **知识库更新**：无
- **Agent更新**：self-improvement.md 强化"工具失败必须先记录再继续"为硬性规则；interaction-rules.md 增加流程顺序约束
- **脚本更新**：新增 PostToolUse hook 脚本做工具失败检测（待实现）

---

## 2026-08-10 工具能力：禅道 SPA + iframe 架构，curl 读数据全失败 + 未及时记录踩坑

- **问题**：
  1. 禅道旗舰版 6.4 用 Zui3 Zin 框架，纯 SPA 渲染，curl 拿不到任何渲染后数据
  2. `?zin=1` 参数返回 HTML 不是 JSON（误以为是 API 端点）
  3. 状态过滤参数 `type=finished/closed/all` 不生效，URL 都返回默认的"指派给我"列表
  4. URL 模式 `/my-work-task-finished.html` 等不存在，返回空页面
  5. 禅道 REST API `/api.php/v1/tasks` 用 session cookie 返回 "Access not allowed"，用 Basic Auth 返回 "Unauthorized"，需要 PAT
  6. 已关闭执行列表的分页 URL 参数格式 `/execution-all-closed-rawID_desc-0-0-20-{page}.html` 不生效
  7. **数据在 iframe 里**（`app-my`、`app-execution`），不在主页面 DOM，必须用 Playwright 遍历 `page.frames` 找到对应 iframe 才能提取
  8. 用户两次沟通都未主动记录踩坑，被用户批评后才补记，说明自改进机制在执行过程中未生效
- **根因**：
  1. 禅道 Zin 框架是纯前端渲染，所有数据通过 JS 动态加载到 iframe 内的 dtable 组件，curl 只能拿到空壳 HTML
  2. 禅道 URL 的 `?zin=1` 是 Zin 框架的内部参数，不是 REST API 开关
  3. 状态过滤不是通过 URL 参数，而是通过 dtable 组件内的 AJAX 交互，需要模拟点击 tab
  4. REST API 需要独立的 PAT 认证，不能用 Web session 或 Basic Auth
  5. iframe 的 URL 是 `about:blank`，内容由父页面 JS 注入，不能直接通过 URL 访问
  6. **Agent 没有在执行过程中即时记录踩坑**，违背了 self-improvement.md 的"工具失败必须立即记录"规则
- **解决方案**：
  1. **读操作必须用 Playwright**：禅道 SPA 的数据在 iframe 里，必须 `page.frames` 遍历找 `app-*` iframe，在 iframe 内提取 `inner_text('body')` 或 `eval_on_selector_all`
  2. **写操作用 curl**：POST 表单不需要读响应，session cookie 复用 Playwright 登录的 zentaosid
  3. **"我的任务"vs"我的贡献"**：`/my-work-task.html` = 指派给我的未完成任务；`/my-contribute-task.html` = 我贡献过的所有任务（含已完成）
  4. **分页**：dtable 用 AJAX 滚动加载，没有传统分页 URL，需要在 Playwright 里模拟滚动或点击
  5. **REST API**：如果需要批量查询，生成禅道 PAT（头像→设置→Personal Access Tokens），用 `Header: Token {PAT}` 调用 `/api.php/v1/`
  6. **踩坑必须即时记录**：遇到工具失败/方案不奏效时，当场写入 lessons-learned.md，不等用户提醒
- **关联文件**：`.trae/skills/zentao-operation/SKILL.md`、`.trae/scripts/zentao_login.py`、`docs/lessons-learned.md`
- **知识库更新**：无
- **Agent更新**：zentao-operation skill 补充 iframe 架构说明 + 读操作用 Playwright + 写操作用 curl + "我的任务"vs"我的贡献"区别
- **脚本更新**：zentao_login.py 增加 check/screenshot 子命令

---

## 2026-08-08 工具能力：Confluence 认证用错账号密码，根因是凭据来源不统一

- **问题**：Confluence 页面读取失败，尝试了 PAT、JSESSIONID、Basic Auth 都失败，浪费多轮对话
- **根因**：凭据存在两个地方，Agent 从记忆里取了错误的旧账号（liuran:Aa123456），而正确凭据在 `.trae/settings/credentials.json`（zhangguichang:Qwe@1997）
- **教训**：**凭据必须从文件读取，不能从记忆中取**。记忆可能过时，文件是 single source of truth
- **修复**：
  1. tool-usage skill 已更新：Confluence 凭据从 credentials.json 读取，不从 .env 读
  2. 加粗标注"不要从记忆中取凭据，必须每次从文件读取"
  3. 401 处理流程第一步改为"先检查 credentials.json 是否存在且凭据正确"
- **关联文件**：`.trae/skills/tool-usage/SKILL.md`、`.trae/settings/credentials.json`

---

## 2026-08-06 工具能力：Confluence 401 凭据失效未主动记录踩坑 + Hook 检查逻辑有缺陷

- **问题**：
  1. 读取 Confluence 页面 120670848 时返回 401 Unauthorized
  2. 遇到 401 后直接跳过读文档，转而给方法论建议，**没有主动记录踩坑、没有反思、没有更新 skill**
  3. 用户批评后才补记，说明自改进机制在"执行过程中"没有生效，只靠 Stop Hook 事后提醒
- **根因**：
  1. Confluence 启用了 CAPTCHA 验证码，导致：Basic Auth 被禁用（401）+ REST API 登录被拒绝（permissionViolation）+ 表单登录被拦截（需要验证码）
  2. 遇到工具失败时，Agent 没有遵循"立即记录踩坑"的规则，而是继续推进任务
  3. `on-stop-check-lessons.sh` 有逻辑缺陷：只检查"今天是否有 `## 日期` 标题"，有就跳过提醒。但一天内可能多次踩坑，只检查标题会导致后续踩坑被漏掉
  4. 凭据硬编码在 tool-usage skill 中，没有过期检测和更新机制
- **解决方案**：
  1. **工具失败必须立即记录**：遇到 401/超时/连接失败等工具错误时，当场写入 lessons-learned.md，不等 Stop Hook
  2. **Confluence 认证方案**：CAPTCHA 启用后无法通过脚本自动登录，替代方案：①用户在浏览器登录后复制 JSESSIONID cookie ②使用 Personal Access Token (PAT)  ③用户手动贴内容
  3. **Hook 检查逻辑修复**：不能只检查"有无今日标题"，改为每次 stop 都输出检查清单 + 今日条数
  4. **凭据管理改进**：凭据不放 skill 明文，改放 `.env` 文件（.gitignore 过滤），skill 只引用变量名
- **关联文件**：`docs/lessons-learned.md`、`.trae/skills/tool-usage/SKILL.md`、`.trae/hooks/on-stop-check-lessons.sh`、`.trae/steering/self-improvement.md`
- **知识库更新**：无
- **Agent更新**：tool-usage skill 加 Confluence 401 处理流程 + 凭据管理规范 + CAPTCHA 应对方案
- **脚本更新**：on-stop-check-lessons.sh 修复检查逻辑

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
