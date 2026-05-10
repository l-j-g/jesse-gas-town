#!/usr/bin/env python3

import argparse
import getpass
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.parse
import zipfile
from pathlib import Path

import requests
import websocket


LOGIN_URL = "https://jesse.trade/login"
DEFAULT_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


class CdpPage:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=10)
        self.next_id = 0

    def close(self):
        self.ws.close()

    def send(self, method, params=None):
        self.next_id += 1
        message_id = self.next_id
        self.ws.send(json.dumps({
            "id": message_id,
            "method": method,
            "params": params or {},
        }))

        while True:
            message = json.loads(self.ws.recv())
            if message.get("id") == message_id:
                return message

    def enable(self):
        for method in ("Page.enable", "Runtime.enable", "Network.enable"):
            self.send(method)

    def eval(self, expression):
        response = self.send("Runtime.evaluate", {
            "expression": expression,
            "awaitPromise": True,
            "returnByValue": True,
        })
        result = response.get("result", {})
        if "exceptionDetails" in result:
            return None
        return result.get("result", {}).get("value")

    def navigate(self, url):
        self.send("Page.navigate", {"url": url})
        deadline = time.time() + 45
        while time.time() < deadline:
            ready = self.eval("document.readyState")
            if ready == "complete":
                return
            time.sleep(0.25)
        raise TimeoutError(f"timed out waiting for page load: {url}")

    def body_text(self):
        return self.eval("document.body ? document.body.innerText : ''") or ""


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_devtools(port):
    url = f"http://127.0.0.1:{port}/json/version"
    deadline = time.time() + 30
    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=1)
            if response.ok:
                return response.json()
        except requests.RequestException:
            pass
        time.sleep(0.25)
    raise RuntimeError(f"Chrome DevTools did not start on port {port}")


def create_tab(port):
    response = requests.put(f"http://127.0.0.1:{port}/json/new", timeout=5)
    response.raise_for_status()
    page_info = response.json()
    return CdpPage(page_info["webSocketDebuggerUrl"])


def launch_chrome(chrome_path, profile_dir, download_dir, port):
    profile_dir.mkdir(parents=True, exist_ok=True)
    download_dir.mkdir(parents=True, exist_ok=True)

    command = [
        chrome_path,
        f"--remote-debugging-port={port}",
        "--remote-allow-origins=*",
        f"--user-data-dir={profile_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-popup-blocking",
        LOGIN_URL,
    ]
    return subprocess.Popen(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def set_download_behavior(page, download_dir):
    params = {"behavior": "allow", "downloadPath": str(download_dir)}
    for method in ("Browser.setDownloadBehavior", "Page.setDownloadBehavior"):
        try:
            page.send(method, params)
        except Exception:
            pass


def js_string(value):
    return json.dumps(value)


def fill_login(page, account, password):
    script = f"""
(() => {{
  const account = {js_string(account)};
  const password = {js_string(password)};
  const inputs = Array.from(document.querySelectorAll('input'));
  const accountInput = inputs.find((el) => ['email', 'text'].includes((el.type || '').toLowerCase())) || inputs[0];
  const passwordInput = inputs.find((el) => (el.type || '').toLowerCase() === 'password');

  function setValue(el, value) {{
    if (!el) return false;
    el.focus();
    el.value = value;
    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
    return true;
  }}

  const accountSet = setValue(accountInput, account);
  const passwordSet = setValue(passwordInput, password);
  const buttons = Array.from(document.querySelectorAll('button, input[type=submit], [role=button]'));
  const button = buttons.find((el) => /login/i.test(el.innerText || el.value || el.getAttribute('aria-label') || '')) || buttons[0];
  if (button) button.click();
  return {{ accountSet, passwordSet, clicked: Boolean(button) }};
}})()
"""
    return page.eval(script)


def wait_after_login(page):
    deadline = time.time() + 30
    while time.time() < deadline:
        text = page.body_text().lower()
        if "login to your account" not in text:
            return True
        time.sleep(0.5)
    return False


def click_get_strategy(page):
    script = """
(() => {
  const candidates = Array.from(document.querySelectorAll('button, a, [role=button], input[type=submit]'));
  const target = candidates.find((el) => /get\\s+strategy/i.test(
    el.innerText || el.value || el.getAttribute('aria-label') || ''
  ));
  if (!target) return { clicked: false, reason: 'no get strategy control found' };
  target.scrollIntoView({ block: 'center', inline: 'center' });
  target.click();
  return {
    clicked: true,
    text: (target.innerText || target.value || target.getAttribute('aria-label') || '').trim()
  };
})()
"""
    return page.eval(script) or {"clicked": False, "reason": "click script failed"}


def extract_strategy_code(page):
    script = r"""
(() => {
  const blocks = Array.from(document.querySelectorAll('textarea, pre, code'))
    .map((el) => el.value || el.innerText || el.textContent || '')
    .filter(Boolean);

  const monacoText = Array.from(document.querySelectorAll('.view-line'))
    .map((el) => el.innerText || el.textContent || '')
    .join('\n');
  if (monacoText) blocks.push(monacoText);

  const scripts = Array.from(document.querySelectorAll('script[type="application/json"], script#__NEXT_DATA__'))
    .map((el) => el.innerText || el.textContent || '')
    .filter(Boolean);
  blocks.push(...scripts);

  const candidates = blocks
    .map((text) => text.replace(/\\n/g, '\n'))
    .filter((text) => text.length > 100)
    .filter((text) => /(class\s+\w+.*Strategy|from\s+jesse|import\s+jesse|self\.(buy|sell|take_profit|stop_loss))/i.test(text));

  candidates.sort((a, b) => b.length - a.length);
  return candidates[0] || '';
})()
"""
    text = page.eval(script) or ""
    text = text.strip()
    if len(text) < 100:
        return ""
    return text


def complete_downloads(download_dir):
    return {
        path for path in download_dir.glob("*")
        if path.is_file() and not path.name.endswith(".crdownload")
    }


def wait_for_new_downloads(download_dir, before):
    deadline = time.time() + 20
    while time.time() < deadline:
        current = complete_downloads(download_dir)
        new_files = sorted(current - before)
        if new_files:
            return new_files
        time.sleep(0.5)
    return []


def safe_slug(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-").lower()


def import_download(slug, download_path, output_dir):
    destination_dir = output_dir / slug
    destination_dir.mkdir(parents=True, exist_ok=True)
    if zipfile.is_zipfile(download_path):
        with zipfile.ZipFile(download_path) as archive:
            archive.extractall(destination_dir)
        return str(destination_dir)

    destination = destination_dir / download_path.name
    shutil.copy2(download_path, destination)
    return str(destination)


def write_code(slug, code, output_dir):
    strategy_dir = output_dir / slug
    strategy_dir.mkdir(parents=True, exist_ok=True)
    path = strategy_dir / "Strategy.py"
    path.write_text(code + "\n", encoding="utf-8")
    return str(path)


def load_catalog(path, tiers):
    catalog = json.loads(path.read_text(encoding="utf-8"))
    strategies = catalog["strategies"]
    if tiers:
        wanted = set(tiers)
        strategies = [item for item in strategies if item.get("access_tier", "unknown") in wanted]
    return strategies


def main():
    parser = argparse.ArgumentParser(description="Download Jesse.Trade strategy source through a local Chrome session.")
    parser.add_argument("--catalog", type=Path, default=Path("references/jesse-trade-strategies/catalog.json"))
    parser.add_argument("--output", type=Path, default=Path("references/jesse-trade-strategies/source"))
    parser.add_argument("--profile-dir", type=Path, default=Path("/private/tmp/jesse-trade-chrome-profile"))
    parser.add_argument("--chrome", default=DEFAULT_CHROME)
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--account", default="")
    parser.add_argument("--tiers", default="premium,free,unknown")
    parser.add_argument("--slugs", default="")
    parser.add_argument("--manual-login", action="store_true")
    args = parser.parse_args()

    if not Path(args.chrome).exists():
        raise SystemExit(f"Chrome not found: {args.chrome}")

    args.output.mkdir(parents=True, exist_ok=True)
    download_dir = args.output / "_downloads"
    download_dir.mkdir(parents=True, exist_ok=True)

    tiers = [item.strip() for item in args.tiers.split(",") if item.strip()]
    slugs = {item.strip() for item in args.slugs.split(",") if item.strip()}
    strategies = load_catalog(args.catalog, tiers)
    if slugs:
        strategies = [item for item in strategies if item["slug"] in slugs]

    if not strategies:
        raise SystemExit("No strategies selected")

    port = args.port or free_port()
    process = launch_chrome(args.chrome, args.profile_dir, download_dir, port)
    wait_for_devtools(port)
    page = create_tab(port)
    page.enable()
    set_download_behavior(page, download_dir)

    manifest = {
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "source": str(args.catalog),
        "output": str(args.output),
        "strategies": [],
    }

    try:
        page.navigate(LOGIN_URL)
        if args.manual_login:
            input("Complete login in Chrome, then press Enter here...")
        else:
            account = args.account or input("Jesse.Trade account/email: ")
            password = getpass.getpass("Jesse.Trade password (not echoed): ")
            result = fill_login(page, account, password)
            if not result or not result.get("passwordSet"):
                print("Could not fill the login form. Complete login in Chrome, then press Enter.")
                input()
            elif not wait_after_login(page):
                print("Login was not confirmed. Complete login in Chrome, then press Enter.")
                input()

        for index, strategy in enumerate(strategies, start=1):
            slug = safe_slug(strategy["slug"])
            url = strategy["url"]
            print(f"[{index}/{len(strategies)}] {strategy['name']} ({strategy.get('access_tier', 'unknown')})")
            before = complete_downloads(download_dir)
            page.navigate(url)
            time.sleep(1)
            click_result = click_get_strategy(page)
            time.sleep(2)

            downloaded = wait_for_new_downloads(download_dir, before)
            imported = []
            for download_path in downloaded:
                imported.append(import_download(slug, download_path, args.output))

            code_path = ""
            if not imported:
                code = extract_strategy_code(page)
                if code:
                    code_path = write_code(slug, code, args.output)

            status = "downloaded" if imported else "captured_code" if code_path else "not_found"
            manifest["strategies"].append({
                "slug": slug,
                "name": strategy["name"],
                "tier": strategy.get("access_tier", "unknown"),
                "url": url,
                "click": click_result,
                "status": status,
                "downloads": [str(path) for path in downloaded],
                "imported": imported,
                "code_path": code_path,
            })
            print(f"  -> {status}")

    finally:
        manifest_path = args.output / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        print(f"Manifest: {manifest_path}")
        page.close()
        if process.poll() is None:
            print("Chrome left open so the authenticated session can be reused.")


if __name__ == "__main__":
    main()
