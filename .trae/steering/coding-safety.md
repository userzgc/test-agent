# 工作流安全规则

## 文件操作

- 所有生成的用例文件放 `docs/test-cases/`
- 所有需求分析文档放 `docs/requirements/`
- 所有测试报告放 `docs/reports/`
- 临时文件放 `/tmp/`，不污染项目目录

## 凭据管理

- 凭据统一放 `settings/credentials.json`（不提交 Git）
- Agent 代码中不硬编码密码
- 引用凭据时从 settings 读取

## 质量约束

- 用例编写前必须先完成需求分析
- 用例编写后必须经过评审才能标记为最终版
- 评审发现的问题必须修改后重新生成
- 每个版本变更需记录在 `docs/CHANGELOG.md`
