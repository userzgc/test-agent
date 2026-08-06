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
