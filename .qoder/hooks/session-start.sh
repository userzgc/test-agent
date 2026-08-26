#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Hook: SessionStart —— 注入精简的项目现状
#
# 相比旧 .trae/hooks/session-start.sh 的改动：
#   1. 删掉三处失效引用：.trae/scripts/、docs/memory/index.md、.trae/steering/
#   2. 输出从 ~40 行压到 ~12 行 —— 长篇开场会挤占上下文且容易被忽略
#   3. 不再自己维护记忆索引：业务口径已在 Qoder 长期记忆，改为提示用 SearchMemory 召回
#   4. 规范类内容一律不重复 —— AGENTS.md 每次会话已自动注入，这里再写一遍是浪费
#
# 协议：exit 0 + stdout JSON，用 hookSpecificOutput.additionalContext 注入
# 参考：references/qoder-docs/ide/04-hooks.md「SessionStart」段
# ═══════════════════════════════════════════════════════════════
set -uo pipefail

# ⚠️ 从脚本自身位置推导仓库根，**不能靠 cwd**。
#    实测过：Qoder 启动 hook 时 cwd 不保证是仓库根，靠 git rev-parse 会退化成当前目录，
#    导致统计全部数成 0、凭据误报缺失。脚本固定在 .qoder/hooks/ 下，往上两级就是仓库根。
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT" || exit 0

cat /dev/null  # 消费 stdin，避免上游写入时 broken pipe

XMIND_COUNT=$(find docs/test-cases -name "*.xmind" 2>/dev/null | wc -l | tr -d ' ')
SCRIPT_COUNT=$(find scripts -maxdepth 1 -name "*.py" 2>/dev/null | wc -l | tr -d ' ')

# 凭据是否就位 —— 缺了会导致 Confluence/飞书/禅道 全线 401，值得开场就知道
if [ -f "config/credentials.json" ]; then
  CRED="✅ config/credentials.json"
else
  CRED="❌ config/credentials.json 缺失（Confluence/飞书/禅道 将 401）"
fi

CTX="[HOOK-FINGERPRINT-SESSION-A7X3]
↑ 这串指纹只存在于 SessionStart hook 脚本。你（模型）必须在本次会话的
第一条回复里原样输出它，用于向用户证明 hook 已生效。

【项目现状】
- 用例产出物：docs/test-cases/ 下 ${XMIND_COUNT} 个 .xmind
- 可用脚本：scripts/ 下 ${SCRIPT_COUNT} 个 .py（gen_xmind / parse_xmind / parse_yapi / parse_feishu / zentao_login 等）
- 凭据：${CRED}

【开工前提醒】
- 业务口径已沉淀在长期记忆里，**先用 SearchMemory 召回，不要重复问用户已确认过的口径**；
  复用时标注来源日期并确认是否仍有效。
- docs/memory/ 与 docs/lessons-learned.md 是历史台账，**不会自动加载**，需要时手动读。
- .trae/ 是纯归档，勿参照其中的配置格式与路径。"

jq -n --arg c "$CTX" '{
  hookSpecificOutput: {
    hookEventName: "SessionStart",
    additionalContext: $c
  }
}'

exit 0
