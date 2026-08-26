#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Hook: SessionStart —— 使用日志：每次会话追加一行到 docs/usage-log.csv
#
# 列：时间,操作人,session_id
#   操作人取 git config user.name（每人 clone 后各自的 git 身份，无需手填）
#
# 约定：
#   - 日志入库随 git 同步 = 每次会话产生一行待提交 diff，
#     随日常工作一并手动提交（本项目禁止自动提交）。
#   - 只追加，不改写历史行。
#   - 验证 hook 生效：重启 IDE 开新会话后 tail docs/usage-log.csv 看新行。
# ═══════════════════════════════════════════════════════════════
set -uo pipefail

# ⚠️ 从脚本自身位置推导仓库根，不能靠 cwd（见 known-pitfalls.md 第 3 类）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT" || exit 0

INPUT="$(cat)"  # stdin JSON，含 session_id
SESSION_ID="$(printf '%s' "$INPUT" | jq -r '.session_id // "unknown"' 2>/dev/null || echo unknown)"
OPERATOR="$(git config user.name 2>/dev/null || echo unknown)"
LOG="docs/usage-log.csv"

[ -f "$LOG" ] || echo "时间,操作人,session_id" > "$LOG"
echo "$(date '+%Y-%m-%d %H:%M'),${OPERATOR},${SESSION_ID}" >> "$LOG"

exit 0
