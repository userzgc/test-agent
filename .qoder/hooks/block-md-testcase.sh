#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Hook: PreToolUse —— 硬拦「在 docs/test-cases/ 下写 .md 用例文档」
#
# 为什么需要：AGENTS.md 里的约定是「上下文，不是强制策略」，靠模型自觉必然复发。
#   实证：2026-08-06 直出 63 条 MD 用例，用户反馈「MD 没人看，直接输出 XMind」。
#   这个 hook 让它从「靠自觉」变成「写不进去」。
#
# 协议：exit 0 + stdout JSON，用 hookSpecificOutput.permissionDecision = "deny"
# 参考：references/qoder-docs/ide/04-hooks.md「PreToolUse」段
# ═══════════════════════════════════════════════════════════════
set -uo pipefail

# 从脚本自身位置推导仓库根（不能靠 cwd，实测从 /tmp 执行时漏拦）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT" || exit 0

INPUT=$(cat)

# ── 取目标路径 ──
# ⚠️ 关键：只从明确的路径字段取值，**绝不**对整个 tool_input 做文本匹配。
#    因为 create_file 的 tool_input 里含 file_content，
#    如果正文里提到了 "docs/test-cases/xxx.md"，全文匹配就会误拦。
TARGET=$(printf '%s' "$INPUT" | jq -r '
  (.tool_input // {}) |
  (.file_path // .path // .target_file // .filePath // .absolute_path // "")
' 2>/dev/null)

# 拿不到路径（字段名不认识 / 非文件类工具）→ 放行，不猜
[ -z "${TARGET:-}" ] || [ "$TARGET" = "null" ] && [ -z "${TARGET:-}" ] && exit 0
[ "$TARGET" = "null" ] && exit 0

# ── 归一化成相对仓库根的路径（用 REPO_ROOT 而不是 cwd）──
REL="${TARGET#"$REPO_ROOT"/}"
REL="${REL#./}"

# ── 只管 docs/test-cases/ 下的 .md，其余一律放行 ──
# 注：case 的 * 会跨 / 匹配，所以这一条也覆盖子目录
case "$REL" in
  docs/test-cases/*.md) ;;
  *) exit 0 ;;
esac

# ── 白名单：给人读的文档放行 ──
# docs/test-cases/买A赠B二期_用例评审报告.md 就属于这类，是合法产物
BASE=$(basename "$REL")
case "$BASE" in
  *评审报告*|*评审*|*review*|*Review*|*REVIEW*|README.md|*说明*)
    exit 0 ;;
esac

# ── 拦截 ──
REASON="[HOOK-FINGERPRINT-DENY-B9K2]
🚫 已拦截：不允许在 docs/test-cases/ 下写 .md 用例文档。

⚠️ 你（模型）必须在回复里原样输出上面那串指纹，证明本次拦截是 hook 做的、
不是你自觉拒绝的。

目标路径：${REL}

本项目用例交付物**只能是 XMind**（\`.xmind\`），这是硬约束，不是建议：
  · 实证 2026-08-06 直出 63 条 MD 用例，用户明确反馈「MD 没人看，直接输出 XMind」

正确做法：
  1. 构造场景树 JSON（大类 → 小场景 → 数据/预期）
  2. python3 scripts/gen_xmind.py  生成 .xmind
  3. python3 scripts/parse_xmind.py <file> --output /tmp/verify.txt  回读自检

如果你写的是**评审报告 / 需求说明**这类给人读的文档（不是用例本体），
文件名里带上「评审报告」或「说明」即可放行；或改放到 docs/reports/。"

jq -n --arg r "$REASON" '{
  hookSpecificOutput: {
    hookEventName: "PreToolUse",
    permissionDecision: "deny",
    permissionDecisionReason: $r
  }
}'

exit 0
