# Confluence 访问方式

## 基本信息
- 地址：`http://confluence.mxbc-code.com:8090`
- 认证方式：HTTP Basic Auth
- 账号：见 `settings/credentials.json`

## 获取页面内容
```bash
curl -s -u "username:password" \
  "http://confluence.mxbc-code.com:8090/rest/api/content/{pageId}?expand=body.storage" \
  -o /tmp/confluence_page.json
```

## 解析 HTML
Confluence 返回的是 HTML 格式，需用正则清理：
```python
import json, re
with open('/tmp/confluence_page.json') as f:
    d = json.load(f)
body = d.get('body',{}).get('storage',{}).get('value','')
# 清理HTML标签
text = re.sub(r'<[^>]+>', ' ', body)
# 清理HTML实体
text = text.replace('&amp;', '&').replace('&ldquo;', '"').replace('&rdquo;', '"')
text = re.sub(r'\s+', ' ', text)
```

## 已知页面ID
| 页面 | pageId | 说明 |
|------|--------|------|
| 买A赠B一期需求 | 120654652 | 一期PRD |
| 买A赠B二期需求 | 120671596 | 二期PRD |
| 买A赠B技术设计 | 120655361 | 技术方案 |
| 城市徽章需求 | 120654950 | 雪王游南方PRD |
