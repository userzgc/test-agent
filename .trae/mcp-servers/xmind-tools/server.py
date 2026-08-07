"""
XMind Tools MCP Server（骨架，占位未实装）

未来对外赋能时启用：把 gen_xmind.py / parse_xmind.py 包装成 MCP Server，
同事在他们的 Trae/Cursor 里配置即可复用。

启用步骤：
1. 安装 mcp python sdk：pip install mcp
2. 在 .trae/mcp.json 添加：
   {
     "xmind-tools": {
       "command": "python3",
       "args": [".trae/mcp-servers/xmind-tools/server.py"]
     }
   }
3. 重启 Trae

当前状态：骨架，工具逻辑待填充（标注 TODO）
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = PROJECT_ROOT / ".trae" / "scripts"


def generate_xmind(tree_json: dict, output_path: str) -> dict:
    """生成 XMind 文件"""
    sys.path.insert(0, str(SCRIPTS_DIR))
    from gen_xmind import generate_xmind as _gen
    _gen(tree_json, output_path)
    return {"status": "ok", "output": output_path}


def parse_xmind(input_path: str) -> dict:
    """解析 XMind/JSON 为树形文本"""
    sys.path.insert(0, str(SCRIPTS_DIR))
    from parse_xmind import parse_xmind_file
    tree_text = parse_xmind_file(input_path)
    return {"status": "ok", "tree": tree_text}


def list_tools() -> dict:
    """列出当前可用的工具"""
    return {
        "tools": [
            {
                "name": "generate_xmind",
                "description": "根据 tree JSON 生成 XMind 文件",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "tree_json": {"type": "object", "description": "场景树 JSON"},
                        "output_path": {"type": "string", "description": "输出 .xmind 路径"}
                    },
                    "required": ["tree_json", "output_path"]
                }
            },
            {
                "name": "parse_xmind",
                "description": "解析 XMind/JSON 为树形文本",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input_path": {"type": "string", "description": "XMind/JSON 文件路径"}
                    },
                    "required": ["input_path"]
                }
            }
        ]
    }


def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    """处理工具调用"""
    if tool_name == "generate_xmind":
        return generate_xmind(arguments["tree_json"], arguments["output_path"])
    elif tool_name == "parse_xmind":
        return parse_xmind(arguments["input_path"])
    else:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}


def main():
    """
    stdio 传输模式入口

    协议：
    - 输入：每行一个 JSON，格式 {"method": "tools/list" | "tools/call", "params": {...}}
    - 输出：每行一个 JSON 响应

    TODO: 替换为 mcp sdk 的标准 Server 实现：
        from mcp.server import Server
        from mcp.server.stdio import stdio_server
        ...
    """
    for line in sys.stdin:
        try:
            req = json.loads(line.strip())
            method = req.get("method")
            params = req.get("params", {})

            if method == "tools/list":
                resp = list_tools()
            elif method == "tools/call":
                resp = handle_tool_call(params.get("name"), params.get("arguments", {}))
            else:
                resp = {"status": "error", "message": f"Unknown method: {method}"}

            sys.stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    print("XMind Tools MCP Server (skeleton)", file=sys.stderr)
    print("Status: 骨架，未实装", file=sys.stderr)
    print(f"Scripts dir: {SCRIPTS_DIR}", file=sys.stderr)
    print("Run `python3 server.py` 启动 stdio 模式（需实装后）", file=sys.stderr)
    main()
