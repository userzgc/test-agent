#!/usr/bin/env python3
"""图片 OCR 文字提取器

用法:
  python3 ocr_images.py <image_dir> [--lang <lang>] [--output <output.json>]

依赖:
  tesseract OCR 引擎
  - macOS: brew install tesseract tesseract-lang
  - Python 包: pip install pytesseract Pillow

对目录下所有图片做 OCR，输出 JSON（文件名 → 识别文字）。
作为 design-extractor agent 的兜底方案（无法识别布局/交互，仅提取文字）。
"""
import argparse
import json
import os
import sys

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}


def check_tesseract():
    """检查 tesseract 是否安装"""
    import shutil
    return shutil.which("tesseract") is not None


def ocr_image(image_path, lang="chi_sim+eng"):
    """对单张图片做 OCR"""
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img, lang=lang)
        return text.strip()
    except ImportError:
        return None
    except Exception as e:
        return f"[OCR Error: {e}]"


def main():
    parser = argparse.ArgumentParser(description="图片 OCR 文字提取器")
    parser.add_argument("image_dir", help="图片所在目录")
    parser.add_argument("--lang", default="chi_sim+eng", help="OCR 语言（默认 chi_sim+eng）")
    parser.add_argument("--output", default=None, help="输出 JSON 路径（默认 stdout）")
    args = parser.parse_args()

    if not os.path.isdir(args.image_dir):
        print(f"目录不存在: {args.image_dir}", file=sys.stderr)
        sys.exit(1)

    # 检查依赖
    try:
        import pytesseract
        from PIL import Image
    except ImportError:
        print("缺少依赖，请安装:", file=sys.stderr)
        print("  pip install pytesseract Pillow", file=sys.stderr)
        print("  macOS: brew install tesseract tesseract-lang", file=sys.stderr)
        sys.exit(1)

    if not check_tesseract():
        print("tesseract 未安装:", file=sys.stderr)
        print("  macOS: brew install tesseract tesseract-lang", file=sys.stderr)
        sys.exit(1)

    # 收集图片
    images = []
    for f in sorted(os.listdir(args.image_dir)):
        if f.startswith("_") or f.startswith("."):
            continue
        ext = os.path.splitext(f)[1].lower()
        if ext in IMAGE_EXTS:
            images.append(f)

    if not images:
        print(f"目录 {args.image_dir} 中没有图片文件", file=sys.stderr)
        sys.exit(1)

    print(f"找到 {len(images)} 张图片，开始 OCR（语言: {args.lang}）...")

    results = {}
    for i, img_name in enumerate(images, 1):
        img_path = os.path.join(args.image_dir, img_name)
        print(f"[{i}/{len(images)}] {img_name}...", end=" ", flush=True)
        text = ocr_image(img_path, args.lang)
        if text is None:
            print("跳过（依赖缺失）")
            results[img_name] = "[SKIPPED: dependency missing]"
        elif text.startswith("[OCR Error"):
            print(f"失败: {text}")
            results[img_name] = text
        else:
            char_count = len(text)
            print(f"提取 {char_count} 字符")
            results[img_name] = text

    # 输出
    output = {
        "image_dir": args.image_dir,
        "lang": args.lang,
        "image_count": len(images),
        "results": results,
    }

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"\n结果已保存: {args.output}")
    else:
        print("\n" + "=" * 60)
        for img_name, text in results.items():
            print(f"\n--- {img_name} ---")
            print(text)

    # 统计
    total_chars = sum(len(t) for t in results.values() if not t.startswith("["))
    print(f"\n共提取 {total_chars} 字符")


if __name__ == "__main__":
    main()
