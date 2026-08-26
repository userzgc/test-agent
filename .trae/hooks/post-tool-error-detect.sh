#!/usr/bin/env bash
# Hook: PostToolUse 事件触发
# 作用：检测工具返回是否包含错误关键字，如果是则强提醒 Agent 立即记录踩坑
# 匹配 RunCommand（curl/脚本执行最可能失败）

set -e
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)"

# 读取 stdin（Trae PostToolUse hook 会传入工具调用结果）
INPUT=$(cat)

# 检测错误关键字（不区分大小写）
ERROR_PATTERNS="error|401|403|timeout|unauthorized|connection refused|command not found|traceback|exception|access not allowed|exit code [1-9]"

if echo "$INPUT" | grep -iqE "$ERROR_PATTERNS"; then
  cat <<EOF
⚠️⚠️⚠️ 工具调用可能失败！检测到错误关键字。

按照 .trae/steering/self-improvement.md 的"即时记录规则"（最高优先级）：
1. 立即记录踩坑到 docs/lessons-learned.md（不等会话结束）
2. 分析根因
3. 用 AskUserQuestion 通知用户并推送选项
4. 用户确认后才继续推进任务

禁止：跳过记录直接换方案继续、等用户提醒才补记
EOF
fi

exit 0
