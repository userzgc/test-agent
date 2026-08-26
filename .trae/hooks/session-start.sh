#!/usr/bin/env bash
# Hook: SessionStart 事件触发
# 作用：输出项目上下文摘要，让 Agent 快速了解项目状态
# Trae 会在会话开始时执行此脚本，输出会被 Agent 看到

set -e
cd "$(git rev-parse --show-toplevel 2>/dev/null || echo .)"

echo "=== Test-Agent 项目上下文 ==="
echo ""

# 项目概览
echo "[项目] 测试需求对焦和用例管理项目"
echo ""

# 最近踩坑（取最新1条标题）
if [ -f "docs/lessons-learned.md" ]; then
  LATEST=$(grep "^## " docs/lessons-learned.md | head -1)
  echo "[最近踩坑] $LATEST"
fi
echo ""

# 记忆索引（最近 3 条业务口径 / 会话存档）
# 作用：新会话开始就带上已沉淀的口径，避免重复问用户同样的问题
if [ -f "docs/memory/index.md" ]; then
  echo "[记忆索引] 已沉淀的业务口径（复用前先向用户确认是否仍有效）"
  grep "^| 20" docs/memory/index.md 2>/dev/null | head -3 | awk -F'|' '{gsub(/^ +| +$/,"",$2); gsub(/^ +| +$/,"",$3); gsub(/^ +| +$/,"",$5); print "  - " $2 " | " $3 " | " $5}'
  echo "  详见: docs/memory/index.md | 写入规则: .trae/skills/memory-keeping/SKILL.md"
fi
echo ""

# 用例文件
echo "[用例文件]"
ls docs/test-cases/ 2>/dev/null | head -10
echo ""

# 脚本工具
echo "[可用脚本]"
ls .trae/scripts/ 2>/dev/null
echo ""

# 自改进机制
echo "[自改进] 踩坑记录: docs/lessons-learned.md | 规则: .trae/steering/self-improvement.md"
