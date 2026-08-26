#!/usr/bin/env python3
"""禅道登录 + Session 管理（Playwright + curl 混合方案）

用法:
  # 登录并导出 session cookie
  python3 zentao_login.py login

  # 截图确认当前页面
  python3 zentao_login.py screenshot <url> [--output <path>]

  # 检查 session 是否有效
  python3 zentao_login.py check

凭据从 config/credentials.json 读取。
Session cookie 缓存在 /tmp/zentao_session.txt，供 curl 批量操作复用。
"""
import argparse
import json
import os
import sys
from pathlib import Path

CREDENTIALS_PATH = Path(__file__).resolve().parents[1] / "config" / "credentials.json"
SESSION_CACHE = "/tmp/zentao_session.txt"


def load_credentials():
    """从 credentials.json 读取禅道凭据"""
    with open(CREDENTIALS_PATH) as f:
        creds = json.load(f)
    zentao = creds.get("zentao", {})
    return zentao.get("baseUrl", "https://mxbc.chandao.net"), zentao.get("username", ""), zentao.get("password", "")


def save_session(zentaosid):
    """保存 session cookie 供 curl 使用"""
    with open(SESSION_CACHE, "w") as f:
        f.write(zentaosid)
    print(f"Session saved to {SESSION_CACHE}", file=sys.stderr)


def load_session():
    """读取缓存的 session cookie"""
    if os.path.exists(SESSION_CACHE):
        with open(SESSION_CACHE) as f:
            return f.read().strip()
    return None


def login():
    """用 Playwright 登录禅道，导出 session cookie"""
    from playwright.sync_api import sync_playwright

    base_url, username, password = load_credentials()
    if not username or not password:
        print("Error: zentao credentials not found in credentials.json", file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 访问登录页
        login_url = f"{base_url}/user-login-L215Lmh0bWw=.html"
        page.goto(login_url, wait_until="networkidle")

        # 填写表单并提交
        page.fill('input[name="account"]', username)
        page.fill('input[name="password"]', password)
        page.click('button[type="submit"], #submit, input[type="submit"]')

        # 等待跳转（登录成功会跳到首页）
        try:
            page.wait_for_url(f"{base_url}/", timeout=10000)
        except Exception:
            # 可能跳到 my 页面
            pass

        # 提取 session cookie
        cookies = page.context.cookies()
        zentaosid = None
        for cookie in cookies:
            if cookie["name"] == "zentaosid":
                zentaosid = cookie["value"]
                break

        browser.close()

    if zentaosid:
        save_session(zentaosid)
        print(zentaosid)
        return zentaosid
    else:
        print("Error: login failed, no zentaosid found", file=sys.stderr)
        sys.exit(1)


def check_session():
    """检查 session 是否有效"""
    import urllib.request
    import urllib.error

    zentaosid = load_session()
    if not zentaosid:
        print("No session cached. Run `python3 zentao_login.py login` first.", file=sys.stderr)
        return False

    base_url, _, _ = load_credentials()
    req = urllib.request.Request(
        f"{base_url}/my/",
        headers={"Cookie": f"zentaosid={zentaosid}"},
    )
    try:
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            if "zhangguichang" in html or "我的地盘" in html:
                print("Session valid")
                return True
            else:
                print("Session invalid (redirected to login)", file=sys.stderr)
                return False
    except urllib.error.HTTPError as e:
        print(f"HTTP error {e.code}: {e.reason}", file=sys.stderr)
        return False


def screenshot(url, output_path="/tmp/zentao_screenshot.png"):
    """用 Playwright 截图指定页面"""
    from playwright.sync_api import sync_playwright

    base_url, username, password = load_credentials()
    zentaosid = load_session()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # 注入 session cookie
        if zentaosid:
            context.add_cookies([{
                "name": "zentaosid",
                "value": zentaosid,
                "domain": "mxbc.chandao.net",
                "path": "/",
                "secure": True,
                "httpOnly": True,
            }])

        page = context.new_page()
        page.goto(url, wait_until="networkidle")
        page.screenshot(path=output_path, full_page=True)
        browser.close()

    print(f"Screenshot saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="禅道登录 + Session 管理")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("login", help="登录并导出 session cookie")
    sub.add_parser("check", help="检查 session 是否有效")

    ss = sub.add_parser("screenshot", help="截图指定页面")
    ss.add_argument("url", help="要截图的 URL")
    ss.add_argument("--output", default="/tmp/zentao_screenshot.png", help="输出路径")

    args = parser.parse_args()

    if args.command == "login":
        login()
    elif args.command == "check":
        check_session()
    elif args.command == "screenshot":
        screenshot(args.url, args.output)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
