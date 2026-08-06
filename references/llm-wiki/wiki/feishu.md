# 飞书 CLI 使用

## 基本信息
- 使用 `lark-cli` 工具操作飞书云表格
- 配置目录：`~/.lark-cli/`

## 常用命令

### 导出表格
```bash
lark-cli sheet workbook-export \
  --token {wiki_token} \
  --sheet {sheet_id} \
  --output /tmp/sheet.csv
```

### 更新表格
```bash
lark-cli sheet table-update \
  --token {wiki_token} \
  --sheet {sheet_id} \
  --data /tmp/data.json
```

## 已知文档
| 文档 | URL | 说明 |
|------|-----|------|
| SSOS接口YAPI文档 | https://mxbc.feishu.cn/wiki/IPz7wMMqKiMhktkOA3lcmOL4nFX | 接口场景分类 |
| 城市徽章技术方案 | https://mxbc.feishu.cn/wiki/IRdZwmDqsirhA8kaJ2CclWjInGe | 华南城市徽章技术设计 |

## 注意事项
- table-get 命令有返回行数限制，大量数据用 workbook-export 导出CSV
- 写入前先导出确认现有数据格式
- 表格操作非原子性，写入失败需检查中间状态
