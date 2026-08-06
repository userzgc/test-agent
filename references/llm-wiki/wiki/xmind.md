# XMind 文件格式

## 文件结构
XMind 文件本质是 zip 包，包含3个 JSON 文件：

```
file.xmind (zip)
├── content.json     # 主体内容
├── metadata.json    # 元数据
└── manifest.json    # 清单
```

## content.json 结构
```json
[
  {
    "id": "uuid",
    "class": "sheet",
    "title": "测试用例",
    "rootTopic": {
      "id": "uuid",
      "class": "topic",
      "title": "根节点标题",
      "children": {
        "attached": [
          {
            "id": "uuid",
            "class": "topic",
            "title": "子节点标题",
            "children": {
              "attached": [...]
            }
          }
        ]
      }
    }
  }
]
```

## 脚本工具

生成和解析逻辑已抽取为独立脚本：

### 生成 XMind
```bash
python3 .trae/scripts/gen_xmind.py <input.json> <output.xmind>
```
input.json 用简单的 `{title, children: [...]}` 结构，脚本内部转换为 XMind 的 topic 格式。

### 解析 XMind/JSON
```bash
python3 .trae/scripts/parse_xmind.py <input.xmind|input.json> [--output <out.txt>]
```
支持 .xmind 文件和 XMind 导出的 .json 文件（含单行 JSON）。

## 注意事项
- 每个节点必须有 `id` 和 `class` 字段
- 叶子节点的 `children` 为 `null`
- `ensure_ascii=False` 确保中文正常
- **XMind 导出的 JSON 是单行格式**，超过 20KB 时 Read 工具无法直接读取完整内容，必须用 `parse_xmind.py` 脚本解析
