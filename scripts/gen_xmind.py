#!/usr/bin/env python3
"""XMind 文件生成器

用法:
  python3 gen_xmind.py <input.json> <output.xmind>

input.json 格式:
{
  "title": "根节点标题",
  "children": [
    {
      "title": "一级节点",
      "children": [
        {"title": "二级节点", "children": [{"title": "叶子节点"}]}
      ]
    }
  ]
}

或直接传入 tree 结构（带 children 数组的 dict）
"""
import json
import sys
import zipfile
import uuid


def gid():
    return str(uuid.uuid4())


def build_topic(node):
    """递归构建 XMind topic 节点"""
    title = node.get("title", "")
    children = node.get("children") or []
    icons = node.get("icons", [])

    topic = {
        "id": gid(),
        "class": "topic",
        "title": title,
        "children": None,
    }

    if icons:
        topic["markers"] = {"markerId": icons} if isinstance(icons, str) else {"markers": [{"markerId": i} for i in icons]}

    if children:
        topic["children"] = {
            "attached": [build_topic(c) for c in children]
        }

    return topic


def generate_xmind(tree_data, output_path):
    """生成 XMind 文件"""
    root_topic = build_topic(tree_data)

    sheet = {
        "id": gid(),
        "class": "sheet",
        "title": tree_data.get("title", "测试用例"),
        "rootTopic": root_topic,
        "theme": {
            "id": gid(),
            "map": {"properties": {"svg:fill": "#FFFFFF"}},
        },
    }

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(
            "content.json",
            json.dumps([sheet], ensure_ascii=False, indent=2),
        )
        zf.writestr(
            "metadata.json",
            json.dumps({"creator": {"name": "test-agent"}}),
        )
        zf.writestr(
            "manifest.json",
            json.dumps(
                {
                    "file-entries": {
                        "content.json": {},
                        "metadata.json": {},
                    }
                }
            ),
        )


def main():
    if len(sys.argv) != 3:
        print("用法: python3 gen_xmind.py <input.json> <output.xmind>")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, "r", encoding="utf-8") as f:
        tree_data = json.load(f)

    generate_xmind(tree_data, output_path)
    print(f"XMind 文件已生成: {output_path}")


if __name__ == "__main__":
    main()
