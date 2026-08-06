#!/usr/bin/env bash
# Hook: Stop 事件触发
# 作用：检查本次会话是否有新的踩坑经验需要记录到 docs/lessons-learned.md
# 机制：通过对比 today 和 lessons-learned.md 的最后修改时间，
#       输出提醒信息，由 Agent 读取后判断是否需要补充踩坑记录
#
# Trae Stop Hook 的输出会被 Agent 看到，所以这里输出检查清单

set -e
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)"

LESSONS_FILE="docs/lessons-learned.md"
TODAY=$(date +%Y-%m-%d)
NOW_TS=$(date +%s)

# 如果踩坑记录文件不存在，提醒创建
if [ ! -f "$LESSONS_FILE" ]; then
  echo "⚠️  踩坑记录文件 $LESSONS_FILE 不存在，请创建（参考 .trae/steering/self-improvement.md）"
  exit 0
fi

# 检查今天是否已有踩坑记录
if grep -q "^## $TODAY" "$LESSONS_FILE" 2>/dev/null; then
  echo "✅ 今日($TODAY)已有踩坑记录"
  exit 0
fi

# 检查文件最后修改时间，如果是今天修改过但没有今日标题，说明可能漏记
FILE_MTIME=$(stat -f "%m" "$LESSONS_FILE" 2>/dev/null || stat -c "%Y" "$LESSONS_FILE" 2>/dev/null || echo 0)
FILE_DATE=$(date -r "$FILE_MTIME" +%Y-%m-%d 2>/dev/null || date -d @"$FILE_MTIME" +%Y-%m-%d 2>/dev/null || echo "")

if [ "$FILE_DATE" = "$TODAY" ]; then
  echo "ℹ️  今日已修改过 $LESSONS_FILE 但无今日标题，请检查是否需要补充 ## $TODAY 标题"
else
  cat <<'EOF'
⚠️  本次会话尚未记录踩坑经验。请按以下清单检查：

1. 本次会话是否被用户纠正过需求理解？
2. 是否有工具调用失败并找到根因？
3. 是否发现 agent/skill/wiki 需要补充的内容？
4. 是否发现新的边界场景或业务规则？

如有以上情况，按 .trae/steering/self-improvement.md 的格式追加到 docs/lessons-learned.md
如本次会话确实无踩坑，可忽略此提醒
EOF
fi

exit 0
