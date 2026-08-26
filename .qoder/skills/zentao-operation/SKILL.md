---
name: "zentao-operation"
description: "Use when operating Zentao (禅道) for task management, effort logging, and project queries. Triggers on 禅道、拆任务、补工时、补录工时、zentao etc."
---

# 禅道操作

## 何时使用

- 需要在禅道拆任务、补录工时、查看任务列表
- 触发词：禅道、拆任务、补工时、补录工时、zentao

## 架构：Playwright + curl 混合

| 层 | 工具 | 职责 |
|----|------|------|
| 登录层 | Playwright（headless） | 登录禅道，导出 zentaosid cookie |
| 读操作 | Playwright | SPA 渲染后提取数据（禅道用 Zui3 dtable，curl 拿不到渲染数据） |
| 写操作 | curl（带 session） | POST 表单：拆任务、补工时（不需要读响应） |
| 确认层 | Playwright screenshot | 操作后截图确认结果 |

## 凭据管理

凭据存放在 `config/credentials.json`（已被 .gitignore 过滤），**不要从记忆中取凭据，必须从文件读取**：

```json
{
  "zentao": {
    "baseUrl": "https://mxbc.chandao.net",
    "username": "zhangguichang",
    "password": "Qwe@1997"
  }
}
```

## 禅道模块结构（10 大模块）

禅道旗舰版 6.4，URL 模式：`/module-method-params.html`

| 模块 | URL | 说明 | QA 常用 |
|------|-----|------|---------|
| **地盘 (my)** | `/my.html` | 个人首页 | ✅ |
| 项目集 (program) | `/program-browse.html` | 项目集管理 | |
| 产品 (product) | `/product-all.html` | 产品管理 | |
| **项目 (project)** | `/project-browse.html` | 项目列表 | ✅ |
| **执行 (execution)** | `/execution-task.html` | 迭代/执行任务 | ✅ |
| **测试 (qa)** | `/qa.html` | 测试用例/Bug | ✅ |
| BI (screen) | `/screen-browse.html` | 数据看板 | |
| 文档 (doc) | `/doc-lastViewedSpace.html` | 文档管理 | |
| 组织 (my-team) | `/my-team.html` | 团队管理 | |
| 后台 (admin) | `/admin.html` | 系统管理 | |

## 地盘子页面（QA 最常用）

| 子页面 | URL | 说明 |
|--------|-----|------|
| 我的任务 | `/my-work-task.html` | 当前分配给我的任务 |
| 我的研发需求 | `/my-work-story.html` | 分配给我的需求 |
| 我的 Bug | `/my-work-bug.html` | 分配给我的 Bug |
| 我的用例 | `/my-work-testcase.html` | 分配给我的用例 |
| 我的日志 | `/my-effort.html` | 我的工时记录 |
| 工时日历 | `/effort-calendar.html` | 工时日历视图 |

## 登录流程

```bash
# 1. Playwright 登录，导出 session cookie
python3 scripts/zentao_login.py login
# 输出 zentaosid，缓存到 /tmp/zentao_session.txt

# 2. 检查 session 是否有效
python3 scripts/zentao_login.py check

# 3. 截图确认页面
python3 scripts/zentao_login.py screenshot "https://mxbc.chandao.net/my/" --output /tmp/zentao_my.png
```

## Session 复用（curl 写操作）

```bash
ZENTAOSID=$(cat /tmp/zentao_session.txt)
BASE="https://mxbc.chandao.net"
```

## 读操作（必须用 Playwright）

禅道用 Zui3 Zin 框架，纯 SPA 渲染，curl 拿不到数据。必须用 Playwright 等待 JS 渲染后提取。

```python
# 示例：读取我的任务列表
from playwright.sync_api import sync_playwright

ZENTAOSID = open('/tmp/zentao_session.txt').read().strip()
BASE = "https://mxbc.chandao.net"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    context.add_cookies([{
        'name': 'zentaosid', 'value': ZENTAOSID,
        'domain': 'mxbc.chandao.net', 'path': '/',
        'secure': True, 'httpOnly': True,
    }])
    page = context.new_page()
    page.goto(f'{BASE}/my-work-task.html', wait_until='networkidle')
    page.wait_for_timeout(3000)  # 等 dtable 渲染

    # 提取表格行
    rows = page.eval_on_selector_all('tr, .dtable-row', """() => {
        return [...document.querySelectorAll('tr, .dtable-row')].map(tr => tr.textContent.trim()).filter(t => t.length > 0);
    }""")
    for row in rows:
        print(row[:200])

    browser.close()
```

## 写操作（curl POST）

### 拆任务

需要知道 executionID（执行 ID），从执行页面获取。

```bash
ZENTAOSID=$(cat /tmp/zentao_session.txt)
BASE="https://mxbc.chandao.net"

# POST 创建任务
curl -s -b "zentaosid=${ZENTAOSID}" \
  -X POST \
  "${BASE}/task-create-${executionID}.html" \
  -d "name=任务名&est=预估工时&assignedTo[]=zhangguichang&type=devel&desc=任务描述" \
  -o /tmp/zentao_create_resp.html
```

任务类型 type 取值：`devel`(开发)、`test`(测试)、`design`(设计)、`study`(研究)、`discuss`(讨论)、`misc`(其他)、`affair`(事务)

### 补录工时

```bash
ZENTAOSID=$(cat /tmp/zentao_session.txt)
BASE="https://mxbc.chandao.net"

# 方式1：通过任务补录
curl -s -b "zentaosid=${ZENTAOSID}" \
  -X POST \
  "${BASE}/task-effort-${taskID}.html" \
  -d "date=2026-08-06&consumed=4&left=0&work=工作内容描述" \
  -o /tmp/zentao_effort_resp.html

# 方式2：通过日志页面补录
curl -s -b "zentaosid=${ZENTAOSID}" \
  -X POST \
  "${BASE}/effort-create-objectID=${taskID}.html" \
  -d "date=2026-08-06&consumed=4&left=0&work=工作内容描述" \
  -o /tmp/zentao_effort_resp.html
```

## 操作确认

每次写操作后，用 Playwright 截图确认：

```bash
python3 scripts/zentao_login.py screenshot "https://mxbc.chandao.net/task-view-${taskID}.html" --output /tmp/zentao_confirm.png
```

## 工作流组合

### 工作流1：拆任务（完整流程）

```
1. [Playwright] 登录 → 导出 session
2. [Playwright] 访问 /execution-task-{executionID}.html → 截图确认当前执行
3. [curl] POST /task-create-{executionID}.html → 创建任务
4. [Playwright] 截图 /task-view-{newTaskID}.html → 确认任务创建成功
```

### 工作流2：补录工时（完整流程）

```
1. [Playwright] 登录 → 导出 session
2. [Playwright] 访问 /my-work-task.html → 获取任务ID列表
3. [curl] POST /task-effort-{taskID}.html → 补录工时
4. [Playwright] 截图 /my-effort.html → 确认工时记录
```

### 工作流3：多模块查询（需求→任务→工时）

```
1. [Playwright] 登录 → 导出 session
2. [Playwright] 访问 /my-work-story.html → 获取需求列表
3. [Playwright] 访问 /execution-task-{executionID}.html → 获取任务列表
4. [Playwright] 访问 /my-effort.html → 获取工时记录
5. [Playwright] 截图确认 → 汇总输出
```

## Session 过期处理

如果 curl 返回登录页（302 或 HTML 包含 "login"）：

1. 重新登录：`python3 scripts/zentao_login.py login`
2. 重试操作

## 限制

- **读操作必须用 Playwright**：禅道 Zin 框架是纯 SPA，curl 拿不到渲染后的数据
- **写操作用 curl**：POST 表单不需要读响应，curl 更快
- 禅道表单可能有 CSRF token，需要先 GET 页面提取 token 再 POST
- 批量操作建议每次只操作 1 条，用截图确认成功后再继续
- Playwright headless 模式不支持 CAPTCHA，如果禅道加了验证码需要用 `headless=False`
