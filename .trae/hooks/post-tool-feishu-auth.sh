#!/usr/bin/env bash
# Hook: PostToolUse 事件触发（matcher: WebFetch）
# 作用：检测飞书 WebFetch 调用是否因授权失败，提醒改用 lark-cli
# 默认 enabled=false，需要时手动启用

set -e
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)"

# Trae 会传入工具调用的结果，这里做简单检查
# 实际的检测逻辑依赖 Trae 传入的 stdin JSON，这里先做基础提醒
echo "ℹ️  飞书相关操作请优先使用 lark-cli，避免 WebFetch 授权问题"
echo "    参考: references/llm-wiki/wiki/feishu.md"

exit 0
