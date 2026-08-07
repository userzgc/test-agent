# test-agent

基于 Trae IDE 的测试需求对焦和用例管理 Agent 项目。

## 快速开始

### 1. 跑一个完整 QA 工作流

在 Trae 对话框直接说：

```
走工作流，分析这个需求：[贴需求文档链接或内容]
```

Agent 会按 4 步事务式工作流推进，每步等你确认才进下一步：

```
Step 1: 需求分析    → docs/requirements/<需求名>_需求分析.md
   ↓ [确认通过]
Step 2: 测试场景对齐  → docs/requirements/<需求名>_测试场景.md
   ↓ [确认通过]
Step 3: 用例编写     → docs/test-cases/<需求名>_测试用例_v<n>.xmind
   ↓ [确认通过]
Step 4: 用例评审     → docs/test-cases/<需求名>_评审报告.md
```

### 2. 单步使用

| 你想做什么 | 对话框输入 |
|-----------|-----------|
| 分析需求 | `分析这个需求：[内容]` |
| 对齐测试场景 | `帮我对齐测试场景` |
| 生成 XMind 用例 | `生成 XMind 用例` |
| 评审用例 | `评审这份用例：[文件路径]` |
| 提取设计稿测试点 | `分析这个设计稿：[蓝湖/墨刀链接]` |

## 能力一览

### Agent（6 个）

| Agent | 职责 | 对话框引用 |
|-------|------|-----------|
| requirements | 需求分析 | `@requirements` |
| design-extractor | 设计稿/原型稿提取 | `@design-extractor` |
| case-writing | 用例编写 | `@case-writing` |
| case-review | 用例评审 | `@case-review` |
| execution | 测试执行 | `@execution` |
| utils | 工具调用（Confluence/飞书/YAPI） | `@utils` |

### Skill（7 个）

| Skill | 触发词 |
|-------|--------|
| qa-workflow | 测试工作流、用例全流程、qa workflow |
| requirements-analysis | 需求分析、requirements analysis |
| test-case-writing | 编写测试用例、test case writing |
| test-case-reviewer | 测试用例评审、test case review |
| functional-testing | 功能测试、测试方案设计 |
| design-extraction | 设计稿、原型稿、截图识别、UI 提取 |
| tool-usage | 工具调用、Confluence、飞书、YAPI、脚本 |

### 脚本工具（8 个）

所有脚本独立可执行，Agent 按需调用：

| 脚本 | 用途 | 用法 |
|------|------|------|
| gen_xmind.py | 生成 XMind 文件 | `python3 .trae/scripts/gen_xmind.py <input.json> <output.xmind>` |
| parse_xmind.py | 解析 XMind 为树形文本 | `python3 .trae/scripts/parse_xmind.py <input>` |
| gen_buyagiftb_xmind.py | 买A赠B场景树生成 | `python3 .trae/scripts/gen_buyagiftb_xmind.py` |
| parse_yapi.py | 解析 YAPI 导出的 Markdown | `python3 .trae/scripts/parse_yapi.py <input.md>` |
| parse_feishu.py | 解析飞书导出的 CSV | `python3 .trae/scripts/parse_feishu.py <input.csv>` |
| extract_confluence_images.py | 下载 Confluence 页面图片 | `python3 .trae/scripts/extract_confluence_images.py <pageId>` |
| ocr_images.py | 图片 OCR 文字提取 | `python3 .trae/scripts/ocr_images.py <image_dir>` |
| md_to_xmind_tree.py | Markdown 转 XMind 树 JSON | `python3 .trae/scripts/md_to_xmind_tree.py <input.md>` |

## 项目架构

```
test-agent/
├── .trae/
│   ├── agents/              # Agent 指令（6 个，每个只含角色/IO/工作流/停止条件）
│   │   ├── requirements/     # 需求分析
│   │   ├── design-extractor/ # 设计稿提取
│   │   ├── case-writing/     # 用例编写
│   │   ├── case-review/      # 用例评审
│   │   ├── execution/        # 测试执行
│   │   └── utils/            # 工具调用
│   ├── skills/              # Skill 可复用操作规范（7 个）
│   │   ├── qa-workflow/      # QA 事务式工作流（4 步串行）
│   │   ├── requirements-analysis/
│   │   ├── test-case-writing/
│   │   ├── test-case-reviewer/
│   │   ├── functional-testing/
│   │   ├── design-extraction/
│   │   └── tool-usage/
│   ├── steering/           # 全局行为约束（6 条）
│   │   ├── multi-agent-orchestration.md  # Agent 路由 + sub-agent 落地 + MCP 预留
│   │   ├── interaction-rules.md         # 交互规范（多选项推送等）
│   │   ├── self-improvement.md           # 自改进机制（踩坑记录 → Wiki）
│   │   ├── coding-safety.md             # 编码安全
│   │   ├── prompt-writing-guide.md      # Prompt 写作规范
│   │   └── graphify.md                  # 知识图谱运行规则
│   ├── hooks/              # 事件驱动自动化（3 个）
│   │   ├── on-stop-check-lessons.sh     # Agent 结束 → 检查踩坑写入 Wiki
│   │   ├── post-tool-feishu-auth.sh    # 飞书 token 过期 → 自动重授权
│   │   └── session-start.sh            # 会话开始 → 加载项目上下文
│   ├── hooks.json          # Hook 配置
│   ├── scripts/            # 独立工具脚本（8 个）
│   ├── mcp-servers/         # MCP Server 预留（骨架未实装）
│   │   └── xmind-tools/     # XMind 生成/解析 MCP Server
│   └── settings/           # 凭据配置
├── docs/                   # 产出物
│   ├── requirements/        # 需求分析文档
│   ├── test-cases/         # 测试用例（XMind/JSON）
│   ├── historical-cases/   # 历史用例归档
│   ├── api-reference/      # 接口参考
│   ├── lessons-learned.md   # 踩坑记录
│   └── mcp-config-guide.md # MCP 配置指南
├── references/llm-wiki/    # LLM 知识库
│   ├── _quarto.yml          # Quarto 渲染配置
│   ├── SCHEMA.md            # 知识结构定义
│   └── wiki/                # 知识页面
│       ├── index.md         # 知识目录
│       ├── activities/       # 活动知识（买A赠B、城市徽章）
│       ├── conventions/     # 测试规范
│       ├── confluence.md     # Confluence 访问
│       ├── feishu.md         # 飞书访问
│       └── xmind.md          # XMind 格式说明
├── graphify-out/           # 知识图谱产出（占位）
└── .gitignore
```

### 组件协作关系

```
用户在 Trae 对话框用自然语言描述需求
  │
  ▼
Steering（路由规则）→ 识别意图，加载对应 Agent + Skill
  │
  ▼
Agent 执行任务 → 调用脚本工具 → 产出物落 docs/
  │
  ▼
Hook 自动触发 → Agent 结束时检查踩坑，写入 Wiki
```

## 核心机制

### QA 事务式工作流

4 步串行，每步用户确认后才进下一步。用 `走工作流` 触发。

### 多动作推送选项

任务完成有 ≥2 个后续动作时，Agent 用 `AskUserQuestion` 推送选项，用户点选而不是手打。

### 自改进机制

Agent 踩坑后自动记录到 `docs/lessons-learned.md`，同步更新 Skill 和 Wiki，下次自动规避。

### XMind 场景树规范

用例直接输出 XMind，不写 MD。格式参考华南徽章 v2 风格：大类 → 小场景 → 数据/预期，不带字段头。

## 已有资产

| 产出 | 位置 |
|------|------|
| 买A赠B二期需求分析 | `docs/requirements/买A赠B二期_需求分析.md` |
| 买A赠B二期测试用例 | `docs/test-cases/买A赠B二期_测试用例.xmind` |
| 买A赠B二期冒烟用例 | `docs/test-cases/买A赠B二期_冒烟用例.xmind` |
| 买A赠B二期评审报告 | `docs/test-cases/买A赠B二期_用例评审报告.md` |
| 城市徽章 v2 用例 | `docs/test-cases/雪王游南方_点亮城市徽章_测试用例_v2.xmind` |
| 买A赠B一期用例（JSON） | `docs/test-cases/买 a 赠 b 一期用例.json` |
| 踩坑记录 | `docs/lessons-learned.md` |
| MCP 配置指南 | `docs/mcp-config-guide.md` |
