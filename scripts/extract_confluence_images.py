#!/usr/bin/env python3
"""Confluence 页面图片提取器

用法:
  python3 extract_confluence_images.py <pageId> [--output <dir>] [--user <user>] [--pass <pass>]

环境变量:
  CONFLUENCE_USER, CONFLUENCE_PASS  认证信息
  CONFLUENCE_BASE                   基础 URL（默认 http://confluence.mxbc-code.com:8090）

从 Confluence 页面 HTML 中提取图片（<ac:image> 和 <img>），下载到本地。
"""
import argparse
import os
import re
import sys
import urllib.request
import urllib.error
import base64
from html.parser import HTMLParser


class ImageTagParser(HTMLParser):
    """解析 Confluence storage 格式 HTML，提取图片引用"""

    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        # Confluence 特有的 ac:image 标签
        if tag == "ac:image":
            # 子元素 ac:attachment > ri:filename 或 ac:url
            self.images.append({"type": "ac_image", "attrs": attrs_dict})
        # 标准 img 标签
        elif tag == "img":
            src = attrs_dict.get("src", "")
            if src:
                self.images.append({"type": "img", "src": src, "attrs": attrs_dict})


def extract_ac_image_filenames(html):
    """从 ac:image 标签中提取 ri:filename"""
    # 匹配 <ac:image>...<ri:filename ri:content-attr="xxx"/></ac:image>
    pattern = r'<ac:image[^>]*>.*?<ri:filename\s+ri:content-attr="([^"]+)"\s*/?>.*?</ac:image>'
    matches = re.findall(pattern, html, re.DOTALL)
    # 也匹配 <ac:attachment>...<ri:filename>
    pattern2 = r'<ac:attachment[^>]*>.*?<ri:filename\s+ri:content-attr="([^"]+)"\s*/?>.*?</ac:attachment>'
    matches2 = re.findall(pattern2, html, re.DOTALL)
    return matches + matches2


def extract_img_srcs(html):
    """从 img 标签中提取 src"""
    pattern = r'<img[^>]+src="([^"]+)"'
    return re.findall(pattern, html)


def fetch_page(page_id, base_url, user, password):
    """获取 Confluence 页面内容"""
    url = f"{base_url}/rest/api/content/{page_id}?expand=body.storage,version,title"
    req = urllib.request.Request(url)
    if user and password:
        credentials = f"{user}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        req.add_header("Authorization", f"Basic {encoded}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            import json
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"HTTP 错误 {e.code}: {e.reason}", file=sys.stderr)
        if e.code == 401:
            print("认证失败，请设置 CONFLUENCE_USER 和 CONFLUENCE_PASS 环境变量", file=sys.stderr)
        return None
    except Exception as e:
        print(f"请求失败: {e}", file=sys.stderr)
        return None


def download_image(url, filepath, user, password):
    """下载单张图片"""
    req = urllib.request.Request(url)
    if user and password:
        credentials = f"{user}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        req.add_header("Authorization", f"Basic {encoded}")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(filepath, "wb") as f:
                f.write(resp.read())
        return True
    except Exception as e:
        print(f"下载失败 {url}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Confluence 页面图片提取器")
    parser.add_argument("pageId", help="Confluence 页面 ID")
    parser.add_argument("--output", default=None, help="输出目录（默认 /tmp/confluence_images/<pageId>/）")
    parser.add_argument("--user", default=os.environ.get("CONFLUENCE_USER", ""), help="用户名")
    parser.add_argument("--pass", dest="password", default=os.environ.get("CONFLUENCE_PASS", ""), help="密码")
    parser.add_argument("--base", default=os.environ.get("CONFLUENCE_BASE", "http://confluence.mxbc-code.com:8090"), help="Confluence 基础 URL")
    args = parser.parse_args()

    output_dir = args.output or f"/tmp/confluence_images/{args.pageId}"
    os.makedirs(output_dir, exist_ok=True)

    # 1. 获取页面
    print(f"获取 Confluence 页面 {args.pageId}...")
    page = fetch_page(args.pageId, args.base, args.user, args.password)
    if not page:
        sys.exit(1)

    title = page.get("title", "")
    html = page.get("body", {}).get("storage", {}).get("value", "")
    print(f"页面标题: {title}")
    print(f"HTML 长度: {len(html)} 字符")

    if not html:
        print("页面内容为空", file=sys.stderr)
        sys.exit(1)

    # 2. 提取图片引用
    ac_filenames = extract_ac_image_filenames(html)
    img_srcs = extract_img_srcs(html)
    print(f"找到 {len(ac_filenames)} 个 ac:image 附件, {len(img_srcs)} 个 img 标签")

    # 3. 下载图片
    downloaded = []
    for filename in ac_filenames:
        url = f"{args.base}/download/attachments/{args.pageId}/{urllib.parse.quote(filename)}"
        filepath = os.path.join(output_dir, filename)
        print(f"下载: {filename}")
        if download_image(url, filepath, args.user, args.password):
            downloaded.append(filepath)

    for src in img_srcs:
        if src.startswith("http"):
            url = src
        elif src.startswith("/"):
            url = f"{args.base}{src}"
        else:
            url = f"{args.base}/{src}"
        filename = os.path.basename(urllib.parse.urlparse(url).path) or f"image_{len(downloaded)}.png"
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            continue
        print(f"下载: {filename}")
        if download_image(url, filepath, args.user, args.password):
            downloaded.append(filepath)

    # 4. 输出结果
    print(f"\n共下载 {len(downloaded)} 张图片到 {output_dir}")
    result = {
        "pageId": args.pageId,
        "title": title,
        "output_dir": output_dir,
        "images": downloaded,
        "ac_image_count": len(ac_filenames),
        "img_count": len(img_srcs),
    }
    import json
    result_path = os.path.join(output_dir, "_meta.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"元数据: {result_path}")


if __name__ == "__main__":
    import urllib.parse
    main()
