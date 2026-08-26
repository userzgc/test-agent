#!/usr/bin/env python3
"""飞书云表格导出 CSV 解析器

用法:
  python3 parse_feishu.py <input.csv> [--output <output.json>]

解析飞书导出的 CSV，输出 JSON 数组（每行一个对象，key 取表头）。
便于后续基于场景名/模块筛选接口清单。

配合 docs/interface-matrix.csv 使用，
该文件包含字段: 区域, 所属产品, 模块, 场景名称, 场景等级, 接口名称, 涉及接口
"""
import csv
import json
import sys


def parse_csv(csv_path):
    """解析 CSV 为 dict 列表"""
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [row for row in reader]
    return rows


def group_by(rows, group_key="模块"):
    """按指定字段分组"""
    groups = {}
    for row in rows:
        key = row.get(group_key, "未分类")
        if key not in groups:
            groups[key] = []
        groups[key].append(row)
    return groups


def main():
    if len(sys.argv) < 2:
        print("用法: python3 parse_feishu.py <input.csv> [--output <output.json>] [--group-by <字段名>]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = None
    group_by_field = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--output" and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        elif args[i] == "--group-by" and i + 1 < len(args):
            group_by_field = args[i + 1]
            i += 2
        else:
            i += 1

    rows = parse_csv(input_path)

    if output_path:
        if group_by_field:
            result = group_by(rows, group_by_field)
        else:
            result = rows
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"解析完成，共 {len(rows)} 行，已保存: {output_path}")
    else:
        # 按模块打印摘要
        if group_by_field:
            groups = group_by(rows, group_by_field)
            for key, items in groups.items():
                print(f"\n## {key} ({len(items)} 条)")
                for item in items:
                    print(f"  - {item.get('场景名称', '')} [{item.get('场景等级', '')}] {item.get('接口名称', '')}")
        else:
            for row in rows:
                print(json.dumps(row, ensure_ascii=False))
        print(f"\n共 {len(rows)} 行")


if __name__ == "__main__":
    main()
