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

### 凭据管理

凭据存放在 `config/credentials.json`（已被 .gitignore 过滤），**不要从记忆中取凭据，必须每次从文件读取**：

```json
// config/credentials.json 格式（不入 git）
{
  "confluence": {
    "baseUrl": "http://confluence.mxbc-code.com:8090",
    "username": "your_username",
    "password": "your_password",
    "apiPath": "/rest/api/content"
  }
}
```

curl 中直接引用文件中的凭据：
```bash
# 先读 credentials.json 取凭据
USER=$(python3 -c "import json;print(json.load(open('config/credentials.json'))['confluence']['username'])")
PASS=$(python3 -c "import json;print(json.load(open('config/credentials.json'))['confluence']['password'])")
curl -s -u "${USER}:${PASS}" ...
```

### 获取页面内容

```bash
USER=$(python3 -c "import json;print(json.load(open('config/credentials.json'))['confluence']['username'])")
PASS=$(python3 -c "import json;print(json.load(open('config/credentials.json'))['confluence']['password'])")
curl -s -u "${USER}:${PASS}" "http://confluence.mxbc-code.com:8090/rest/api/content/{pageId}?expand=body.storage" -o /tmp/confluence_page.json

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

### 401 凭据失效处理流程

遇到 401 Unauthorized 时**必须按以下流程处理，不能跳过**：

1. **立即检测**：检查返回内容是否包含 `401` 或 `Unauthorized`
2. **记录踩坑**：当场用 `UpdateMemory` 落长期记忆（`common_pitfalls_experience`），不要只写 md 文件
3. **诊断根因**：
   - Basic Auth 401 → 尝试表单登录 `/dologin.action`
   - 表单登录返回 CAPTCHA → **Confluence 启用了验证码，脚本无法自动登录**
   - 表单登录成功但 REST API 404 → **Cookie 不被 REST API 接受，需用 PAT**
4. **通知用户**：用 AskUserQuestion 推送选项：
   - "用户在浏览器登录后复制 JSESSIONID cookie"（见下方说明）
   - "用户在 Confluence 设置中生成 Personal Access Token (PAT)"
   - "用户手动贴需求内容，跳过 Confluence 读取"
5. **更新凭据**：用户给新凭据后，更新 `.env` 文件
6. **重试**：用新凭据重新读取

### CAPTCHA 应对方案

当 Confluence 启用 CAPTCHA 后，所有非交互式登录方式都被拒绝：
- ❌ Basic Auth → 401
- ❌ REST API 登录 (/rest/auth/1/session) → permissionViolation
- ❌ 表单登录 (/dologin.action) → 需要验证码

**替代方案**：

| 方案 | 操作 | 优劣 |
|------|------|------|
| ① 复制 JSESSIONID | 用户在浏览器登录 Confluence → F12 → Application → Cookies → 复制 JSESSIONID 值 → 传给 Agent | 最简单，但 cookie 会过期 |
| ② Personal Access Token | 用户在 Confluence → 头像 → Settings → Personal Access Tokens → Create Token → 传给 Agent | 最稳定，PAT 长期有效 |
| ③ 手动贴内容 | 用户在浏览器打开页面 → 全选复制 → 贴到对话 | 最快但无格式 |

**使用 JSESSIONID 的方式**：
```bash
curl -s -b "JSESSIONID=<用户复制的值>" "http://confluence.mxbc-code.com:8090/rest/api/content/{pageId}?expand=body.storage"
```

**使用 PAT 的方式**：
```bash
curl -s -H "Authorization: Bearer <用户生成的token>" "http://confluence.mxbc-code.com:8090/rest/api/content/{pageId}?expand=body.storage"
```

**禁止的行为**：
- ❌ 遇到 401 直接跳过，转而给方法论建议
- ❌ 凭据硬编码在脚本/skill 明文中
- ❌ 不记录踩坑就继续推进任务

## 飞书

```bash
# 使用 lark-cli 操作飞书表格
lark-cli sheet workbook-export --token {token} --sheet {sheet_id} --output /tmp/sheet.csv
lark-cli sheet table-update --token {token} --sheet {sheet_id} --data /tmp/data.json
```

## YAPI

```bash
# 解析 YAPI 接口分类信息
python3 scripts/parse_yapi.py <input.md> [--output <out.json>]
```

## 蓝湖 / 墨刀 / 设计稿

- 设计稿类输入统一由 `design-extractor` agent 收口处理
- 详见 `design-extraction` skill（`#design-extraction` 激活）

## 脚本工具（scripts/）

所有工具已抽取为独立脚本，直接命令行调用：

| 脚本 | 用途 | 用法 |
|------|------|------|
| `gen_xmind.py` | 生成 XMind 文件 | `python3 scripts/gen_xmind.py <input.json> <output.xmind>` |
| `parse_xmind.py` | 解析 XMind/JSON 为树形文本 | `python3 scripts/parse_xmind.py <input> [--output <out.txt>]` |
| `parse_yapi.py` | 解析 YAPI 导出的 Markdown | `python3 scripts/parse_yapi.py <input.md> [--output <out.json>]` |
| `parse_feishu.py` | 解析飞书导出的 CSV | `python3 scripts/parse_feishu.py <input.csv> [--group-by <字段>]` |
| `extract_confluence_images.py` | 下载 Confluence 页面中的图片 | `python3 scripts/extract_confluence_images.py <pageId> [--output <dir>]` |
| `ocr_images.py` | 对本地图片做 OCR 文字提取 | `python3 scripts/ocr_images.py <image_dir> [--lang chi_sim+eng]` |

## 平台能力参考

> ⚠️ **当前运行平台是 Qoder，不是 Trae。**
> `references/llm-wiki/trae-docs/` 是 Trae 时代的文档，**扩展机制部分对本项目已不适用**。
> 查 rules / skills / subagent / hooks / commands / MCP 的正确格式，一律看
> `.qoder/rules/qoder-platform.md`；需要原文时看 `references/qoder-docs/`。

配置位置以 Qoder 为准：

| 能力 | Qoder 配置位置 |
|------|---------------|
| 项目说明 | `AGENTS.md`（每次会话自动注入） |
| 规则 Rules | `.qoder/rules/*.md`（frontmatter 用 `trigger:`） |
| 技能 Skill | `.qoder/skills/<name>/SKILL.md` |
| Subagent | `.qoder/agents/<name>.md`（**单文件**） |
| 自定义命令 | `.qoder/commands/<name>.md` |
| MCP Server | `.mcp.json` |

### 踩坑记录落点

工具调用失败的处置流程见 `.qoder/rules/failure-protocol.md`。
可复用的教训落 **Qoder 长期记忆**（`UpdateMemory`），不是只写 md。

> 历史说明：`.trae/hooks/` 下的 Stop / SessionStart 脚本在 Qoder 下**不会被触发**，
> 本项目当前没有配置任何 hook。因此「自动提醒记录踩坑」这件事目前**没有机制兜底**，
> 完全依赖当场自觉执行 `failure-protocol.md`。

### XMind 文件结构说明

XMind 文件本质是 zip 包，包含3个 JSON 文件：content.json + metadata.json + manifest.json。
生成逻辑见 `scripts/gen_xmind.py`，解析逻辑见 `scripts/parse_xmind.py`。
