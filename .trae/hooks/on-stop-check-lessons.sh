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

# 统计今天的踩坑记录条数（一天可能多次踩坑）
# 注意：grep -c 无匹配时本身已输出 "0" 并返回退出码 1，
#       写成 `|| echo "0"` 会再追加一个 0，得到 "0\n0"。故用 `|| true` 只吞掉退出码。
TODAY_COUNT=$(grep -c "^## $TODAY" "$LESSONS_FILE" 2>/dev/null || true)

# 统计记忆索引条数（文件不存在时 grep 无输出，用 :- 兜默认值）
MEMORY_COUNT=$(grep -c "^| 20" docs/memory/index.md 2>/dev/null || true)
TODAY_COUNT=${TODAY_COUNT:-0}
MEMORY_COUNT=${MEMORY_COUNT:-0}

# 不管今天有几条，都输出检查清单（Hook 无法感知对话内容，每次 stop 都提醒）
cat <<EOF
ℹ️  今日($TODAY)已有 ${TODAY_COUNT} 条踩坑记录，记忆索引共 ${MEMORY_COUNT} 条。请按两份清单检查本次会话：

【A. 踩坑记录】→ docs/lessons-learned.md
1. 本次会话是否被用户纠正过需求理解？
2. 是否有工具调用失败（401/超时/连接失败）并找到根因？→ 必须当场记录，不等下次
3. 是否发现 agent/skill/wiki 需要补充的内容？
4. 是否发现新的边界场景或业务规则？
5. 是否跳过了某个错误继续推进任务？→ 回头补记踩坑

【B. 记忆沉淀】→ docs/memory/（规则见 .trae/skills/memory-keeping/SKILL.md）
6. 本次是否有需求方**口述澄清**的业务口径（文档里没写、只在对话里说过的）？→ docs/memory/decisions.md
7. 是否有"实现容易做反"的口径（聚合 any/all、边界、降级）？→ 单列到「关键实现分歧点」
8. 我的理解是否被用户纠正过、值得存档过程？→ docs/memory/sessions/
9. 是否有未闭环的待确认问题或产品风险？→ decisions.md 对应段落
10. 写入后是否同步更新了 docs/memory/index.md 索引？

如有以上情况按对应格式写入（踩坑格式见 .trae/steering/self-improvement.md）；确实没有可忽略此提醒。
EOF

exit 0
