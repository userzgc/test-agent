#!/usr/bin/env python3
"""XMind / XMind导出JSON 解析器

用法:
  python3 parse_xmind.py <input.xmind|input.json> [--output <output.txt>]

支持两种输入:
  - .xmind 文件（zip包，读取 content.json）
  - .json 文件（XMind 导出的单行JSON，或 gen_xmind.py 生成的结构）

输出: 树形文本结构，便于阅读和后续分析
"""
import json
import sys
import zipfile


def walk_xmind_topic(topic, depth=0):
    """递归遍历 XMind content.json 的 topic 结构"""
    title = topic.get("title", "")
    children = (topic.get("children") or {}).get("attached") or []
    markers = topic.get("markers", {})
    marker_ids = []
    if isinstance(markers, dict):
        marker_ids = markers.get("markers", [])
        if marker_ids and isinstance(marker_ids[0], dict):
            marker_ids = [m.get("markerId", "") for m in marker_ids]
        elif not marker_ids and markers.get("markerId"):
            marker_ids = [markers.get("markerId")]

    marker_str = f" [{','.join(marker_ids)}]" if marker_ids else ""
    print("  " * depth + "- " + title + marker_str)

    for child in children:
        walk_xmind_topic(child, depth + 1)


def walk_xmind_json(node, depth=0):
    """递归遍历 XMind 导出 JSON（如"买a赠b一期用例.json"）的结构"""
    data = node.get("data", {})
    text = data.get("text", "")
    icons = data.get("icon", [])
    children = node.get("children") or []

    marker_str = f" [{','.join(icons)}]" if icons else ""
    print("  " * depth + "- " + text + marker_str)

    for child in children:
        walk_xmind_json(child, depth + 1)


def parse_xmind_file(xmind_path):
    """解析 .xmind 文件"""
    with zipfile.ZipFile(xmind_path, "r") as zf:
        content = json.loads(zf.read("content.json"))
    # content.json 是数组，取第一个 sheet
    if isinstance(content, list):
        content = content[0]
    root = content.get("rootTopic", {})
    walk_xmind_topic(root)


def parse_json_file(json_path):
    """解析 XMind 导出的 JSON 文件"""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 判断格式：XMind导出JSON有 root 字段，gen_xmind 生成的有 title+children
    if "root" in data:
        # XMind 导出格式
        walk_xmind_json(data["root"])
    elif "rootTopic" in data:
        # content.json 单 sheet 格式
        walk_xmind_topic(data["rootTopic"])
    elif "title" in data:
        # gen_xmind 输入格式
        walk_xmind_topic(data)
    else:
        # 尝试作为 sheet 数组
        if isinstance(data, list) and data:
            sheet = data[0]
            if "rootTopic" in sheet:
                walk_xmind_topic(sheet["rootTopic"])
            elif "root" in sheet:
                walk_xmind_json(sheet["root"])
            else:
                print("无法识别的 JSON 格式", file=sys.stderr)
                sys.exit(1)
        else:
            print("无法识别的 JSON 格式", file=sys.stderr)
            sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print("用法: python3 parse_xmind.py <input.xmind|input.json> [--output <output.txt>]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    # 重定向输出
    if output_path:
        import contextlib
        with open(output_path, "w", encoding="utf-8") as f:
            with contextlib.redirect_stdout(f):
                _parse(input_path)
        print(f"解析结果已保存: {output_path}")
    else:
        _parse(input_path)


def _parse(input_path):
    if input_path.endswith(".xmind"):
        parse_xmind_file(input_path)
    else:
        parse_json_file(input_path)


if __name__ == "__main__":
    main()
