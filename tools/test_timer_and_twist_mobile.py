# -*- coding: utf-8 -*-
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright
import threading

doc_root = r"C:\Users\rsagl\.gemini\antigravity\scratch\ridvanbsaglam.github.io\sims\tell-me-story"

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=doc_root, **kwargs)
    def log_message(self, format, *args):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), CustomHandler)
port = server.server_port
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()

url = f"http://127.0.0.1:{port}/index.html"
print(f"Testing Timer & Twist on {url}")

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={"width": 390, "height": 844}, is_mobile=True, has_touch=True)
    page = context.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=10000)
    page.wait_for_timeout(2000)

    # 1. Start Level 2 (Timer)
    page.evaluate("startLevel(1); render();")
    page.wait_for_timeout(400)

    # Tap 30 sec timer
    res_tm30 = page.evaluate("""() => {
        const z = game.zones.find(x => x.id === 'tm_30');
        const sx = game.ox + (z.x + z.w/2) * game.scale;
        const sy = game.oy + (z.y + z.h/2) * game.scale;
        return { sx, sy };
    }""")
    page.tap("canvas", position={"x": res_tm30["sx"], "y": res_tm30["sy"]})
    page.wait_for_timeout(300)
    t_running = page.evaluate("game.timerRunning")
    t_max = page.evaluate("game.timerMax")
    assert t_running and t_max == 30, "Timer 30s failed to start!"
    print("PASS: 30s timer started")

    # Tap tm_skip ("I'm Ready!")
    res_skip = page.evaluate("""() => {
        const z = game.zones.find(x => x.id === 'tm_skip');
        const sx = game.ox + (z.x + z.w/2) * game.scale;
        const sy = game.oy + (z.y + z.h/2) * game.scale;
        return { sx, sy };
    }""")
    page.tap("canvas", position={"x": res_skip["sx"], "y": res_skip["sy"]})
    page.wait_for_timeout(300)
    t_left = page.evaluate("game.timerLeft")
    assert t_left == 0, "tm_skip failed!"
    print("PASS: tm_skip (I'm Ready) works")

    # Tap tm_reset ("Reset Timer")
    res_reset = page.evaluate("""() => {
        const z = game.zones.find(x => x.id === 'tm_reset');
        const sx = game.ox + (z.x + z.w/2) * game.scale;
        const sy = game.oy + (z.y + z.h/2) * game.scale;
        return { sx, sy };
    }""")
    page.tap("canvas", position={"x": res_reset["sx"], "y": res_reset["sy"]})
    page.wait_for_timeout(300)
    t_max2 = page.evaluate("game.timerMax")
    assert t_max2 == 0, "tm_reset failed!"
    print("PASS: tm_reset works")

    # 2. Test Level 3 (Twist reveal & next)
    page.evaluate("startLevel(2); render();")
    page.wait_for_timeout(400)
    res_twist_rev = page.evaluate("""() => {
        const z = game.zones.find(x => x.id === 'twist_reveal');
        const sx = game.ox + (z.x + z.w/2) * game.scale;
        const sy = game.oy + (z.y + z.h/2) * game.scale;
        return { sx, sy };
    }""")
    page.tap("canvas", position={"x": res_twist_rev["sx"], "y": res_twist_rev["sy"]})
    page.wait_for_timeout(300)
    s_open = page.evaluate("game.sentenceOpen")
    assert s_open, "twist_reveal failed!"
    print("PASS: Twist reveal works")

    # Tap twist_next
    s_idx = page.evaluate("game.sentenceIdx")
    res_twist_next = page.evaluate("""() => {
        const z = game.zones.find(x => x.id === 'twist_next');
        const sx = game.ox + (z.x + z.w/2) * game.scale;
        const sy = game.oy + (z.y + z.h/2) * game.scale;
        return { sx, sy };
    }""")
    page.tap("canvas", position={"x": res_twist_next["sx"], "y": res_twist_next["sy"]})
    page.wait_for_timeout(300)
    s_idx2 = page.evaluate("game.sentenceIdx")
    assert s_idx2 != s_idx, "twist_next failed to cycle sentence!"
    print("PASS: Twist next works")

    print("\nALL TIMER & TWIST BUTTON TESTS PASSED!")
    browser.close()
