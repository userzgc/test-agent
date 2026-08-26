#!/usr/bin/env python3
"""YAPI 导出文档解析器

用法:
  python3 parse_yapi.py <input.md> [--output <output.json>]

解析 YAPI 导出的 Markdown（含 HTML 标签），
提取接口分组、接口名称、路径、方法、参数等信息。

输出: JSON 数组，每项包含:
  - category: 接口分类
  - name: 接口名称
  - path: 接口路径
  - method: HTTP 方法
  - desc: 接口描述
  - headers: 请求头
  - params: 请求参数（query/body）
"""
import json
import re
import sys


def parse_yapi_md(md_content):
    """解析 YAPI 导出的 Markdown"""
    apis = []
    current_category = ""
    current_api = None

    lines = md_content.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 二级标题 = 接口分类
        if line.startswith("## ") and not line.startswith("### "):
            current_category = line.lstrip("# ").strip()
            i += 1
            continue

        # 三级标题 = 接口名称
        if line.startswith("### "):
            # 保存上一个接口
            if current_api:
                apis.append(current_api)

            current_api = {
                "category": current_category,
                "name": line.lstrip("# ").strip(),
                "path": "",
                "method": "",
                "desc": "",
                "headers": [],
                "params": [],
            }
            i += 1
            continue

        # Path
        if line.startswith("**Path：**"):
            if current_api:
                current_api["path"] = line.replace("**Path：**", "").strip()
            i += 1
            continue

        # Method
        if line.startswith("**Method：**"):
            if current_api:
                current_api["method"] = line.replace("**Method：**", "").strip()
            i += 1
            continue

        # 接口描述
        if line.startswith("**接口描述：**"):
            if current_api:
                current_api["desc"] = line.replace("**接口描述：**", "").strip()
            i += 1
            continue

        # 参数表格（简化处理，只提取表格行）
        if line.startswith("|") and current_api:
            # 跳过表头分隔行
            if not re.match(r"^\|[\s-]+\|", line):
                cells = [c.strip() for c in line.strip("|").split("|")]
                if len(cells) >= 4:
                    current_api["params"].append({
                        "name": cells[0],
                        "type": cells[1],
                        "required": cells[2],
                        "example": cells[3] if len(cells) > 3 else "",
                        "remark": cells[4] if len(cells) > 4 else "",
                    })
            i += 1
            continue

        i += 1

    # 保存最后一个接口
    if current_api:
        apis.append(current_api)

    return apis


def main():
    if len(sys.argv) < 2:
        print("用法: python3 parse_yapi.py <input.md> [--output <output.json>]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = None

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 清理 HTML 标签
    content = re.sub(r"<[^>]+>", " ", content)

    apis = parse_yapi_md(content)

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(apis, f, ensure_ascii=False, indent=2)
        print(f"解析完成，共 {len(apis)} 个接口，已保存: {output_path}")
    else:
        # 按分类打印摘要
        categories = {}
        for api in apis:
            cat = api["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(f"  {api['method']} {api['path']} - {api['name']}")

        for cat, items in categories.items():
            print(f"\n## {cat}")
            print("\n".join(items))
        print(f"\n共 {len(apis)} 个接口")


if __name__ == "__main__":
    main()
