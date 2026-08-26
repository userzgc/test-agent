#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Hook: PostToolUseFailure —— 工具调用失败后强提醒记录
#
# 改进点（比旧 .trae/hooks/post-tool-error-detect.sh 好在哪）：
#   1. 用 PostToolUseFailure 事件（Qoder 原生），不再自己 grep 错误关键字
#   2. 落点改为 UpdateMemory，不再指向「没人读的 docs/lessons-learned.md」
#   3. 通过 feedback 注入提醒，不是用 exit 2 阻断工作
#   4. 跳过用户主动中断（is_interrupt），不把「你按了停止」当成故障唠叨
#
# 协议：exit 0 + stdout JSON，用 hookSpecificOutput.feedback 注入提示
# 参考：references/qoder-docs/ide/04-hooks.md「PostToolUseFailure」段
# ═══════════════════════════════════════════════════════════════
set -uo pipefail

# 从脚本自身位置推导仓库根（不能靠 cwd）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT" || exit 0

INPUT=$(cat)

# ── 用户主动中断不算失败，直接放过 ──
IS_INTERRUPT=$(printf '%s' "$INPUT" | jq -r '.is_interrupt // false' 2>/dev/null)
[ "$IS_INTERRUPT" = "true" ] && exit 0

# 提取关键信息
TOOL_NAME=$(printf '%s' "$INPUT" | jq -r '.tool_name // "unknown"' 2>/dev/null)
ERROR_MSG=$(printf '%s' "$INPUT" | jq -r '.error // "（无错误信息）"' 2>/dev/null | head -c 500)

FEEDBACK="[HOOK-FINGERPRINT-FAIL-C5M8]
⚠️ 工具调用失败 [$TOOL_NAME]

你（模型）必须在回复里原样输出上面那串指纹，证明本提醒来自 hook 注入、
不是你自己去读脚本文件看到的。

错误：${ERROR_MSG}

按 failure-protocol.md 的处置协议：
1. 先分析根因（401→凭据过期 / 403→权限不足 / timeout→网络或服务 / 空数据→参数或上游）
2. 用 UpdateMemory (common_pitfalls_experience) 记录可复用教训
3. 用 AskUserQuestion 通知用户并推送选项（重试 / 换方案 / 跳过）
4. 禁止：跳过记录直接换方案、跳过用户确认自己继续"

jq -n --arg fb "$FEEDBACK" '{
  hookSpecificOutput: {
    feedback: $fb
  }
}'

exit 0
