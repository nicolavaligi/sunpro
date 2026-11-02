"""Exercise real browser downloads against the local ASGI application.

Run with: python tests/browser_smoke.py (requires Playwright and Chromium).
"""
import json
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    root = Path(__file__).resolve().parents[1]
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
    process = subprocess.Popen([
        sys.executable, '-m', 'uvicorn', 'server:app',
        '--host', '127.0.0.1', '--port', str(port),
    ], cwd=root)
    try:
        deadline = time.monotonic() + 30
        while True:
            try:
                with socket.create_connection(('127.0.0.1', port), timeout=1):
                    break
            except OSError:
                if process.poll() is not None or time.monotonic() >= deadline:
                    raise RuntimeError('ASGI server failed to start')
                time.sleep(0.2)
        with sync_playwright() as playwright, tempfile.TemporaryDirectory() as temporary:
            browser = playwright.chromium.launch()
            page = browser.new_page(accept_downloads=True)
            page.goto(f'http://127.0.0.1:{port}/', wait_until='domcontentloaded')
            page.wait_for_function("typeof SITES !== 'undefined' && typeof SunProPreselection !== 'undefined' && typeof showGuideTip === 'function'")
            page.evaluate('showGuideTip(SITES[0])')
            for extension, label in [('html', 'Scheda preliminare HTML'), ('json', 'Dati e verifiche JSON')]:
                with page.expect_download() as event:
                    page.get_by_role('button', name=label, exact=True).click()
                download = event.value
                assert download.failure() is None
                assert download.suggested_filename.endswith('.' + extension)
                target = Path(temporary) / download.suggested_filename
                download.save_as(target)
                content = target.read_text()
                if extension == 'json':
                    report = json.loads(content)
                    assert report['id'] == page.evaluate('SITES[0].id')
                    assert report['pending']
                    assert report['checks'][3]['value'] == 'Da verificare'
                else:
                    assert 'Scheda di preselezione' in content
                    assert 'Verifiche aperte' in content
            browser.close()
            print('PASS: real Chromium page and HTML/JSON downloads')
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()


if __name__ == '__main__':
    main()
