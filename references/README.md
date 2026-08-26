# references/ —— 外部参考资料（只读）

本目录是**外部资料镜像**，不是本项目产出，不会被自动加载进 agent 上下文。

| 子目录 | 内容 | 用途 |
|---|---|---|
| `qoder-docs/` | Qoder 官方文档镜像（CLI 20 篇 + IDE 20 篇） | 写/排查 `.qoder/` 扩展资产时逐字查证（蒸馏版在 `.qoder/rules/qoder-platform.md`） |
| `llm-wiki/` | Trae 时代的 Quarto Wiki 源码与业务知识 | 仅供人翻阅历史；业务口径以 `docs/` 下现行文档为准 |
| `yapi-oss-api.md` | YAPI 开放接口说明 | `scripts/parse_yapi.py` 的依据 |

约定：

- **勿在此目录写本项目产出**（产出落位见 `.qoder/rules/output-schema.md`）
- agent 需要这里的内容时按需 Read 单篇，不要整目录通读
