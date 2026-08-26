# 在脚本中运行（Headless 模式）

> 来源：https://docs.qoder.com/zh/cli/run-in-scripts

Headless（非交互）模式：接收一个提示词 → 执行任务 → 结果输出到 stdout → 退出。
适合嵌入 Shell 脚本、自动化流程和 CI/CD。

入口是 `--print`（`-p`）：
```shell
qoder -p "解释这个代码仓库的架构"
```

> ⚠️ **关键前提**：没有人在旁边确认，所以权限必须**预先配置好**。
> 纯文本 Headless 模式下，任何原本需要弹窗确认的操作会被**自动拒绝**。

## 三种传入方式

```shell
# 1. 参数
qoder -p "生成本次改动的提交信息"

# 2. 标准输入
echo "总结昨天的所有代码变更" | qoder -p

# 3. 脚本中捕获输出
result=$(qoder -p "列出 src 目录下所有导出的函数")
echo "$result"
```

## 输出格式 `-o` / `--output-format`

| 格式 | 说明 | 适用 |
|---|---|---|
| `text` | 纯文本结果（默认） | 直接阅读、简单脚本 |
| `json` | **单个 JSON 对象，含结果和元数据** | 程序化解析最终结果 |
| `stream-json` | **逐条输出的 JSON 消息流** | 实时消费中间过程 |

输入格式 `--input-format` 支持 `text` 和 `stream-json`。
用 `stream-json` 输入时，可通过 stdin **持续发送结构化消息**。

## Headless 常用参数

| 参数 | 说明 |
|---|---|
| `-p, --print` | 打印响应并退出 |
| `-o, --output-format` | text / json / stream-json |
| `--input-format` | text / stream-json |
| **`--max-turns <count>`** | 限制单次查询最大对话轮数 |
| `--permission-mode <mode>` | 权限模式 |
| `--allowed-tools` / `--disallowed-tools` | 工具白/黑名单 |
| `-m, --model` | 指定模型 |
| `--session-id <id>` | 使用指定会话 id |
| `-w, --cwd <dir>` | 启动前切换工作目录 |

## ⭐ 权限控制（Headless 的核心难点）

```shell
# 文件编辑自动通过，Shell 命令仍被拒绝
qoder -p "重构 utils 模块" --permission-mode accept_edits

# 只放行特定工具（注意这种细粒度写法）
qoder -p "检查状态" --allowed-tools 'Read,Bash(git status)'

# 全部放行（仅限可信场景）
qoder -p "执行数据库迁移" --yolo
```

- 纯文本 Headless 下，任何"需要确认"的操作**默认转为拒绝**
- 若由宿主程序通过 **stream-json 协议**驱动（例如 Agent SDK），
  确认请求会**转交宿主程序决策**
- `--permission-mode accept_edits` 自动批准**工作目录内**的安全文件编辑
- `--yolo` ≡ `bypass_permissions`，跳过所有确认，**仅完全可信环境**

> ⭐ `--allowed-tools 'Read,Bash(git status)'` 这种**带参数的工具限定**写法值得注意 ——
> 可以精确到「只允许跑 `git status` 这一条 shell 命令」。

## CI/CD 示例

```shell
export QODER_PERSONAL_ACCESS_TOKEN="your_token"

qoder -p "审查本次改动并列出潜在问题" \
  --output-format json \
  --permission-mode accept_edits \
  --max-turns 20
```

认证见 `/zh/cli/authentication`（尚未抓取）。

## 🎯 本项目落地：用例资产的 CI 校验

```shell
# 只给读权限，禁止任何写入 —— 纯校验场景最安全
qoder -p "校验 docs/test-cases 下所有 xmind 是否含必填字段（用例编号/前置条件/预期结果），
输出不合规清单" \
  -o json \
  --allowed-tools 'Read,Glob,Grep' \
  --max-turns 8
```

要点：
1. **纯校验任务只放行 `Read,Glob,Grep`** —— 不给 Write/Bash，从机制上保证不会误改用例
2. `-o json` 便于流水线后续步骤解析
3. `--max-turns` 必带，防跑飞
4. 需要生成用例时才加 `--permission-mode accept_edits`，且配合 `--worktree` 隔离
