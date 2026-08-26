#!/usr/bin/env python3
"""Markdown 用例 → XMind tree JSON

用法:
  python3 md_to_xmind_tree.py <input.md> <output_tree.json>

解析规则：
  ### 模块x：xxx        → 第2层节点
  #### Sxx 【...】xxx  → 第3层节点
  | 字段 | 内容 |      → 第4层节点 "字段: 内容"
                       内容含 <br> → 拆成第5层子节点
"""
import json
import re
import sys


def split_br(text: str):
    """把 '1. xxx<br>2. yyy' 拆成 ['1. xxx', '2. yyy']"""
    parts = re.split(r"<br\s*/?>", text)
    return [p.strip() for p in parts if p.strip()]


def parse_md(path: str):
    root = {"title": "买A赠B二期测试用例", "children": []}
    current_module = None
    current_case = None

    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].rstrip("\n")

        # 二级标题：重置状态（避免后续表格被误挂到上个用例）
        if re.match(r"^##\s+", line):
            current_case = None
            i += 1
            continue

        # 模块：### 模块x：xxx
        m = re.match(r"^###\s+(模块[一二三四五六七]+[：:].+)", line)
        if m:
            current_module = {"title": m.group(1), "children": []}
            root["children"].append(current_module)
            current_case = None
            i += 1
            continue

        # 用例：#### Sxx 【...】xxx
        m = re.match(r"^####\s+(S\d+.*)", line)
        if m:
            current_case = {"title": m.group(1), "children": []}
            if current_module is None:
                current_module = {"title": "(未分类)", "children": []}
                root["children"].append(current_module)
            current_module["children"].append(current_case)
            i += 1
            continue

        # 表格字段：| 字段 | 内容 |
        m = re.match(r"^\|\s*([^|]+?)\s*\|\s*(.+?)\s*\|\s*$", line)
        if m and current_case is not None:
            field = m.group(1).strip()
            value = m.group(2).strip()
            # 跳过表头分隔行
            if field in ("项", "---", "----"):
                i += 1
                continue
            node = {"title": field, "children": []}
            # 华南 v2 风格：字段名作为分类节点，内容拆为子节点
            if "<br>" in value or "<br/>" in value:
                parts = split_br(value)
                node["children"] = [{"title": p, "children": []} for p in parts]
            else:
                # 单行内容也作为子节点
                node["children"] = [{"title": value, "children": []}]
            current_case["children"].append(node)

        i += 1

    return root


def main():
    if len(sys.argv) != 3:
        print("用法: python3 md_to_xmind_tree.py <input.md> <output_tree.json>")
        sys.exit(1)
    tree = parse_md(sys.argv[1])
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)
    # 统计
    modules = len(tree["children"])
    cases = sum(len(m["children"]) for m in tree["children"])
    print(f"已生成 tree JSON: {sys.argv[2]}")
    print(f"模块数: {modules}，用例数: {cases}")


if __name__ == "__main__":
    main()
