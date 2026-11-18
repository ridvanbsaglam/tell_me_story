# -*- coding: utf-8 -*-
import os
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright

doc_root = r"C:\Users\rsagl\.gemini\antigravity\scratch\ridvanbsaglam.github.io\sims\tell-me-story"

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=doc_root, **kwargs)
    def log_message(self, format, *args):
        pass

server = ThreadingHTTPServer(('127.0.0.1', 0), CustomHandler)
port = server.server_port
import threading
t = threading.Thread(target=server.serve_forever, daemon=True)
t.start()

url = f"http://127.0.0.1:{port}/index.html"
print(f"Testing on {url}")

test_results = []

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=10000)
        page.wait_for_timeout(2500) # assets load

        # 1. Test btn_help click on Hello screen
        # Let's find virtual coordinates of btn_help: VW/2=360, y=1025
        # Convert virtual (360, 1025) to screen touch coords:
        res = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'btn_help');
            if (!z) return null;
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        page.tap(f"canvas", position={"x": res["sx"], "y": res["sy"]})
        page.wait_for_timeout(300)
        help_open = page.evaluate("game.showHelp")
        assert help_open == True, "btn_help failed to open help modal!"
        test_results.append("PASS: btn_help opens modal")

        # 2. Test close_help click
        res_close = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'close_help');
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        page.tap(f"canvas", position={"x": res_close["sx"], "y": res_close["sy"]})
        page.wait_for_timeout(300)
        help_closed = page.evaluate("game.showHelp")
        assert help_closed == False, "close_help failed to close modal!"
        test_results.append("PASS: close_help closes modal")

        # 3. Test Level 1 card tap
        res_lv1 = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'lv1');
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        page.tap("canvas", position={"x": res_lv1["sx"], "y": res_lv1["sy"]})
        page.wait_for_timeout(600)
        screen = page.evaluate("game.screen")
        levelIdx = page.evaluate("game.levelIdx")
        assert screen == "play" and levelIdx == 0, "Level 1 tap failed!"
        test_results.append("PASS: Level 1 starts game")

        # 4. Test Card 1 tap to flip
        res_c1 = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'card1');
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        page.tap("canvas", position={"x": res_c1["sx"], "y": res_c1["sy"]})
        page.wait_for_timeout(300)
        c1_target = page.evaluate("game.cards[0].target")
        assert c1_target == 1, "Card 1 failed to flip on tap!"
        test_results.append("PASS: Card 1 flips on tap")

        # 5. Test Flip All button
        res_flip = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'flip_all');
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        page.tap("canvas", position={"x": res_flip["sx"], "y": res_flip["sy"]})
        page.wait_for_timeout(300)
        all_flipped = page.evaluate("game.cards.every(c => c.target === 1)")
        assert all_flipped == True, "Flip All button failed!"
        test_results.append("PASS: Flip All button flips all cards")

        # 6. Test It Is Done button
        res_done = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'mark_done');
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        page.tap("canvas", position={"x": res_done["sx"], "y": res_done["sy"]})
        page.wait_for_timeout(300)
        all_used = page.evaluate("game.cards.every(c => c.used === true)")
        assert all_used == True, "It Is Done button failed!"
        test_results.append("PASS: It Is Done button marks all cards used")

        # 7. Test Levels button in Top Bar
        res_other = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'other');
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        page.tap("canvas", position={"x": res_other["sx"], "y": res_other["sy"]})
        page.wait_for_timeout(500)
        screen_hello = page.evaluate("game.screen")
        assert screen_hello == "hello", "Levels button in top bar failed!"
        test_results.append("PASS: Levels button returns to Hello screen")

        # 8. Test Level 4 (Guru) & go_write button
        page.evaluate("startLevel(3); render();")
        page.wait_for_timeout(600)
        res_gowrite = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'go_write');
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        page.tap("canvas", position={"x": res_gowrite["sx"], "y": res_gowrite["sy"]})
        page.wait_for_timeout(400)
        phase_write = page.evaluate("game.phase")
        assert phase_write == "write", "go_write button failed to enter write studio!"
        test_results.append("PASS: go_write button enters Write Studio")

        # 9. Test Story Starter Chip
        res_starter1 = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'ins_start_1');
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        page.tap("canvas", position={"x": res_starter1["sx"], "y": res_starter1["sy"]})
        page.wait_for_timeout(300)
        body = page.evaluate("game.storyBody")
        assert len(body) > 0, "Story starter chip tap failed!"
        test_results.append("PASS: Story starter chip inserts text")

        # 10. Test Insert Twist Sentence Chip
        res_twist = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'ins_twist');
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        prev_len = len(body)
        page.tap("canvas", position={"x": res_twist["sx"], "y": res_twist["sy"]})
        page.wait_for_timeout(300)
        body2 = page.evaluate("game.storyBody")
        assert len(body2) > prev_len, "Insert twist sentence button failed!"
        test_results.append("PASS: Insert twist sentence button works")

        # 11. Test Clear Text button
        res_clear = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'txt_clear');
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        page.tap("canvas", position={"x": res_clear["sx"], "y": res_clear["sy"]})
        page.wait_for_timeout(300)
        body3 = page.evaluate("game.storyBody")
        assert len(body3) == 0, "Clear Text button failed!"
        test_results.append("PASS: Clear Text button clears text")

        # 12. Test go_showcase button
        page.evaluate("game.storyBody = 'Once upon a time in space...'; render();")
        res_showcase = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'go_showcase');
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        page.tap("canvas", position={"x": res_showcase["sx"], "y": res_showcase["sy"]})
        page.wait_for_timeout(400)
        phase_sc = page.evaluate("game.phase")
        assert phase_sc == "showcase", "go_showcase button failed to enter showcase!"
        test_results.append("PASS: go_showcase enters Showcase Card")

        # 13. Test Showcase 'Try Another Level' button
        res_sc_other = page.evaluate("""() => {
            const z = game.zones.find(x => x.id === 'other');
            const sx = game.ox + (z.x + z.w/2) * game.scale;
            const sy = game.oy + (z.y + z.h/2) * game.scale;
            return { sx, sy };
        }""")
        page.tap("canvas", position={"x": res_sc_other["sx"], "y": res_sc_other["sy"]})
        page.wait_for_timeout(400)
        sc_hello = page.evaluate("game.screen")
        assert sc_hello == "hello", "Showcase Try Another Level button failed!"
        test_results.append("PASS: Showcase Try Another Level returns to Hello screen")

        browser.close()

    print("\\n==================================")
    print("ALL 13 MOBILE BUTTON TESTS PASSED!")
    print("==================================")
    for r in test_results:
        print("  *", r)

finally:
    server.shutdown()
