# -*- coding: utf-8 -*-
import os
import time
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright

doc_root = r"C:\Users\rsagl\.gemini\antigravity\scratch\ridvanbsaglam.github.io\sims\tell-me-story"
out_dir = r"C:\Users\rsagl\.gemini\antigravity\brain\ac962468-14fb-4403-80e1-6d3617a93d9b"

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
print(f"Server started on {url}")

try:
    with sync_playwright() as p:
        browser = p.chromium.launch()

        # 1. Mobile Portrait (iPhone 14/15 390x844)
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=10000)
        page.wait_for_timeout(2500) # wait for all images to finish loading

        page.screenshot(path=os.path.join(out_dir, "mobile_portrait_01_hello.png"))
        print("Captured mobile_portrait_01_hello.png")

        # Open Help modal
        page.evaluate("game.showHelp = true; render();")
        page.wait_for_timeout(400)
        page.screenshot(path=os.path.join(out_dir, "mobile_portrait_02_help.png"))
        print("Captured mobile_portrait_02_help.png")
        page.evaluate("game.showHelp = false; render();")

        # Start Level 1 (Rookie)
        page.evaluate("startLevel(0); render();")
        page.wait_for_timeout(600)
        page.evaluate("game.cards.forEach(c => { c.target = 1; c.flip = 1; }); render();")
        page.wait_for_timeout(400)
        page.screenshot(path=os.path.join(out_dir, "mobile_portrait_03_level1_play.png"))
        print("Captured mobile_portrait_03_level1_play.png")

        # Start Level 2 (Expert with timer)
        page.evaluate("startLevel(1); render();")
        page.wait_for_timeout(600)
        page.screenshot(path=os.path.join(out_dir, "mobile_portrait_04_level2_timer.png"))
        print("Captured mobile_portrait_04_level2_timer.png")

        # Start Level 3 (Master with twist revealed)
        page.evaluate("startLevel(2); game.sentenceOpen = true; render();")
        page.wait_for_timeout(600)
        page.screenshot(path=os.path.join(out_dir, "mobile_portrait_05_level3_twist.png"))
        print("Captured mobile_portrait_05_level3_twist.png")

        # Start Level 4 Write Studio
        page.evaluate("startLevel(3); game.phase = 'write'; game.storyBody = 'Once upon a time in a cosmic station, a brave cat found an ancient mystery box...'; render();")
        page.wait_for_timeout(600)
        page.screenshot(path=os.path.join(out_dir, "mobile_portrait_06_level4_write.png"))
        print("Captured mobile_portrait_06_level4_write.png")

        # Start Level 4 Showcase
        page.evaluate("game.phase = 'showcase'; render();")
        page.wait_for_timeout(600)
        page.screenshot(path=os.path.join(out_dir, "mobile_portrait_07_showcase.png"))
        print("Captured mobile_portrait_07_showcase.png")
        context.close()

        # 2. Mobile Landscape (844x390)
        context_land = browser.new_context(
            viewport={"width": 844, "height": 390},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True
        )
        page_land = context_land.new_page()
        page_land.goto(url, wait_until="domcontentloaded", timeout=10000)
        page_land.wait_for_timeout(2000)
        page_land.screenshot(path=os.path.join(out_dir, "mobile_landscape_01_hello.png"))
        print("Captured mobile_landscape_01_hello.png")

        page_land.evaluate("startLevel(0); game.cards.forEach(c => { c.target = 1; c.flip = 1; }); render();")
        page_land.wait_for_timeout(600)
        page_land.screenshot(path=os.path.join(out_dir, "mobile_landscape_02_play.png"))
        print("Captured mobile_landscape_02_play.png")
        context_land.close()

        # 3. Desktop (1280x720)
        context_desk = browser.new_context(viewport={"width": 1280, "height": 720})
        page_desk = context_desk.new_page()
        page_desk.goto(url, wait_until="domcontentloaded", timeout=10000)
        page_desk.wait_for_timeout(2000)
        page_desk.screenshot(path=os.path.join(out_dir, "desktop_01_hello.png"))
        print("Captured desktop_01_hello.png")
        context_desk.close()

        browser.close()
        print("SUCCESSFULLY FINISHED ALL SCREENSHOTS!")

finally:
    server.shutdown()
