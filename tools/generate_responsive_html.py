# -*- coding: utf-8 -*-
import sys

source_path = r"C:\Users\rsagl\.gemini\antigravity\scratch\ridvanbsaglam.github.io\sims\tell-me-story\index.backup.html"
target_path = r"C:\Users\rsagl\.gemini\antigravity\scratch\ridvanbsaglam.github.io\sims\tell-me-story\index.html"

with open(source_path, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Update meta viewport & add styles
text = text.replace(
    '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />',
    '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />\n  <meta name="theme-color" content="#0c4459" />\n  <meta name="apple-mobile-web-app-capable" content="yes" />\n  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />'
)

textarea_style = """    #native-story-input {
      position: fixed;
      top: -9999px;
      left: -9999px;
      width: 1px;
      height: 1px;
      opacity: 0.01;
      pointer-events: none;
      font-size: 16px;
    }
  </style>"""
text = text.replace('  </style>', textarea_style)

# Add textarea in body
text = text.replace(
    '<canvas id="game-canvas"></canvas>',
    '<textarea id="native-story-input" autocapitalize="sentences" autocomplete="off" spellcheck="true"></textarea>\n  <canvas id="game-canvas"></canvas>'
)

# 2. Update VW, VH to let
text = text.replace(
    'const VW = 1280;\n    const VH = 720;',
    'let VW = 1280;\n    let VH = 720;\n    let isPortrait = false;'
)

# 3. Add fields in game state
text = text.replace(
    'hover: "",\n      scale: 1,',
    'hover: "",\n      scale: 1,\n      isPortrait: false,\n      cardsFlippedCount: 0,\n      cardsUsedCount: 0,'
)

# 4. Background bubbles scaling
old_draw_bg = """    function drawBackground() {
      BUBBLES.forEach((b, i) => {
        const idx = i + 1;
        const dx = Math.sin(game.time * 0.35 + idx * 1.4) * 12;
        const dy = Math.cos(game.time * 0.28 + idx * 1.9) * 9;
        drawSketchBubble(b.x + dx, b.y + dy, b.rad);
      });
    }"""

new_draw_bg = """    function drawBackground() {
      const sx = VW / 1280;
      const sy = VH / 720;
      BUBBLES.forEach((b, i) => {
        const idx = i + 1;
        const dx = Math.sin(game.time * 0.35 + idx * 1.4) * 12;
        const dy = Math.cos(game.time * 0.28 + idx * 1.9) * 9;
        drawSketchBubble(b.x * sx + dx, b.y * sy + dy, b.rad * (isPortrait ? 1.15 : 1.0));
      });
    }"""
text = text.replace(old_draw_bg, new_draw_bg)

# 5. Extract and replace screens block
# Let's locate from `// --- SCREENS (1:1 WITH main.luau) ---` to `function drawSparkles()`
screen_start = text.find('    // --- SCREENS (1:1 WITH main.luau) ---')
sparkles_start = text.find('    function drawSparkles() {')

if screen_start == -1 or sparkles_start == -1:
    print("Error finding screen positions!")
    sys.exit(1)

new_screens_code = '''    // --- SINGLE CARD RENDERER (UNIFIED FOR PORTRAIT & LANDSCAPE) ---
    function drawSingleCard(c, i, cx, cy, cardW, cardH, scaleMult) {
      if (c.target > 0.5) game.cardsFlippedCount++;
      if (c.used) game.cardsUsedCount++;

      const pop = easeOutBack(clamp01(c.pop / 0.50));
      if (c.pop <= 0) return;

      const id = "card" + (i + 1);
      const hov = game.hover === id;
      const lift = hov ? -8 : 0;
      const flipP = c.flip;
      const sx = Math.abs(Math.cos(Math.PI * flipP));
      const front = flipP > 0.5;
      const sc = pop * (hov ? 1.04 : 1.0);
      const w = cardW * sc * Math.max(sx, 0.001);
      const h = cardH * sc;
      const col = CAT_COLORS[c.cat];
      const data = CardsData[c.cat];
      const cxLeft = cx - w / 2;
      const cyTop = cy - h / 2 + lift;

      if (!front) {
        drawSketchBox(cxLeft, cyTop, w, h, 20 * sc, col[0], col[1], col[2], 255, (i + 1) * 23, true);
        if (sx > 0.35) {
          strokeRect(cxLeft + 10 * sx, cyTop + 10, w - 20 * sx, h - 20, 14 * sc, PAPER_R, PAPER_G, PAPER_B, 195, 2.2);
          strokeRect(cxLeft + 12 * sx, cyTop + 12, w - 24 * sx, h - 24, 12 * sc, INK_R, INK_G, INK_B, 140, 1.4);
          label("?", cx, cy - 10 * scaleMult + lift, 92 * sc * sx * scaleMult, PAPER_R, PAPER_G, PAPER_B, 255 * sx, "center");
          label(data.label.toUpperCase(), cx, cy + 82 * scaleMult + lift, 16 * sc * scaleMult, INK_R, INK_G, INK_B, 255 * sx, "center");
        }
      } else {
        drawSketchBox(cxLeft, cyTop, w, h, 20 * sc, PAPER_R, PAPER_G, PAPER_B, 255, (i + 1) * 29, true);

        const banH = 36 * sc * scaleMult;
        fillRect(cxLeft + 3 * sx, cyTop + 3, w - 6 * sx, banH, 16 * sc, col[0], col[1], col[2], 240);
        fillRect(cxLeft + 10 * sx, cyTop + 6, (w - 20 * sx) * 0.65, 6 * sc, 3, 255, 255, 255, 75);
        fillRect(cxLeft + 2 * sx, cyTop + banH + 1, w - 4 * sx, 2.2, 0, INK_R, INK_G, INK_B, 235);
        fillRect(cxLeft + 6 * sx, cyTop + banH + 3.5, w - 12 * sx, 1.0, 0, INK_R, INK_G, INK_B, 115);

        if (sx > 0.3) {
          label(data.label.toUpperCase(), cx, cyTop + banH * 0.52, 15 * scaleMult, INK_R, INK_G, INK_B, 255 * sx, "center");
          const item = data.items[c.item];
          drawImg(item.id, cx, cy + 4 * scaleMult + lift, 132 * sc * scaleMult, sx, c.used ? 0.55 : 1);
          label(cleanItemLabel(item.name), cx, cy + 96 * scaleMult + lift, 14 * scaleMult, INK_R, INK_G, INK_B, 255 * sx * (c.used ? 0.6 : 1), "center");
        }

        if (c.used && sx > 0.3) {
          const bx = cx + cardW / 2 - 26 * scaleMult;
          const by = cy - cardH / 2 + 58 * scaleMult + lift;
          drawSketchCircle(bx, by, 18 * scaleMult, 112, 196, 132, 255, 245);
          ctx.beginPath();
          ctx.moveTo(bx - 7 * scaleMult, by + 1);
          ctx.lineTo(bx - 2 * scaleMult, by + 6 * scaleMult);
          ctx.lineTo(bx + 8 * scaleMult, by - 6 * scaleMult);
          ctx.strokeStyle = rgba(PAPER_R, PAPER_G, PAPER_B, 255);
          ctx.lineWidth = 3.8;
          ctx.lineCap = 'round';
          ctx.lineJoin = 'round';
          ctx.stroke();
          ctx.strokeStyle = rgba(INK_R, INK_G, INK_B, 220);
          ctx.lineWidth = 1.6;
          ctx.stroke();
        }
      }
      zone(id, cx - cardW / 2, cy - cardH / 2, cardW, cardH);
    }

    // --- HELLO SCREEN ---
    function drawHelloLandscape() {
      const t = game.screenT;
      const ts = easeOutBack(clamp01(t / 0.65));
      const bob = Math.sin(game.time * 1.8) * 5;
      drawImg("ui_title", VW / 2, 128 + bob, 310 * ts, 1, clamp01(t / 0.3));

      pill("btn_help", "?  How to Play", VW - 125, 44, 195, 46, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17);

      label("Choose a difficulty level and unleash your storytelling imagination!", VW / 2, 282, 22, 255, 255, 255, 245 * clamp01((t - 0.25) / 0.4), "center");

      const cw = 254, ch = 314, gap = 26;
      const total = 4 * cw + 3 * gap;
      const x0 = (VW - total) / 2;

      LEVELS.forEach((lv, i) => {
        const p = easeOutBack(clamp01((t - 0.30 - 0.09 * i) / 0.50));
        if (p <= 0.02) return;
        const cx = x0 + i * (cw + gap) + cw / 2;
        const cy = 492;
        const hov = game.hover === "lv" + (i + 1);
        const lift = hov ? -10 : 0;
        const sc = p * (hov ? 1.04 : 1.0);
        const w = cw * sc;
        const h = ch * sc;

        drawSketchBox(cx - w / 2, cy - h / 2 + lift, w, h, 24 * sc, PAPER_R, PAPER_G, PAPER_B, 255, (i + 1) * 19, true);

        fillRect(cx - w / 2 + 4, cy - h / 2 + 4 + lift, w - 8, 36 * sc, 18 * sc, lv.col[0], lv.col[1], lv.col[2], 235);
        fillRect(cx - w / 2 + 3, cy - h / 2 + 36 * sc + lift, w - 6, 2, 0, INK_R, INK_G, INK_B, 210);
        label(lv.tag, cx, cy - h / 2 + 22 * sc + lift, 14 * sc, INK_R, INK_G, INK_B, 255, "center");

        drawImg(lv.id, cx, cy - 24 + lift, 136 * sc, 1, 1);
        label(lv.name, cx, cy + 74 + lift, 24 * sc, INK_R, INK_G, INK_B, 255, "center");
        label(lv.sub, cx, cy + 102 + lift, 14 * sc, 75, 70, 65, 255, "center");

        const btnCol = lv.col;
        drawSketchBox(cx - 74 * sc, cy + 118 * sc + lift, 148 * sc, 30 * sc, 15 * sc, btnCol[0], btnCol[1], btnCol[2], 255, (i + 1) * 31, false);
        label("PLAY NOW", cx, cy + 133 * sc + lift, 13 * sc, INK_R, INK_G, INK_B, 255, "center");

        zone("lv" + (i + 1), cx - cw / 2, cy - ch / 2, cw, ch);
      });

      label("Created by Ridvan Saglam  -  Rive Hand-Drawn Edition", VW / 2, 692, 15, 255, 255, 255, 200, "center");
    }

    function drawHelloPortrait() {
      const t = game.screenT;
      const ts = easeOutBack(clamp01(t / 0.65));
      const bob = Math.sin(game.time * 1.8) * 5;
      drawImg("ui_title", VW / 2, 122 + bob, 420 * ts, 1, clamp01(t / 0.3));

      label("Choose your challenge & weave a tale!", VW / 2, 236, 21, 255, 255, 255, 245 * clamp01((t - 0.25) / 0.4), "center");

      const cw = 296, ch = 330, gapx = 24, gapy = 24;
      const x0 = (VW - (2 * cw + gapx)) / 2; // 52

      const positions = [
        { cx: x0 + cw / 2, cy: 435 },
        { cx: x0 + cw + gapx + cw / 2, cy: 435 },
        { cx: x0 + cw / 2, cy: 435 + ch + gapy },
        { cx: x0 + cw + gapx + cw / 2, cy: 435 + ch + gapy }
      ];

      LEVELS.forEach((lv, i) => {
        const p = easeOutBack(clamp01((t - 0.28 - 0.08 * i) / 0.50));
        if (p <= 0.02) return;
        const { cx, cy } = positions[i];
        const hov = game.hover === "lv" + (i + 1);
        const lift = hov ? -8 : 0;
        const sc = p * (hov ? 1.03 : 1.0);
        const w = cw * sc;
        const h = ch * sc;

        drawSketchBox(cx - w / 2, cy - h / 2 + lift, w, h, 24 * sc, PAPER_R, PAPER_G, PAPER_B, 255, (i + 1) * 19, true);

        fillRect(cx - w / 2 + 4, cy - h / 2 + 4 + lift, w - 8, 38 * sc, 18 * sc, lv.col[0], lv.col[1], lv.col[2], 235);
        fillRect(cx - w / 2 + 3, cy - h / 2 + 38 * sc + lift, w - 6, 2, 0, INK_R, INK_G, INK_B, 210);
        label(lv.tag, cx, cy - h / 2 + 24 * sc + lift, 15 * sc, INK_R, INK_G, INK_B, 255, "center");

        drawImg(lv.id, cx, cy - 22 + lift, 142 * sc, 1, 1);
        label(lv.name, cx, cy + 78 + lift, 25 * sc, INK_R, INK_G, INK_B, 255, "center");
        label(lv.sub, cx, cy + 104 + lift, 14 * sc, 75, 70, 65, 255, "center");

        const btnCol = lv.col;
        drawSketchBox(cx - 82 * sc, cy + 124 * sc + lift, 164 * sc, 32 * sc, 16 * sc, btnCol[0], btnCol[1], btnCol[2], 255, (i + 1) * 31, false);
        label("PLAY NOW", cx, cy + 140 * sc + lift, 14 * sc, INK_R, INK_G, INK_B, 255, "center");

        zone("lv" + (i + 1), cx - cw / 2, cy - ch / 2 + lift, cw, ch);
      });

      pill("btn_help", "?  How to Play", VW / 2, 1025, 300, 52, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 18);
      label("Created by Ridvan Saglam  -  Hand-Drawn Edition", VW / 2, 1115, 15, 255, 255, 255, 200, "center");
      label("Tip: Rotate phone to Landscape for Widescreen Table", VW / 2, 1150, 14, 246, 188, 68, 220, "center");
    }

    function drawHello() {
      if (isPortrait) drawHelloPortrait();
      else drawHelloLandscape();
    }

    // --- HELP MODAL ---
    function drawHelpModalLandscape() {
      fillRect(0, 0, VW, VH, 0, 6, 22, 32, 205);
      const mw = 920, mh = 545;
      const mx = (VW - mw) / 2, my = (VH - mh) / 2;
      drawSketchBox(mx, my, mw, mh, 26, PAPER_R, PAPER_G, PAPER_B, 255, 77, true);
      fillRect(mx + 4, my + 4, mw - 8, 68, 22, 246, 194, 62, 240);
      fillRect(mx + 4, my + 70, mw - 8, 2.5, 0, INK_R, INK_G, INK_B, 220);
      label("HOW TO PLAY TELL ME!", VW / 2, my + 38, 26, INK_R, INK_G, INK_B, 255, "center");

      label("Flip 5 random cards and weave them into one creative story!", VW / 2, my + 105, 18, 55, 50, 45, 255, "center");

      LEVELS.forEach((lv, i) => {
        const ry = my + 142 + i * 76;
        drawSketchBox(mx + 36, ry, mw - 72, 64, 16, 252, 249, 242, 255, (i + 1) * 11, false);
        fillRect(mx + 40, ry + 4, 12, 56, 6, lv.col[0], lv.col[1], lv.col[2], 255);
        drawImg(lv.id, mx + 86, ry + 32, 46, 1, 1);
        label(`${lv.tag} - ${lv.name}`, mx + 126, ry + 22, 17, INK_R, INK_G, INK_B, 255, "left");
        label(lv.desc, mx + 126, ry + 45, 15, 75, 70, 65, 255, "left");
      });

      pill("close_help", "Got it, let's play!", VW / 2, my + mh - 42, 240, 48, 246, 194, 62, INK_R, INK_G, INK_B, 19);
    }

    function drawHelpModalPortrait() {
      fillRect(0, 0, VW, VH, 0, 6, 22, 32, 215);
      const mw = 660, mh = 1060;
      const mx = (VW - mw) / 2, my = (VH - mh) / 2;
      drawSketchBox(mx, my, mw, mh, 26, PAPER_R, PAPER_G, PAPER_B, 255, 77, true);
      fillRect(mx + 4, my + 4, mw - 8, 72, 22, 246, 194, 62, 240);
      fillRect(mx + 4, my + 74, mw - 8, 2.5, 0, INK_R, INK_G, INK_B, 220);
      label("HOW TO PLAY TELL ME!", VW / 2, my + 42, 26, INK_R, INK_G, INK_B, 255, "center");

      label("Flip 5 random cards and weave them into one creative story!", VW / 2, my + 110, 17, 55, 50, 45, 255, "center");

      LEVELS.forEach((lv, i) => {
        const ry = my + 140 + i * 195;
        drawSketchBox(mx + 28, ry, mw - 56, 180, 18, 252, 249, 242, 255, (i + 1) * 11, false);
        fillRect(mx + 32, ry + 4, 14, 172, 6, lv.col[0], lv.col[1], lv.col[2], 255);
        drawImg(lv.id, mx + 95, ry + 90, 84, 1, 1);
        label(`${lv.tag} - ${lv.name}`, mx + 155, ry + 42, 22, INK_R, INK_G, INK_B, 255, "left");
        drawParagraph(lv.desc, mx + 155, ry + 68, 38, 22, 16, 65, 60, 55, 255, "left");
        label(lv.sub, mx + 155, ry + 152, 15, lv.col[0], lv.col[1], lv.col[2], 255, "left");
      });

      pill("close_help", "Got it, let's play!", VW / 2, my + mh - 48, 280, 52, 246, 194, 62, INK_R, INK_G, INK_B, 19);
    }

    function drawHelpModal() {
      if (isPortrait) drawHelpModalPortrait();
      else drawHelpModalLandscape();
    }

    // --- TOP BAR ---
    function drawTopBarLandscape() {
      const lv = LEVELS[game.levelIdx];
      fillRect(0, 0, VW, 86, 0, 6, 36, 48, 95);
      fillRect(0, 85, VW, 2, 0, INK_R, INK_G, INK_B, 175);
      fillRect(0, 87, VW, 1, 0, 255, 255, 255, 45);

      drawSketchCircle(48, 43, 25, PAPER_R, PAPER_G, PAPER_B, 255, 245);
      drawImg("ui_home", 48, 43, 25, 1, 1);
      zone("home", 20, 15, 56, 56);

      drawImg(lv.id, 114, 43, 56, 1, 1);
      label(`${lv.tag} - ${lv.name}`, 156, 33, 26, 255, 255, 255, 255, "left");
      label(lv.sub, 156, 59, 15, 235, 245, 250, 235, "left");

      pill("shuffle", "New Cards", VW - 360, 43, 155, 44, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17);
      pill("other", "Try Another Level", VW - 145, 43, 235, 44, 246, 188, 68, INK_R, INK_G, INK_B, 17);
    }

    function drawTopBarPortrait() {
      const lv = LEVELS[game.levelIdx];
      fillRect(0, 0, VW, 96, 0, 6, 36, 48, 95);
      fillRect(0, 95, VW, 2, 0, INK_R, INK_G, INK_B, 175);
      fillRect(0, 97, VW, 1, 0, 255, 255, 255, 45);

      drawSketchCircle(46, 48, 25, PAPER_R, PAPER_G, PAPER_B, 255, 245);
      drawImg("ui_home", 46, 48, 25, 1, 1);
      zone("home", 18, 20, 56, 56);

      drawImg(lv.id, 106, 48, 50, 1, 1);
      label(`${lv.tag}`, 142, 38, 19, 255, 255, 255, 255, "left");
      label(lv.name, 142, 64, 15, 235, 245, 250, 235, "left");

      pill("shuffle", "New Cards", VW - 165, 48, 110, 42, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 15);
      pill("other", "Levels", VW - 55, 48, 85, 42, 246, 188, 68, INK_R, INK_G, INK_B, 15);
    }

    function drawTopBar() {
      if (isPortrait) drawTopBarPortrait();
      else drawTopBarLandscape();
    }

    // --- PLAY STAGE ---
    function drawPlayStageLandscape() {
      drawTopBarLandscape();

      const hasTopPanel = game.levelIdx >= 1;
      const cardsY = hasTopPanel ? 425 : 355;
      const cardsScale = hasTopPanel ? 0.92 : 1.0;

      const cardW = 194 * cardsScale;
      const cardH = 260 * cardsScale;
      const gapx = 24 * cardsScale;
      const total = 5 * cardW + 4 * gapx;
      const x0 = (VW - total) / 2;

      game.cardsFlippedCount = 0;
      game.cardsUsedCount = 0;

      game.cards.forEach((c, i) => {
        const cx = x0 + i * (cardW + gapx) + cardW / 2;
        drawSingleCard(c, i, cx, cardsY, cardW, cardH, cardsScale);
      });

      const flipped = game.cardsFlippedCount;
      const used = game.cardsUsedCount;

      if (game.levelIdx >= 1) {
        const barY = 175;
        if (game.levelIdx === 1) {
          drawSketchBox(VW / 2 - 360, barY - 62, 720, 124, 22, PAPER_R, PAPER_G, PAPER_B, 255, 41, true);
          if (game.timerMax === 0) {
            label("How much time do you need to get ready?", VW / 2, barY - 26, 20, INK_R, INK_G, INK_B, 255, "center");
            pill("tm_30", "30 sec.", VW / 2 - 180, barY + 24, 145, 44, 94, 188, 134, INK_R, INK_G, INK_B, 17);
            pill("tm_45", "45 sec.", VW / 2, barY + 24, 145, 44, 98, 152, 224, INK_R, INK_G, INK_B, 17);
            pill("tm_60", "60 sec.", VW / 2 + 180, barY + 24, 145, 44, 246, 188, 68, INK_R, INK_G, INK_B, 17);
          } else if (game.timerLeft > 0) {
            const secs = Math.ceil(game.timerLeft);
            label(`PREP TIME: ${secs} SECONDS LEFT`, VW / 2 - 110, barY - 22, 21, 215, 75, 70, 255, "center");
            const pw = 420;
            const px = VW / 2 - 320;
            drawSketchBox(px, barY + 8, pw, 18, 9, 232, 226, 212, 255, 12, false);
            const ratio = clamp01(game.timerLeft / game.timerMax);
            fillRect(px + 2, barY + 10, Math.max(14, (pw - 4) * ratio), 14, 7, 94, 188, 134, 255);
            label("Ready early? Skip the countdown!", px + pw / 2, barY + 42, 14, 85, 80, 75, 255, "center");
            pill("tm_skip", "I'm Ready! Start Now", VW / 2 + 215, barY + 6, 220, 48, 246, 188, 68, INK_R, INK_G, INK_B, 17);
          } else {
            label("Time is up! Let's hear your story now!", VW / 2 - 90, barY, 22, 45, 135, 85, 255, "center");
            pill("tm_reset", "Reset Timer", VW / 2 + 230, barY, 165, 42, 246, 188, 68, INK_R, INK_G, INK_B, 16);
          }
        } else {
          const lx = 76, lw = 540;
          drawSketchBox(lx, barY - 62, lw, 124, 22, PAPER_R, PAPER_G, PAPER_B, 255, 53, true);
          if (game.timerMax === 0) {
            label("1. Choose your prep timer:", lx + lw / 2, barY - 26, 18, INK_R, INK_G, INK_B, 255, "center");
            pill("tm_30", "30 sec.", lx + 110, barY + 22, 125, 42, 94, 188, 134, INK_R, INK_G, INK_B, 16);
            pill("tm_45", "45 sec.", lx + 270, barY + 22, 125, 42, 98, 152, 224, INK_R, INK_G, INK_B, 16);
            pill("tm_60", "60 sec.", lx + 430, barY + 22, 125, 42, 246, 188, 68, INK_R, INK_G, INK_B, 16);
          } else if (game.timerLeft > 0) {
            const secs = Math.ceil(game.timerLeft);
            label(`PREP TIMER: ${secs}s`, lx + 165, barY - 20, 20, 215, 75, 70, 255, "center");
            const pw = 290;
            drawSketchBox(lx + 24, barY + 12, pw, 16, 8, 232, 226, 212, 255, 19, false);
            fillRect(lx + 26, barY + 14, Math.max(12, (pw - 4) * clamp01(game.timerLeft / game.timerMax)), 12, 6, 94, 188, 134, 255);
            pill("tm_skip", "I'm Ready!", lx + 425, barY + 4, 170, 44, 246, 188, 68, INK_R, INK_G, INK_B, 16);
          } else {
            label("Prep complete! Tell your story!", lx + 195, barY, 19, 45, 135, 85, 255, "center");
            pill("tm_reset", "Reset", lx + 450, barY, 120, 40, 246, 188, 68, INK_R, INK_G, INK_B, 15);
          }

          const rx = 644, rw = 560;
          drawSketchBox(rx, barY - 62, rw, 124, 22, 252, 243, 215, 255, 67, true);
          if (!game.sentenceOpen) {
            drawSketchCircle(rx + 68, barY, 38, 246, 188, 68, 255, 245);
            label("?", rx + 68, barY, 42, INK_R, INK_G, INK_B, 255, "center");
            label("2. Secret Twist Sentence!", rx + 130, barY - 18, 19, INK_R, INK_G, INK_B, 255, "left");
            label("Tap to reveal the sentence you MUST use!", rx + 130, barY + 12, 15, 95, 80, 60, 255, "left");
            zone("twist_reveal", rx, barY - 62, rw, 124);
          } else {
            drawSketchBox(rx + 18, barY - 46, 138, 26, 13, 238, 108, 104, 255, 3, false);
            label("TWIST SENTENCE", rx + 87, barY - 33, 12, INK_R, INK_G, INK_B, 255, "center");
            label(`"${SENTENCES[game.sentenceIdx]}"`, rx + rw / 2, barY + 8, 19, INK_R, INK_G, INK_B, 255, "center");
            pill("twist_next", "New Sentence", rx + rw - 88, barY - 33, 138, 28, 246, 188, 68, INK_R, INK_G, INK_B, 13);
          }
        }
      }

      const footY = 608;
      let msg = "Let's pick our cards to start with! Tap each card to flip it.";
      if (flipped === 5 && used < 5) {
        msg = `When a card is used in your story, tap on it to mark it done (${used}/5).`;
      } else if (used === 5) {
        msg = (game.levelIdx === 3)
          ? "All 5 cards used! Ready to write and frame your story?"
          : "Excellent! You used all 5 cards! Why don't you try another level now?";
      }
      label(msg, VW / 2, footY, 20, 255, 255, 255, 245, "center");

      if (game.levelIdx === 3) {
        pill("go_write", "Write Your Story Now  ->", VW / 2 - 150, 666, 280, 50, 246, 188, 68, INK_R, INK_G, INK_B, 18);
        pill("flip_all", "Flip All Cards", VW / 2 + 155, 666, 220, 50, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 18);
      } else {
        pill("flip_all", "Flip All Cards", VW / 2 - 145, 666, 235, 50, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 18);
        pill("mark_done", "It Is Done!", VW / 2 + 145, 666, 235, 50, 112, 196, 132, INK_R, INK_G, INK_B, 18);
      }
    }

    function drawPlayStagePortrait() {
      drawTopBarPortrait();

      game.cardsFlippedCount = 0;
      game.cardsUsedCount = 0;

      const hasTopPanel = game.levelIdx >= 1;
      const cy1 = hasTopPanel ? 395 : 355;
      const cy2 = cy1 + 295;

      const cardW = 205, cardH = 275;
      const gap1 = 18;
      const x0_1 = (VW - (3 * cardW + 2 * gap1)) / 2; // 34.5
      drawSingleCard(game.cards[0], 0, x0_1 + cardW / 2, cy1, cardW, cardH, 1.0);
      drawSingleCard(game.cards[1], 1, x0_1 + cardW + gap1 + cardW / 2, cy1, cardW, cardH, 1.0);
      drawSingleCard(game.cards[2], 2, x0_1 + (cardW + gap1) * 2 + cardW / 2, cy1, cardW, cardH, 1.0);

      const gap2 = 28;
      const x0_2 = (VW - (2 * cardW + gap2)) / 2; // 139
      drawSingleCard(game.cards[3], 3, x0_2 + cardW / 2, cy2, cardW, cardH, 1.0);
      drawSingleCard(game.cards[4], 4, x0_2 + cardW + gap2 + cardW / 2, cy2, cardW, cardH, 1.0);

      const flipped = game.cardsFlippedCount;
      const used = game.cardsUsedCount;

      if (game.levelIdx === 1) {
        const barY = 175;
        drawSketchBox(36, barY - 60, 648, 120, 22, PAPER_R, PAPER_G, PAPER_B, 255, 41, true);
        if (game.timerMax === 0) {
          label("Prep time challenge:", VW / 2, barY - 24, 19, INK_R, INK_G, INK_B, 255, "center");
          pill("tm_30", "30 sec.", VW / 2 - 175, barY + 22, 140, 42, 94, 188, 134, INK_R, INK_G, INK_B, 16);
          pill("tm_45", "45 sec.", VW / 2, barY + 22, 140, 42, 98, 152, 224, INK_R, INK_G, INK_B, 16);
          pill("tm_60", "60 sec.", VW / 2 + 175, barY + 22, 140, 42, 246, 188, 68, INK_R, INK_G, INK_B, 16);
        } else if (game.timerLeft > 0) {
          const secs = Math.ceil(game.timerLeft);
          label(`PREP TIME: ${secs}s LEFT`, 200, barY - 20, 20, 215, 75, 70, 255, "center");
          const pw = 340, px = 54;
          drawSketchBox(px, barY + 12, pw, 16, 8, 232, 226, 212, 255, 12, false);
          const ratio = clamp01(game.timerLeft / game.timerMax);
          fillRect(px + 2, barY + 14, Math.max(12, (pw - 4) * ratio), 12, 6, 94, 188, 134, 255);
          pill("tm_skip", "I'm Ready!", 550, barY + 6, 180, 46, 246, 188, 68, INK_R, INK_G, INK_B, 16);
        } else {
          label("Time is up! Let's hear your story!", 250, barY, 20, 45, 135, 85, 255, "center");
          pill("tm_reset", "Reset Timer", 550, barY, 160, 42, 246, 188, 68, INK_R, INK_G, INK_B, 16);
        }
      } else if (game.levelIdx >= 2) {
        const barY = 175;
        const rw = 648, rx = 36;
        drawSketchBox(rx, barY - 60, rw, 120, 22, 252, 243, 215, 255, 67, true);
        if (!game.sentenceOpen) {
          drawSketchCircle(rx + 64, barY, 36, 246, 188, 68, 255, 245);
          label("?", rx + 64, barY, 40, INK_R, INK_G, INK_B, 255, "center");
          label("Secret Twist Sentence!", rx + 125, barY - 16, 20, INK_R, INK_G, INK_B, 255, "left");
          label("Tap to reveal the sentence you MUST use!", rx + 125, barY + 14, 15, 95, 80, 60, 255, "left");
          zone("twist_reveal", rx, barY - 60, rw, 120);
        } else {
          drawSketchBox(rx + 18, barY - 46, 138, 26, 13, 238, 108, 104, 255, 3, false);
          label("TWIST SENTENCE", rx + 87, barY - 33, 12, INK_R, INK_G, INK_B, 255, "center");
          label(`"${SENTENCES[game.sentenceIdx]}"`, rx + rw / 2, barY + 10, 18, INK_R, INK_G, INK_B, 255, "center");
          pill("twist_next", "New Sentence", rx + rw - 88, barY - 33, 138, 28, 246, 188, 68, INK_R, INK_G, INK_B, 13);
        }
      }

      const footY = cy2 + 172;
      let msg = "Tap each card to flip and reveal!";
      if (flipped === 5 && used < 5) {
        msg = `When used in your story, tap to mark done (${used}/5).`;
      } else if (used === 5) {
        msg = (game.levelIdx === 3)
          ? "All 5 cards used! Ready to write your story?"
          : "Awesome! You used all 5 cards!";
      }
      label(msg, VW / 2, footY, 19, 255, 255, 255, 245, "center");

      if (game.levelIdx === 3) {
        pill("go_write", "Write Your Story Now  ->", VW / 2, footY + 65, 480, 56, 246, 188, 68, INK_R, INK_G, INK_B, 20);
        pill("flip_all", "Flip All", VW / 2 - 130, footY + 135, 230, 48, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17);
        pill("shuffle", "New Cards", VW / 2 + 130, footY + 135, 230, 48, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17);
      } else {
        pill("flip_all", "Flip All", VW / 2 - 135, footY + 65, 240, 50, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 18);
        pill("mark_done", "It Is Done!", VW / 2 + 135, footY + 65, 240, 50, 112, 196, 132, INK_R, INK_G, INK_B, 18);
        pill("shuffle", "Shuffle 5 New Cards", VW / 2, footY + 132, 340, 46, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17);
      }
    }

    function drawPlayStage() {
      if (isPortrait) drawPlayStagePortrait();
      else drawPlayStageLandscape();
    }

    // --- WRITE STUDIO ---
    function drawWriteStudioLandscape() {
      drawTopBarLandscape();

      drawSketchBox(48, 96, VW - 96, 74, 18, PAPER_R, PAPER_G, PAPER_B, 255, 17, true);
      label("YOUR STORY ELEMENTS:", 72, 120, 13, 95, 85, 75, 255, "left");
      label(`Twist: "${SENTENCES[game.sentenceIdx]}"`, 72, 146, 15, INK_R, INK_G, INK_B, 255, "left");

      game.cards.forEach((c, i) => {
        const data = CardsData[c.cat];
        const item = data.items[c.item];
        const bx = 540 + i * 138;
        const col = CAT_COLORS[c.cat];
        drawSketchBox(bx, 104, 128, 58, 12, 252, 249, 242, 255, (i + 1) * 13, false);
        drawImg(item.id, bx + 28, 133, 42, 1, 1);
        label(data.label, bx + 54, 124, 12, col[0], col[1], col[2], 255, "left");
        label(cleanItemLabel(item.name), bx + 54, 142, 11, INK_R, INK_G, INK_B, 255, "left");
        zone("card" + (i + 1), bx, 104, 128, 58);
      });

      const px = 48, py = 184, pw = 720, ph = 310;
      drawSketchBox(px, py, pw, ph, 22, PAPER_R, PAPER_G, PAPER_B, 255, 31, true);
      fillRect(px + 3, py + 3, pw - 6, 40, 18, 166, 110, 218, 240);
      fillRect(px + 3, py + 43, pw - 6, 2, 0, INK_R, INK_G, INK_B, 220);
      label("WRITE YOUR STORY BELOW (Type directly with your keyboard, or click chips & cards)", px + 22, py + 23, 15, INK_R, INK_G, INK_B, 255, "left");

      const blink = (Math.floor(game.time * 2) % 2 === 0) ? "|" : "";
      const displayStr = game.storyBody + blink;
      if (game.storyBody.length === 0) {
        label("Type directly with your keyboard, tap any Story Starter on the right, or click cards...", px + 24, py + 74, 16, 130, 120, 110, 255, "left");
      } else {
        drawParagraph(displayStr, px + 24, py + 70, 62, 26, 18, INK_R, INK_G, INK_B, 255, "left");
      }

      zone("notepad_tap", px, py, pw, ph);

      label(`${game.storyBody.length} chars`, px + 24, py + ph - 22, 14, 110, 100, 90, 255, "left");
      pill("txt_clear", "Clear Text", px + pw - 80, py + ph - 24, 120, 32, 238, 108, 104, INK_R, INK_G, INK_B, 14);

      const rx = 788, ry = 184, rw = 444, rh = 310;
      drawSketchBox(rx, ry, rw, rh, 22, PAPER_R, PAPER_G, PAPER_B, 255, 43, true);
      label("QUICK INSERT CHIPS (1-Click Add)", rx + 22, ry + 26, 16, INK_R, INK_G, INK_B, 255, "left");

      STORY_STARTERS.forEach((st, i) => {
        const cy = ry + 58 + i * 34;
        pill("ins_start_" + (i + 1), "+ " + st, rx + rw / 2, cy, rw - 36, 28, 252, 249, 242, INK_R, INK_G, INK_B, 14);
      });
      pill("ins_twist", "+ Insert Twist Sentence", rx + rw / 2, ry + 272, rw - 36, 34, 246, 188, 68, INK_R, INK_G, INK_B, 15);

      const ky = 510;
      KB_ROWS.forEach((row, rIdx) => {
        const kw = 54, kh = 42, kgap = 8;
        const rowW = row.length * kw + (row.length - 1) * kgap;
        const kx0 = 48 + (720 - rowW) / 2;
        const curY = ky + rIdx * (kh + 8);
        row.forEach((ch, cIdx) => {
          const labelCh = game.shiftOn ? ch : ch.toLowerCase();
          const kcx = kx0 + cIdx * (kw + kgap) + kw / 2;
          pill("key_" + labelCh, labelCh, kcx, curY + kh / 2, kw, kh, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17);
        });
      });

      pill("key_shift", game.shiftOn ? "SHIFT (ON)" : "shift", 115, 672, 130, 40, game.shiftOn ? 246 : 232, game.shiftOn ? 188 : 226, game.shiftOn ? 68 : 212, INK_R, INK_G, INK_B, 15);
      pill("key_space", "SPACE", 395, 672, 390, 40, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 16);
      pill("key_back", "BACKSPACE", 680, 672, 150, 40, 238, 108, 104, INK_R, INK_G, INK_B, 15);

      pill("back_cards", "<- Back to Cards", 1010, 555, 440, 48, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17);
      pill("go_showcase", "Create Story Card (Share / Screenshot)", 1010, 625, 440, 60, 112, 196, 132, INK_R, INK_G, INK_B, 18);
    }

    function drawWriteStudioPortrait() {
      drawTopBarPortrait();

      const sw = VW - 48, sx = 24;
      drawSketchBox(sx, 110, sw, 68, 16, PAPER_R, PAPER_G, PAPER_B, 255, 17, true);
      label("CARDS:", sx + 18, 134, 13, 95, 85, 75, 255, "left");
      label("Tap to add", sx + 18, 154, 11, 120, 110, 100, 255, "left");

      const chipW = 98, chipH = 48, chipGap = 8;
      const chipX0 = sx + 74;
      game.cards.forEach((c, i) => {
        const data = CardsData[c.cat];
        const item = data.items[c.item];
        const bx = chipX0 + i * (chipW + chipGap);
        const col = CAT_COLORS[c.cat];
        drawSketchBox(bx, 120, chipW, chipH, 10, 252, 249, 242, 255, (i + 1) * 13, false);
        drawImg(item.id, bx + 18, 144, 30, 1, 1);
        label(cleanItemLabel(item.name), bx + 36, 144, 10.5, INK_R, INK_G, INK_B, 255, "left");
        zone("card" + (i + 1), bx, 120, chipW, chipH);
      });

      drawSketchBox(sx, 188, sw, 46, 14, 252, 243, 215, 255, 61, false);
      label(`Mandatory Twist: "${SENTENCES[game.sentenceIdx]}"`, VW / 2, 211, 15, INK_R, INK_G, INK_B, 255, "center");

      const px = sx, py = 246, pw = sw, ph = 380;
      drawSketchBox(px, py, pw, ph, 22, PAPER_R, PAPER_G, PAPER_B, 255, 31, true);
      fillRect(px + 3, py + 3, pw - 6, 40, 18, 166, 110, 218, 240);
      fillRect(px + 3, py + 43, pw - 6, 2, 0, INK_R, INK_G, INK_B, 220);
      label("STORY NOTEPAD (Tap to type with your keyboard)", px + 20, py + 23, 15, INK_R, INK_G, INK_B, 255, "left");

      const blink = (Math.floor(game.time * 2) % 2 === 0) ? "|" : "";
      const displayStr = game.storyBody + blink;
      if (game.storyBody.length === 0) {
        label("Tap here to start typing, or tap Quick Insert chips below...", px + 24, py + 74, 16, 130, 120, 110, 255, "left");
      } else {
        drawParagraph(displayStr, px + 24, py + 70, 56, 26, 18, INK_R, INK_G, INK_B, 255, "left");
      }

      zone("notepad_tap", px, py, pw, ph);

      label(`${game.storyBody.length} / 420 chars`, px + 24, py + ph - 22, 14, 110, 100, 90, 255, "left");
      pill("txt_clear", "Clear Text", px + pw - 75, py + ph - 22, 110, 30, 238, 108, 104, INK_R, INK_G, INK_B, 14);

      const qy = 642;
      label("QUICK INSERT CHIPS (1-Tap Add):", sx + 10, qy + 14, 16, 255, 255, 255, 245, "left");

      const stColW = (sw - 12) / 2;
      STORY_STARTERS.forEach((st, i) => {
        const colIdx = i % 2;
        const rowIdx = Math.floor(i / 2);
        const bx = sx + colIdx * (stColW + 12);
        const by = qy + 36 + rowIdx * 42;
        pill("ins_start_" + (i + 1), "+ " + st, bx + stColW / 2, by + 18, stColW, 34, 252, 249, 242, INK_R, INK_G, INK_B, 13.5);
      });

      pill("ins_twist", "+ Insert Twist Sentence", VW / 2, qy + 144, sw, 38, 246, 188, 68, INK_R, INK_G, INK_B, 15);

      pill("go_showcase", "Create Story Card (Save / Share) ->", VW / 2, 850, 560, 58, 112, 196, 132, INK_R, INK_G, INK_B, 20);
      pill("back_cards", "<- Back to Cards", VW / 2, 922, 340, 46, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17);
    }

    function drawWriteStudio() {
      if (isPortrait) drawWriteStudioPortrait();
      else drawWriteStudioLandscape();
    }

    // --- SHOWCASE CARD ---
    function drawShowcaseCardLandscape() {
      const px = 90, py = 42, pw = 1100, ph = 565;
      drawSketchBox(px, py, pw, ph, 28, PAPER_R, PAPER_G, PAPER_B, 255, 91, true);
      fillRect(px + 4, py + 4, pw - 8, 82, 24, 166, 110, 218, 240);
      fillRect(px + 4, py + 86, pw - 8, 2.5, 0, INK_R, INK_G, INK_B, 230);

      drawImg("ui_title", px + 115, py + 45, 108, 1, 1);
      label("MY TELL ME! STORY SHOWCASE", VW / 2 + 20, py + 32, 25, INK_R, INK_G, INK_B, 255, "center");
      label("5 Random Cards  -  1 Secret Twist Sentence  -  1 Original Story", VW / 2 + 20, py + 62, 15, 45, 35, 55, 255, "center");
      drawImg("lvl_guru", px + pw - 70, py + 45, 56, 1, 1);

      const cy = py + 168;
      const cw = 178, ch = 126, gap = 20;
      const totalW = 5 * cw + 4 * gap;
      const x0 = (VW - totalW) / 2;
      game.cards.forEach((c, i) => {
        const cx = x0 + i * (cw + gap) + cw / 2;
        const col = CAT_COLORS[c.cat];
        const data = CardsData[c.cat];
        const item = data.items[c.item];
        drawSketchBox(cx - cw / 2, cy - ch / 2, cw, ch, 16, 252, 249, 242, 255, (i + 1) * 17, false);
        fillRect(cx - cw / 2 + 3, cy - ch / 2 + 3, cw - 6, 24, 12, col[0], col[1], col[2], 235);
        drawImg(item.id, cx - 44, cy + 10, 58, 1, 1);
        label(data.label.toUpperCase(), cx, cy - ch / 2 + 15, 12, INK_R, INK_G, INK_B, 255, "center");
        label(cleanItemLabel(item.name), cx + 28, cy + 14, 12, INK_R, INK_G, INK_B, 255, "center");
      });

      drawSketchBox(px + 56, py + 246, pw - 112, 42, 14, 246, 188, 68, 255, 61, false);
      label(`MANDATORY TWIST:  "${SENTENCES[game.sentenceIdx]}"`, VW / 2, py + 267, 16, INK_R, INK_G, INK_B, 255, "center");

      drawSketchBox(px + 56, py + 302, pw - 112, 230, 18, 252, 249, 242, 255, 73, false);
      let finalStory = game.storyBody;
      if (finalStory.length === 0) {
        finalStory = `Once upon a time, our hero stumbled into an unexpected adventure! Just when everything seemed lost, someone whispered: "${SENTENCES[game.sentenceIdx]}" And from that moment on, nothing was ever the same.`;
      }
      drawParagraph(finalStory, px + 84, py + 336, 78, 30, 19, INK_R, INK_G, INK_B, 255, "left");

      label("Take a screenshot of this card to save & share your story with friends!", VW / 2, py + ph - 16, 14, 95, 85, 75, 255, "center");

      pill("edit_story", "<- Edit Story", VW / 2 - 260, 662, 210, 46, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17);
      pill("celebrate", "Celebrate!", VW / 2, 662, 210, 46, 246, 188, 68, INK_R, INK_G, INK_B, 17);
      pill("other", "Try Another Level", VW / 2 + 260, 662, 230, 46, 112, 196, 132, INK_R, INK_G, INK_B, 17);
    }

    function drawShowcaseCardPortrait() {
      const px = 24, py = 36, pw = VW - 48, ph = 1000;
      drawSketchBox(px, py, pw, ph, 26, PAPER_R, PAPER_G, PAPER_B, 255, 91, true);
      fillRect(px + 4, py + 4, pw - 8, 80, 22, 166, 110, 218, 240);
      fillRect(px + 4, py + 84, pw - 8, 2.5, 0, INK_R, INK_G, INK_B, 230);

      drawImg("ui_title", px + 80, py + 44, 96, 1, 1);
      label("MY STORY SHOWCASE", VW / 2 + 10, py + 34, 24, INK_R, INK_G, INK_B, 255, "center");
      label("5 Random Cards  -  1 Secret Twist  -  1 Tale", VW / 2 + 10, py + 62, 14, 45, 35, 55, 255, "center");
      drawImg("lvl_guru", px + pw - 55, py + 44, 52, 1, 1);

      const cy = py + 155;
      const cw = 116, ch = 90, gap = 8;
      const totalW = 5 * cw + 4 * gap;
      const x0 = (VW - totalW) / 2;
      game.cards.forEach((c, i) => {
        const cx = x0 + i * (cw + gap) + cw / 2;
        const col = CAT_COLORS[c.cat];
        const data = CardsData[c.cat];
        const item = data.items[c.item];
        drawSketchBox(cx - cw / 2, cy - ch / 2, cw, ch, 14, 252, 249, 242, 255, (i + 1) * 17, false);
        fillRect(cx - cw / 2 + 3, cy - ch / 2 + 3, cw - 6, 22, 10, col[0], col[1], col[2], 235);
        drawImg(item.id, cx - 30, cy + 10, 48, 1, 1);
        label(data.label.toUpperCase(), cx, cy - ch / 2 + 14, 11, INK_R, INK_G, INK_B, 255, "center");
        label(cleanItemLabel(item.name), cx + 22, cy + 14, 11, INK_R, INK_G, INK_B, 255, "center");
      });

      drawSketchBox(px + 24, py + 225, pw - 48, 44, 14, 246, 188, 68, 255, 61, false);
      label(`MANDATORY TWIST:  "${SENTENCES[game.sentenceIdx]}"`, VW / 2, py + 247, 15, INK_R, INK_G, INK_B, 255, "center");

      drawSketchBox(px + 24, py + 285, pw - 48, 640, 18, 252, 249, 242, 255, 73, false);
      let finalStory = game.storyBody;
      if (finalStory.length === 0) {
        finalStory = `Once upon a time, our hero stumbled into an unexpected adventure! Just when everything seemed lost, someone whispered: "${SENTENCES[game.sentenceIdx]}" And from that moment on, nothing was ever the same.`;
      }
      drawParagraph(finalStory, px + 50, py + 325, 52, 30, 20, INK_R, INK_G, INK_B, 255, "left");

      label("Take a screenshot to save & share your story!", VW / 2, py + ph - 16, 14, 95, 85, 75, 255, "center");

      pill("edit_story", "<- Edit Story", VW / 2 - 145, 1075, 250, 50, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 18);
      pill("celebrate", "Celebrate!", VW / 2 + 145, 1075, 250, 50, 246, 188, 68, INK_R, INK_G, INK_B, 18);
      pill("other", "Try Another Level", VW / 2, 1145, 360, 48, 112, 196, 132, INK_R, INK_G, INK_B, 18);
    }

    function drawShowcaseCard() {
      if (isPortrait) drawShowcaseCardPortrait();
      else drawShowcaseCardLandscape();
    }
'''

text = text[:screen_start] + new_screens_code + text[sparkles_start:]

# 6. Update render() logic to adapt to aspect ratio and portrait resolution
old_render_part = """      game.winW = cssW;
      game.winH = cssH;
      game.scale = Math.min(cssW / VW, cssH / VH);
      game.ox = (cssW - VW * game.scale) * 0.5;
      game.oy = (cssH - VH * game.scale) * 0.5;"""

new_render_part = """      isPortrait = (cssW / cssH) < 1.15;
      VW = isPortrait ? 720 : 1280;
      VH = isPortrait ? 1280 : 720;

      game.winW = cssW;
      game.winH = cssH;
      game.isPortrait = isPortrait;
      game.scale = Math.min(cssW / VW, cssH / VH);
      game.ox = (cssW - VW * game.scale) * 0.5;
      game.oy = (cssH - VH * game.scale) * 0.5;"""

text = text.replace(old_render_part, new_render_part)

# 7. Update pointerdown to handle native text input and keyboard sync
old_pointerdown_top = """    canvas.addEventListener('pointerdown', (e) => {
      if (!game.ready) return;
      const pos = getVirtualPos(e);
      const id = hit(pos);
      if (id === "") return;"""

new_pointerdown_top = """    const nativeInput = document.getElementById("native-story-input");
    if (nativeInput) {
      nativeInput.addEventListener("input", () => {
        game.storyBody = nativeInput.value.slice(0, 420);
      });
    }

    function syncNativeInput() {
      if (nativeInput && nativeInput.value !== game.storyBody) {
        nativeInput.value = game.storyBody;
      }
    }

    canvas.addEventListener('pointerdown', (e) => {
      if (!game.ready) return;
      const pos = getVirtualPos(e);
      const id = hit(pos);

      if (id === "notepad_tap" || (game.screen === "play" && game.phase === "write" && pos.y >= 240 && pos.y <= 600)) {
        if (nativeInput) {
          syncNativeInput();
          nativeInput.focus();
        }
      }

      if (id === "") return;"""

text = text.replace(old_pointerdown_top, new_pointerdown_top)

# Update appendStoryText and backspaceOneChar to sync
text = text.replace(
    'function appendStoryText(str) {\n      if (game.storyBody.length < 420) {\n        game.storyBody += str;\n      }\n    }',
    'function appendStoryText(str) {\n      if (game.storyBody.length < 420) {\n        game.storyBody += str;\n        syncNativeInput();\n      }\n    }'
)

text = text.replace(
    "chars.pop();\n        game.storyBody = chars.join('');",
    "chars.pop();\n        game.storyBody = chars.join('');\n        syncNativeInput();"
)

text = text.replace(
    'game.storyBody = "";\n        sndClick();',
    'game.storyBody = "";\n        syncNativeInput();\n        sndClick();'
)

# Write to target_path
with open(target_path, "w", encoding="utf-8") as f:
    f.write(text)

print("Responsive index.html successfully generated! Size:", len(text))
