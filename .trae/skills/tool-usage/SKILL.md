---
name: "tool-usage"
description: "Use when operating external tools (Confluence/飞书/YAPI/蓝湖) and project scripts. Triggers on 工具调用、Confluence、飞书、YAPI、脚本、gen_xmind、parse_xmind etc."
---

# 工具使用

## 何时使用

- 需要对接外部工具（Confluence、飞书、YAPI、蓝湖）
- 需要调用项目脚本（gen_xmind/parse_xmind/parse_yapi/parse_feishu/extract_confluence_images/ocr_images）
- 触发词：工具调用、Confluence、飞书、YAPI、脚本、gen_xmind、parse_xmind

## Confluence

```bash
# 获取页面内容
curl -s -u "username:password" "http://confluence.mxbc-code.com:8090/rest/api/content/{pageId}?expand=body.storage" -o /tmp/confluence_page.json

# 解析HTML为纯文本
python3 -c "
import json, re
with open('/tmp/confluence_page.json') as f:
    d = json.load(f)
body = d.get('body',{}).get('storage',{}).get('value','')
text = re.sub(r'<[^>]+>', ' ', body)
print(text[:30000])
"
```

## 飞书

```bash
# 使用 lark-cli 操作飞书表格
lark-cli sheet workbook-export --token {token} --sheet {sheet_id} --output /tmp/sheet.csv
lark-cli sheet table-update --token {token} --sheet {sheet_id} --data /tmp/data.json
```

## YAPI

```bash
# 解析 YAPI 接口分类信息
python3 .trae/scripts/parse_yapi.py <input.md> [--output <out.json>]
```

## 蓝湖 / 墨刀 / 设计稿

- 设计稿类输入统一由 `design-extractor` agent 收口处理
- 详见 `design-extraction` skill（`#design-extraction` 激活）

## 脚本工具（.trae/scripts/）

所有工具已抽取为独立脚本，直接命令行调用：

| 脚本 | 用途 | 用法 |
|------|------|------|
| `gen_xmind.py` | 生成 XMind 文件 | `python3 .trae/scripts/gen_xmind.py <input.json> <output.xmind>` |
| `parse_xmind.py` | 解析 XMind/JSON 为树形文本 | `python3 .trae/scripts/parse_xmind.py <input> [--output <out.txt>]` |
| `parse_yapi.py` | 解析 YAPI 导出的 Markdown | `python3 .trae/scripts/parse_yapi.py <input.md> [--output <out.json>]` |
| `parse_feishu.py` | 解析飞书导出的 CSV | `python3 .trae/scripts/parse_feishu.py <input.csv> [--group-by <字段>]` |
| `extract_confluence_images.py` | 下载 Confluence 页面中的图片 | `python3 .trae/scripts/extract_confluence_images.py <pageId> [--output <dir>]` |
| `ocr_images.py` | 对本地图片做 OCR 文字提取 | `python3 .trae/scripts/ocr_images.py <image_dir> [--lang chi_sim+eng]` |

## Trae 能力参考

完整 Trae 官方文档知识库：`references/llm-wiki/trae-docs/README.md`

### 常用机制速查

| 能力 | 配置位置 | 文档 |
|------|---------|------|
| 自定义 Agent | `.trae/agents/<name>/agent.md` | `trae-docs/02-agents.md` |
| 技能 Skill | `.trae/skills/<name>/SKILL.md` | `trae-docs/03-skills.md` |
| 规则 Rules | `.trae/rules/*.md` | `trae-docs/04-rules.md` |
| Hook 自动化 | `.trae/hooks.json` + `.trae/hooks/*.sh` | `trae-docs/05-hooks.md` |
| MCP Server | `.trae/mcp.json` | `trae-docs/06-mcp.md` |
| 上下文引用 | `@agent` / `#file` / `#docs` | `trae-docs/07-context.md` |

### Hook 机制（自改进核心）

- Stop 事件触发：自动检查踩坑记录 → `.trae/hooks/on-stop-check-lessons.sh`
- SessionStart 事件触发：自动加载项目上下文 → `.trae/hooks/session-start.sh`
- 配置文件：`.trae/hooks.json`
- 规则文档：`.trae/steering/self-improvement.md`

### XMind 文件结构说明

XMind 文件本质是 zip 包，包含3个 JSON 文件：content.json + metadata.json + manifest.json。
生成逻辑见 `.trae/scripts/gen_xmind.py`，解析逻辑见 `.trae/scripts/parse_xmind.py`。
