<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover" />
  <meta name="theme-color" content="#0c4459" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <title>Tell Me! — A Storytelling Card Game</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap" rel="stylesheet">
  <style>
    @font-face {
      font-family: 'PatrickHand';
      src: url('PatrickHand-Regular.ttf') format('truetype');
      font-weight: normal;
      font-style: normal;
      font-display: swap;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-tap-highlight-color: transparent; }
    html, body {
      width: 100%;
      height: 100%;
      position: fixed;
      inset: 0;
      margin: 0;
      padding: 0;
      overflow: hidden;
      background: #0c4459;
      font-family: 'PatrickHand', 'Patrick Hand', cursive, sans-serif;
      user-select: none;
      -webkit-user-select: none;
      -webkit-touch-callout: none;
      overscroll-behavior: none;
    }
    #game-canvas {
      position: fixed;
      inset: 0;
      width: 100%;
      height: 100%;
      display: block;
      touch-action: none;
    }
    #native-story-input {
      position: fixed;
      display: none;
      z-index: 25;
      box-sizing: border-box;
      background: transparent;
      border: none;
      outline: none;
      resize: none;
      font-family: 'PatrickHand', 'Patrick Hand', cursive, sans-serif;
      color: transparent;
      caret-color: #1a1614;
      font-size: 18px;
      line-height: 26px;
      padding: 8px 12px;
      margin: 0;
      -webkit-tap-highlight-color: transparent;
    }
    #loading-screen {
      position: fixed;
      inset: 0;
      background: radial-gradient(circle at 50% 40%, #1a576e 0%, #0d2834 100%);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      z-index: 100;
      color: #fff;
      transition: opacity 0.35s ease;
    }
    #loading-screen.hidden {
      opacity: 0;
      pointer-events: none;
    }
    .spinner {
      width: 48px;
      height: 48px;
      border: 4px solid rgba(255, 255, 255, 0.2);
      border-top-color: #f6bc44;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin-bottom: 18px;
    }
    @keyframes spin { to { transform: rotate(360deg); } }
    .load-text {
      font-size: 1.6rem;
      letter-spacing: 0.5px;
      color: #fceecb;
      margin-bottom: 6px;
    }
    .load-sub {
      font-family: system-ui, -apple-system, sans-serif;
      font-size: 0.85rem;
      color: #93bed1;
    }
  </style>
</head>
<body>

  <div id="loading-screen">
    <div class="spinner"></div>
    <div class="load-text">Shuffling Story Cards...</div>
    <div class="load-sub" id="load-count">Loading assets...</div>
  </div>

  <textarea id="native-story-input" autocapitalize="sentences" autocomplete="off" spellcheck="true"></textarea>
  <canvas id="game-canvas"></canvas>

  <script>
    // --- SUBTLE WEB AUDIO SYNTHESIZER ---
    const AudioCtx = window.AudioContext || window.webkitAudioContext;
    let actx = null;
    function playBeep(freq, type, duration, vol) {
      try {
        if (!actx) actx = new AudioCtx();
        if (actx.state === 'suspended') actx.resume();
        const osc = actx.createOscillator();
        const g = actx.createGain();
        osc.type = type || 'sine';
        osc.frequency.setValueAtTime(freq, actx.currentTime);
        g.gain.setValueAtTime(vol || 0.14, actx.currentTime);
        g.gain.exponentialRampToValueAtTime(0.001, actx.currentTime + duration);
        osc.connect(g);
        g.connect(actx.destination);
        osc.start();
        osc.stop(actx.currentTime + duration);
      } catch (e) {}
    }
    function sndFlip() { playBeep(320, 'triangle', 0.08, 0.12); }
    function sndClick() { playBeep(520, 'sine', 0.06, 0.10); }
    function sndCheck() { playBeep(660, 'sine', 0.14, 0.16); setTimeout(() => playBeep(880, 'sine', 0.18, 0.16), 55); }
    function sndTwist() { playBeep(390, 'triangle', 0.22, 0.14); setTimeout(() => playBeep(580, 'triangle', 0.26, 0.16), 100); }
    function sndFanfare() { [523, 659, 783, 1046].forEach((f, i) => setTimeout(() => playBeep(f, 'triangle', 0.22, 0.15), i * 85)); }

    // --- CONSTANTS & DATA (1:1 WITH main.luau & cards_data.luau) ---
    let VW = 1280;
    let VH = 720;
    let isPortrait = false;
    const INK_R = 26, INK_G = 22, INK_B = 20;
    const PAPER_R = 246, PAPER_G = 241, PAPER_B = 229;

    const CardsData = [
      {
        label: "Character",
        items: [
          { id: "c1_alien", name: "space cat" },
          { id: "c1_astronaut", name: "astronaut" },
          { id: "c1_basketball_player", name: "basketball player" },
          { id: "c1_biography", name: "director" },
          { id: "c1_boss", name: "boss" },
          { id: "c1_dress", name: "princess" },
          { id: "c1_family", name: "family" },
          { id: "c1_festival", name: "clown" },
          { id: "c1_investigate", name: "detective" },
          { id: "c1_kick", name: "martial artist" },
          { id: "c1_kung_fu", name: "kung fu master" },
          { id: "c1_mother", name: "mother" },
          { id: "c1_pharmacist", name: "pharmacist" },
          { id: "c1_professions_and_jobs", name: "doctor" },
          { id: "c1_rasta", name: "musician" },
          { id: "c1_receptionist", name: "receptionist" },
          { id: "c1_scientist", name: "scientist" },
          { id: "c1_singer", name: "singer" },
          { id: "c1_student", name: "graduate" },
          { id: "c1_suspect", name: "suspect" },
          { id: "c1_teacher", name: "teacher" },
          { id: "c1_thief", name: "thief" },
          { id: "c1_wizards", name: "wizard" },
          { id: "c1_work", name: "architect" },
        ]
      },
      {
        label: "Place",
        items: [
          { id: "c2_01", name: "carousel" },
          { id: "c2_02", name: "theater" },
          { id: "c2_03", name: "circus" },
          { id: "c2_04", name: "haunted house" },
          { id: "c2_05", name: "tropical island" },
          { id: "c2_06", name: "castle" },
          { id: "c2_07", name: "space station" },
          { id: "c2_government", name: "courthouse" },
          { id: "c2_mortgage_loan", name: "bank vault" },
          { id: "c2_stadium", name: "stadium" },
        ]
      },
      {
        label: "Weather",
        items: [
          { id: "c3_01", name: "sunny" },
          { id: "c3_02", name: "rainbow" },
          { id: "c3_03", name: "snowy night" },
          { id: "c3_04", name: "meteor shower" },
          { id: "c3_beach", name: "beach" },
          { id: "c3_dust", name: "sandstorm" },
          { id: "c3_earthquake", name: "earthquake" },
          { id: "c3_flood", name: "flood" },
          { id: "c3_park", name: "park" },
          { id: "c3_rain", name: "rain" },
          { id: "c3_storm", name: "thunderstorm" },
          { id: "c3_sun", name: "cool sun" },
          { id: "c3_tsunami", name: "tsunami" },
          { id: "c3_war", name: "battle" },
        ]
      },
      {
        label: "Twist",
        items: [
          { id: "c4_bipolar", name: "drama masks" },
          { id: "c4_crocodile", name: "crocodile" },
          { id: "c4_death", name: "grim reaper" },
          { id: "c4_fortune_telling", name: "crystal ball" },
          { id: "c4_scorpion", name: "scorpion" },
          { id: "c4_tent", name: "campfire" },
          { id: "c4_thyroid", name: "lightning" },
          { id: "c4_unicorn", name: "unicorn" },
          { id: "c4_voodoo", name: "voodoo doll" },
          { id: "c4_whale", name: "blue whale" },
        ]
      },
      {
        label: "Object",
        items: [
          { id: "c5_construction_and_tools", name: "tools" },
          { id: "c5_evidences", name: "magnifier" },
          { id: "c5_handcuff", name: "handcuffs" },
          { id: "c5_lighter", name: "lighter" },
          { id: "c5_mat", name: "treasure map" },
          { id: "c5_mutation", name: "dna" },
          { id: "c5_scissors", name: "scissors" },
          { id: "c5_sewing_machine", name: "sewing machine" },
          { id: "c5_sundae", name: "ice cream" },
          { id: "c5_vaccine", name: "potion" },
        ]
      }
    ];

    const SENTENCES = [
      "I am from a different planet.",
      "I wish I hadn't said that.",
      "I wish it was an accident.",
      "She couldn't believe her luck!",
      "That's too bad you should have thought of that before!",
      "The shooter says goodbye to his love.",
      "There was only one way to do it.",
      "They found a dead body.",
      "What day is today?",
      "What were you thinking about?",
      "Why are your eyes so big?",
      "Would you like a bigger one?",
      "You are the weakest link! Goodbye!",
      "Hold on, I need at least a few minutes!",
    ];

    const STORY_STARTERS = [
      "Once upon a time, ",
      "Suddenly, out of nowhere, ",
      "Nobody believed it when ",
      "In the middle of the storm, ",
      "To everyone's surprise, ",
      "Finally, the secret was out: ",
    ];

    const CAT_COLORS = [
      [238, 108, 104], // Character (Warm Watercolor Coral)
      [98, 152, 224],  // Place (Cornflower Gouache Blue)
      [94, 188, 134],  // Weather (Sage Mint Watercolor Green)
      [166, 110, 218], // Twist (Lavender Violet Wash)
      [244, 154, 58],  // Object (Warm Ochre / Tangerine)
    ];

    const LEVELS = [
      {
        id: "lvl_rookie",
        name: "ROOKIE",
        tag: "LEVEL 1",
        sub: "No timer. Take your time.",
        desc: "You will be given 5 random pictures. Start telling your story whenever you feel comfortable.",
        col: [246, 194, 62],
      },
      {
        id: "lvl_expert",
        name: "EXPERT",
        tag: "LEVEL 2",
        sub: "Beat the prep clock (30/45/60s).",
        desc: "5 random pictures and three time options to set up your story before you start telling it.",
        col: [238, 138, 64],
      },
      {
        id: "lvl_master",
        name: "MASTER",
        tag: "LEVEL 3",
        sub: "Timer + Random Twist Sentence.",
        desc: "5 random pictures, prep timer, plus one secret sentence you MUST weave into your story!",
        col: [228, 98, 122],
      },
      {
        id: "lvl_guru",
        name: "GURU",
        tag: "LEVEL 4",
        sub: "Write & Showcase your story.",
        desc: "Full challenge! After unlocking your cards and twist sentence, write and frame your story card.",
        col: [162, 104, 218],
      },
    ];

    const KB_ROWS = [
      ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
      ["A", "S", "D", "F", "G", "H", "J", "K", "L", "!"],
      ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "?"],
    ];

    const BUBBLES = [
      { x: 145, y: 175, rad: 82 },
      { x: 22,  y: 145, rad: 42 },
      { x: 355, y: 265, rad: 98 },
      { x: 865, y: 475, rad: 92 },
      { x: 1095, y: 655, rad: 115 },
      { x: 1185, y: 160, rad: 54 },
    ];

    // --- GAME STATE ---
    const canvas = document.getElementById('game-canvas');
    const ctx = canvas.getContext('2d');

    const game = {
      images: {},
      screen: "hello",
      screenT: 0,
      time: 0,
      levelIdx: 0, // 0..3
      phase: "cards", // "cards" | "write" | "showcase"
      cards: [],
      zones: [],
      sparkles: [],
      hover: "",
      scale: 1,
      isPortrait: false,
      cardsFlippedCount: 0,
      cardsUsedCount: 0,
      ox: 0,
      oy: 0,
      winW: window.innerWidth,
      winH: window.innerHeight,
      toast: "",
      toastT: 0,
      timerMax: 0,
      timerLeft: 0,
      timerRunning: false,
      sentenceIdx: 0,
      sentenceOpen: false,
      storyBody: "",
      shiftOn: true,
      showHelp: false,
      ready: false,
      lastTime: performance.now(),
    };

    // --- ASSET + FONT PRELOADER ---
    const imageIds = [
      "ui_bg", "ui_title", "ui_home", "ui_repeat", "ui_question",
      "lvl_rookie", "lvl_expert", "lvl_master", "lvl_guru"
    ];
    CardsData.forEach(cat => cat.items.forEach(it => imageIds.push(it.id)));

    const loadCountEl = document.getElementById('load-count');
    const loadingScreen = document.getElementById('loading-screen');

    function loadImage(id) {
      return new Promise(resolve => {
        const img = new Image();
        img.onload = () => {
          game.images[id] = img;
          resolve(true);
        };
        img.onerror = () => resolve(false);
        img.src = `img/${id}.png`;
      });
    }

    async function bootstrap() {
      let done = 0;
      loadCountEl.innerText = `Loading 0 / ${imageIds.length} assets`;
      const imgPromises = imageIds.map(id =>
        loadImage(id).then(() => {
          done++;
          loadCountEl.innerText = `Loading ${done} / ${imageIds.length} assets`;
        })
      );
      const fontPromise = document.fonts ? document.fonts.ready : Promise.resolve();
      await Promise.all([...imgPromises, fontPromise]);

      for (let ci = 0; ci < 5; ci++) {
        game.cards.push({ cat: ci, item: 0, flip: 0, target: 0, used: false, pop: 0 });
      }
      dealAll();
      game.ready = true;
      loadingScreen.classList.add('hidden');
      game.lastTime = performance.now();
      requestAnimationFrame(loop);
    }

    // --- COLOR & PATH HELPERS (1:1 WITH main.luau) ---
    function rgba(r, g, b, a) {
      return `rgba(${Math.round(r)},${Math.round(g)},${Math.round(b)},${Math.max(0, Math.min(1, a / 255))})`;
    }

    function traceRoundedRect(x, y, w, h, r) {
      const cr = Math.min(r, Math.min(w, h) * 0.5);
      ctx.beginPath();
      if (cr <= 0.5) {
        ctx.rect(x, y, w, h);
        return;
      }
      ctx.moveTo(x + cr, y);
      ctx.lineTo(x + w - cr, y);
      ctx.quadraticCurveTo(x + w, y, x + w, y + cr);
      ctx.lineTo(x + w, y + h - cr);
      ctx.quadraticCurveTo(x + w, y + h, x + w - cr, y + h);
      ctx.lineTo(x + cr, y + h);
      ctx.quadraticCurveTo(x, y + h, x, y + h - cr);
      ctx.lineTo(x, y + cr);
      ctx.quadraticCurveTo(x, y, x + cr, y);
      ctx.closePath();
    }

    function fillRect(x, y, w, h, rad, r, g, b, a) {
      traceRoundedRect(x, y, w, h, rad);
      ctx.fillStyle = rgba(r, g, b, a);
      ctx.fill();
    }

    function strokeRect(x, y, w, h, rad, r, g, b, a, th) {
      traceRoundedRect(x, y, w, h, rad);
      ctx.strokeStyle = rgba(r, g, b, a);
      ctx.lineWidth = th;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.stroke();
    }

    function fillCircle(cx, cy, rad, r, g, b, a) {
      ctx.beginPath();
      ctx.arc(cx, cy, Math.max(0.1, rad), 0, Math.PI * 2);
      ctx.fillStyle = rgba(r, g, b, a);
      ctx.fill();
    }

    function strokeCircle(cx, cy, rad, r, g, b, a, th) {
      ctx.beginPath();
      ctx.arc(cx, cy, Math.max(0.1, rad), 0, Math.PI * 2);
      ctx.strokeStyle = rgba(r, g, b, a);
      ctx.lineWidth = th;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.stroke();
    }

    function drawSketchBox(x, y, w, h, rad, fr, fg, fb, fa, seed, withHatch) {
      if (w <= 0 || h <= 0) return;
      // 1. Soft dark ink wash under-shadow + diagonal hatch strokes along bottom & right edge
      if (withHatch && w > 30 && h > 24) {
        fillRect(x + 4, y + 6, w, h, rad, 10, 18, 24, 95);
        ctx.beginPath();
        const step = 8;
        const xStart = x + rad * 0.6;
        const xEnd = x + w - rad * 0.4;
        const yBot = y + h;
        let idx = 0;
        let hx = xStart;
        while (hx <= xEnd) {
          const jitter = ((idx * 17 + seed * 7) % 5) - 2;
          ctx.moveTo(hx, yBot + 1);
          ctx.lineTo(hx - 6 + jitter * 0.4, yBot + 8 + (idx % 2) * 2);
          hx += step;
          idx += 1;
        }
        let hy = y + rad * 0.8;
        while (hy <= y + h - rad * 0.5) {
          ctx.moveTo(x + w + 1, hy);
          ctx.lineTo(x + w + 7, hy + 5);
          hy += 9;
        }
        ctx.strokeStyle = rgba(INK_R, INK_G, INK_B, 175);
        ctx.lineWidth = 1.5;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.stroke();
      }

      // 2. Main watercolor/paper body fill
      fillRect(x, y, w, h, rad, fr, fg, fb, fa);

      // 3. Subtle inner highlight stroke on top-left
      if (w > 8 && h > 8) {
        strokeRect(x + 2, y + 2, w - 4, h - 4, Math.max(2, rad - 2), 255, 255, 255, 65, 1.5);
      }

      // 4. Double-pass sketchy espresso ink outline
      const ox1 = ((seed * 13) % 3) - 1;
      const oy1 = ((seed * 29) % 3) - 1;
      strokeRect(x - 1.2 + ox1 * 0.5, y - 0.8 + oy1 * 0.5, w + 2.4, h + 1.8, rad + 1, INK_R, INK_G, INK_B, 145, 1.4);
      strokeRect(x + 0.8, y + 1.1, Math.max(2, w - 0.6), Math.max(2, h - 0.8), Math.max(2, rad - 0.5), INK_R, INK_G, INK_B, 110, 1.1);
      strokeRect(x, y, w, h, rad, INK_R, INK_G, INK_B, 245, 2.4);
    }

    function drawSketchCircle(cx, cy, rad, fr, fg, fb, fa, inkAlpha) {
      if (fa > 0) {
        fillCircle(cx + 2, cy + 3, rad, 10, 18, 24, 80);
        fillCircle(cx, cy, rad, fr, fg, fb, fa);
      }
      strokeCircle(cx - 0.9, cy + 0.7, rad + 1.2, INK_R, INK_G, INK_B, Math.floor(inkAlpha * 0.55), 1.3);
      strokeCircle(cx + 0.7, cy - 0.8, Math.max(2, rad - 0.8), INK_R, INK_G, INK_B, Math.floor(inkAlpha * 0.45), 1.1);
      strokeCircle(cx, cy, rad, INK_R, INK_G, INK_B, inkAlpha, 2.3);
    }

    function drawSketchBubble(cx, cy, rad) {
      fillCircle(cx, cy, rad, 255, 255, 255, 14);
      strokeCircle(cx, cy, rad, 255, 255, 255, 78, 1.6);
      strokeCircle(cx + 2.2, cy - 1.8, rad * 0.97, 255, 255, 255, 48, 1.1);
      ctx.beginPath();
      ctx.moveTo(cx - rad * 0.55, cy - rad * 0.35);
      ctx.bezierCurveTo(
        cx - rad * 0.35, cy - rad * 0.65,
        cx - rad * 0.05, cy - rad * 0.68,
        cx + rad * 0.15, cy - rad * 0.52
      );
      ctx.strokeStyle = rgba(255, 255, 255, 95);
      ctx.lineWidth = 1.8;
      ctx.lineCap = 'round';
      ctx.stroke();
    }

    function label(str, x, y, size, cr, cg, cb, ca, align) {
      if (!str || ca <= 1) return;
      ctx.save();
      ctx.fillStyle = rgba(cr, cg, cb, Math.floor(ca));
      ctx.font = `${(size * 1.15).toFixed(2)}px 'PatrickHand', 'Patrick Hand', cursive`;
      ctx.textAlign = align || "left";
      ctx.textBaseline = "middle";
      ctx.fillText(str, x, y);
      ctx.restore();
    }

    function drawParagraph(str, x, y, maxCharsPerLine, lineH, size, cr, cg, cb, ca, align) {
      if (!str) return 0;
      const paras = str.split("\n");
      const lines = [];
      for (const p of paras) {
        const words = p.trim().length === 0 ? [""] : p.split(/\s+/);
        let cur = "";
        for (const w of words) {
          if (cur.length === 0) {
            cur = w;
          } else if ((cur.length + 1 + w.length) <= maxCharsPerLine) {
            cur = cur + " " + w;
          } else {
            lines.push(cur);
            cur = w;
          }
        }
        lines.push(cur);
      }
      for (let i = 0; i < lines.length; i++) {
        label(lines[i], x, y + i * lineH, size, cr, cg, cb, ca, align);
      }
      return lines.length;
    }

    function clamp01(v) {
      return Math.min(1, Math.max(0, v));
    }

    function easeOutBack(t) {
      const c1 = 1.70158;
      const c3 = c1 + 1;
      const u = t - 1;
      return 1 + c3 * u * u * u + c1 * u * u;
    }

    function drawImg(id, cx, cy, w, sx, opacity) {
      const img = game.images[id];
      if (!img || !img.complete || img.naturalWidth <= 0 || opacity <= 0.01) return;
      const iw = img.naturalWidth;
      const ih = img.naturalHeight;
      const k = w / Math.max(iw, ih);
      ctx.save();
      ctx.globalAlpha = opacity;
      ctx.translate(cx, cy);
      ctx.scale(k * sx, k);
      ctx.translate(-iw * 0.5, -ih * 0.5);
      ctx.drawImage(img, 0, 0, iw, ih);
      ctx.restore();
    }

    function zone(id, x, y, w, h) {
      game.zones.push({ id, x, y, w, h });
    }

    function spawnBurst(cx, cy, count) {
      for (let i = 1; i <= count; i++) {
        const ang = (i / count) * 6.28318 + Math.random() * 0.5;
        const spd = 80 + Math.random() * 180;
        const c = CAT_COLORS[i % CAT_COLORS.length];
        game.sparkles.push({
          x: cx,
          y: cy,
          vx: Math.cos(ang) * spd,
          vy: Math.sin(ang) * spd - 60,
          rad: 4 + Math.random() * 5,
          r: c[0],
          g: c[1],
          b: c[2],
          life: 0,
          maxLife: 0.7 + Math.random() * 0.5,
        });
      }
    }

    function dealCard(card, ci) {
      const list = CardsData[card.cat].items;
      const n = list.length;
      const prev = card.item;
      let pick = Math.floor(Math.random() * n);
      if (n > 1 && pick === prev) pick = (pick + 1) % n;
      card.item = pick;
      card.flip = 0;
      card.target = 0;
      card.used = false;
      card.pop = -0.07 * ci;
    }

    function dealAll() {
      game.cards.forEach((c, i) => dealCard(c, i));
      const prevS = game.sentenceIdx;
      let nextS = Math.floor(Math.random() * SENTENCES.length);
      if (SENTENCES.length > 1 && nextS === prevS) nextS = (nextS + 1) % SENTENCES.length;
      game.sentenceIdx = nextS;
      game.sentenceOpen = false;
      game.timerRunning = false;
      game.timerLeft = 0;
      game.timerMax = 0;
      game.phase = "cards";
    }

    function startLevel(idx) {
      game.levelIdx = idx;
      game.screen = "play";
      game.screenT = 0;
      dealAll();
    }

    function toast(msg) {
      game.toast = msg;
      game.toastT = 2.4;
    }

    function cleanItemLabel(raw) {
      if (/^\d+$/.test(raw)) return "SCENE";
      if (raw.length > 12) return raw.slice(0, 11).toUpperCase() + ".";
      return raw.toUpperCase();
    }

    // --- UI COMPONENTS ---
    function drawBackground() {
      const sx = VW / 1280;
      const sy = VH / 720;
      BUBBLES.forEach((b, i) => {
        const idx = i + 1;
        const dx = Math.sin(game.time * 0.35 + idx * 1.4) * 12;
        const dy = Math.cos(game.time * 0.28 + idx * 1.9) * 9;
        drawSketchBubble(b.x * sx + dx, b.y * sy + dy, b.rad * (isPortrait ? 1.15 : 1.0));
      });
    }

    function pill(id, text, cx, cy, w, h, cr, cg, cb, tr, tg, tb, fsize) {
      const hov = game.hover === id;
      const s = hov ? 1.05 : 1.0;
      const ww = w * s;
      const hh = h * s;
      const seed = id.charCodeAt(0) || 7;
      drawSketchBox(cx - ww / 2, cy - hh / 2, ww, hh, hh * 0.48, cr, cg, cb, 255, seed, true);
      label(text, cx, cy, (fsize || 18) * s, tr, tg, tb, 255, "center");
      zone(id, cx - w / 2, cy - h / 2, w, h);
    }

    // --- SINGLE CARD RENDERER (UNIFIED FOR PORTRAIT & LANDSCAPE) ---
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
      zone("home", 15, 12, 66, 62);

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
      zone("home", 12, 16, 68, 64);

      drawImg(lv.id, 106, 48, 50, 1, 1);
      label(`${lv.tag}`, 142, 38, 19, 255, 255, 255, 255, "left");
      label(lv.name, 142, 64, 15, 235, 245, 250, 235, "left");

      pill("shuffle", "New Cards", VW - 175, 48, 120, 44, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 15);
      pill("other", "Levels", VW - 58, 48, 92, 44, 246, 188, 68, INK_R, INK_G, INK_B, 15);
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
            zone("twist_next", rx, barY - 62, rw, 124);
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
        // Level 2 Timer
        const barY = 175;
        drawSketchBox(36, barY - 60, 648, 120, 22, PAPER_R, PAPER_G, PAPER_B, 255, 41, true);
        if (game.timerMax === 0) {
          label("Prep time challenge:", VW / 2, barY - 24, 19, INK_R, INK_G, INK_B, 255, "center");
          pill("tm_30", "30 sec.", VW / 2 - 175, barY + 22, 140, 44, 94, 188, 134, INK_R, INK_G, INK_B, 16);
          pill("tm_45", "45 sec.", VW / 2, barY + 22, 140, 44, 98, 152, 224, INK_R, INK_G, INK_B, 16);
          pill("tm_60", "60 sec.", VW / 2 + 175, barY + 22, 140, 44, 246, 188, 68, INK_R, INK_G, INK_B, 16);
        } else if (game.timerLeft > 0) {
          const secs = Math.ceil(game.timerLeft);
          label(`PREP TIME: ${secs}s LEFT`, 190, barY - 20, 20, 215, 75, 70, 255, "center");
          const pw = 340, px = 54;
          drawSketchBox(px, barY + 12, pw, 16, 8, 232, 226, 212, 255, 12, false);
          const ratio = clamp01(game.timerLeft / game.timerMax);
          fillRect(px + 2, barY + 14, Math.max(12, (pw - 4) * ratio), 12, 6, 94, 188, 134, 255);
          pill("tm_skip", "I'm Ready!", 550, barY + 6, 180, 48, 246, 188, 68, INK_R, INK_G, INK_B, 16);
        } else {
          label("Time is up! Let's hear your story!", 240, barY, 20, 45, 135, 85, 255, "center");
          pill("tm_reset", "Reset Timer", 550, barY, 165, 46, 246, 188, 68, INK_R, INK_G, INK_B, 16);
        }
      } else if (game.levelIdx >= 2) {
        // Level 3 & 4 Twist Sentence
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
          pill("twist_next", "New Sentence", rx + rw - 92, barY - 32, 146, 36, 246, 188, 68, INK_R, INK_G, INK_B, 14);
          zone("twist_next", rx, barY - 60, rw, 120);
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
        pill("flip_all", "Flip All", VW / 2 - 130, footY + 135, 230, 50, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 18);
        pill("shuffle", "New Cards", VW / 2 + 130, footY + 135, 230, 50, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 18);
      } else {
        pill("flip_all", "Flip All", VW / 2 - 135, footY + 65, 240, 52, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 18);
        pill("mark_done", "It Is Done!", VW / 2 + 135, footY + 65, 240, 52, 112, 196, 132, INK_R, INK_G, INK_B, 18);
        pill("shuffle", "Shuffle 5 New Cards", VW / 2, footY + 135, 340, 48, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17);
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
      label("STORY NOTEPAD (Tap to type your story)", px + 20, py + 23, 15, INK_R, INK_G, INK_B, 255, "left");

      const blink = (Math.floor(game.time * 2) % 2 === 0) ? "|" : "";
      const displayStr = game.storyBody + blink;
      if (game.storyBody.length === 0) {
        label("Tap here to start typing, or tap Quick Insert chips below...", px + 24, py + 74, 16, 130, 120, 110, 255, "left");
      } else {
        drawParagraph(displayStr, px + 24, py + 70, 56, 26, 18, INK_R, INK_G, INK_B, 255, "left");
      }

      zone("notepad_tap", px, py, pw, ph);

      label(`${game.storyBody.length} / 420 chars`, px + 24, py + ph - 22, 14, 110, 100, 90, 255, "left");
      pill("txt_clear", "Clear Text", px + pw - 75, py + ph - 22, 110, 32, 238, 108, 104, INK_R, INK_G, INK_B, 14);

      const qy = 642;
      label("QUICK INSERT CHIPS (1-Tap Add):", sx + 10, qy + 14, 16, 255, 255, 255, 245, "left");

      const stColW = (sw - 12) / 2;
      STORY_STARTERS.forEach((st, i) => {
        const colIdx = i % 2;
        const rowIdx = Math.floor(i / 2);
        const bx = sx + colIdx * (stColW + 12);
        const by = qy + 36 + rowIdx * 42;
        pill("ins_start_" + (i + 1), "+ " + st, bx + stColW / 2, by + 18, stColW, 36, 252, 249, 242, INK_R, INK_G, INK_B, 13.5);
      });

      pill("ins_twist", "+ Insert Twist Sentence", VW / 2, qy + 144, sw, 40, 246, 188, 68, INK_R, INK_G, INK_B, 15);

      pill("go_showcase", "Create Story Card (Save / Share) ->", VW / 2, 850, 560, 58, 112, 196, 132, INK_R, INK_G, INK_B, 20);
      pill("back_cards", "<- Back to Cards", VW / 2, 924, 340, 48, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17);
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

      pill("edit_story", "<- Edit Story", VW / 2 - 260, 662, 210, 48, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17);
      pill("celebrate", "Celebrate!", VW / 2, 662, 210, 48, 246, 188, 68, INK_R, INK_G, INK_B, 17);
      pill("other", "Try Another Level", VW / 2 + 260, 662, 230, 48, 112, 196, 132, INK_R, INK_G, INK_B, 17);
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
    function drawSparkles() {
      game.sparkles.forEach(sp => {
        const a = clamp01(1 - sp.life / sp.maxLife);
        fillCircle(sp.x, sp.y, sp.rad * a, sp.r, sp.g, sp.b, Math.floor(255 * a));
      });
    }

    // --- MAIN TICK & RENDER ---
    function loop(now) {
      requestAnimationFrame(loop);
      if (!game.ready) return;
      const dt = Math.min((now - game.lastTime) / 1000, 0.1);
      game.lastTime = now;

      game.time += dt;
      game.screenT += dt;
      game.toastT = Math.max(0, game.toastT - dt);

      if (game.timerRunning && game.timerLeft > 0) {
        game.timerLeft = Math.max(0, game.timerLeft - dt);
        if (game.timerLeft <= 0) {
          game.timerRunning = false;
          sndFanfare();
          spawnBurst(VW / 2, 180, 22);
        }
      }

      game.cards.forEach(c => {
        c.pop += dt;
        if (c.flip < c.target) c.flip = Math.min(c.target, c.flip + dt / 0.42);
        else if (c.flip > c.target) c.flip = Math.max(c.target, c.flip - dt / 0.42);
      });

      for (let i = game.sparkles.length - 1; i >= 0; i--) {
        const sp = game.sparkles[i];
        sp.life += dt;
        sp.x += sp.vx * dt;
        sp.y += sp.vy * dt;
        sp.vy += 240 * dt;
        if (sp.life >= sp.maxLife) game.sparkles.splice(i, 1);
      }

      render();
    }

    function render() {
      const dpr = window.devicePixelRatio || 1;
      const cssW = window.innerWidth;
      const cssH = window.innerHeight;
      const targetW = Math.round(cssW * dpr);
      const targetH = Math.round(cssH * dpr);

      if (canvas.width !== targetW || canvas.height !== targetH) {
        canvas.width = targetW;
        canvas.height = targetH;
      }

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';

      isPortrait = (cssW / cssH) < 1.15;
      VW = isPortrait ? 720 : 1280;
      VH = isPortrait ? 1280 : 720;

      game.winW = cssW;
      game.winH = cssH;
      game.isPortrait = isPortrait;
      game.scale = Math.min(cssW / VW, cssH / VH);
      game.ox = (cssW - VW * game.scale) * 0.5;
      game.oy = (cssH - VH * game.scale) * 0.5;

      const nativeInput = document.getElementById("native-story-input");
      if (nativeInput) {
        if (game.screen === "play" && game.phase === "write") {
          const sw = isPortrait ? (VW - 48) : 720;
          const sx = isPortrait ? 24 : 48;
          const sy = isPortrait ? 246 : 184;
          const sh = isPortrait ? 380 : 310;
          const topPad = isPortrait ? 52 : 48;
          const botPad = isPortrait ? 122 : 98;
          nativeInput.style.display = "block";
          nativeInput.style.left = (game.ox + (sx + 20) * game.scale) + "px";
          nativeInput.style.top = (game.oy + (sy + topPad) * game.scale) + "px";
          nativeInput.style.width = ((sw - 40) * game.scale) + "px";
          nativeInput.style.height = ((sh - topPad - botPad) * game.scale) + "px";
          nativeInput.style.pointerEvents = "auto";
        } else {
          nativeInput.style.display = "none";
          nativeInput.style.pointerEvents = "none";
          if (document.activeElement === nativeInput) {
            nativeInput.blur();
          }
        }
      }

      // Full-bleed petrol-teal base + watercolor background cover scaling
      ctx.fillStyle = "#0e4d64";
      ctx.fillRect(0, 0, cssW, cssH);

      const bgImg = game.images["ui_bg"];
      if (bgImg && bgImg.complete && bgImg.naturalWidth > 0 && cssW > 0 && cssH > 0) {
        ctx.save();
        const s = Math.max(cssW / bgImg.naturalWidth, cssH / bgImg.naturalHeight);
        const bgOx = (cssW - bgImg.naturalWidth * s) * 0.5;
        const bgOy = (cssH - bgImg.naturalHeight * s) * 0.5;
        ctx.drawImage(bgImg, bgOx, bgOy, bgImg.naturalWidth * s, bgImg.naturalHeight * s);
        ctx.restore();
      }

      // Centered 1280x720 artboard
      game.zones = [];
      ctx.save();
      ctx.translate(game.ox, game.oy);
      ctx.scale(game.scale, game.scale);

      drawBackground();

      if (game.screen === "hello") {
        drawHello();
        if (game.showHelp) drawHelpModal();
      } else {
        if (game.phase === "write") drawWriteStudio();
        else if (game.phase === "showcase") drawShowcaseCard();
        else drawPlayStage();
      }

      drawSparkles();

      if (game.toastT > 0) {
        const toastY = isPortrait ? 108 : 662;
        const toastW = isPortrait ? 560 : 460;
        drawSketchBox(VW / 2 - toastW / 2, toastY - 22, toastW, 46, 23, PAPER_R, PAPER_G, PAPER_B, 255, 99, false);
        label(game.toast, VW / 2, toastY + 1, 18, INK_R, INK_G, INK_B, 255, "center");
      }

      ctx.restore();
    }

    // --- INPUT HANDLING (ROBUST CROSS-DEVICE NORMALIZATION) ---
    function getVirtualPos(e) {
      const rect = canvas.getBoundingClientRect();
      let clientX = e.clientX;
      let clientY = e.clientY;
      if (clientX === undefined) {
        const t = (e.touches && e.touches[0]) || (e.changedTouches && e.changedTouches[0]);
        if (t) {
          clientX = t.clientX;
          clientY = t.clientY;
        } else {
          clientX = 0;
          clientY = 0;
        }
      }

      // Self-normalizing against DOM bounds to prevent any viewport/toolbar scaling drift
      const normX = (clientX - rect.left) / (rect.width || 1);
      const normY = (clientY - rect.top) / (rect.height || 1);

      const cssX = normX * game.winW;
      const cssY = normY * game.winH;

      return {
        x: (cssX - game.ox) / game.scale,
        y: (cssY - game.oy) / game.scale,
      };
    }

    function hit(pos) {
      // 10px generous padding in virtual coordinates for comfortable, forgiving touch on phones
      const pad = isPortrait ? 10 : 4;
      for (let i = game.zones.length - 1; i >= 0; i--) {
        const z = game.zones[i];
        if (
          pos.x >= z.x - pad &&
          pos.x <= z.x + z.w + pad &&
          pos.y >= z.y - pad &&
          pos.y <= z.y + z.h + pad
        ) {
          return z.id;
        }
      }
      return "";
    }

    canvas.addEventListener('pointermove', (e) => {
      if (!game.ready) return;
      const id = hit(getVirtualPos(e));
      game.hover = id;
      canvas.style.cursor = id ? "pointer" : "default";
    });

    function appendStoryText(str) {
      if (game.storyBody.length < 420) {
        game.storyBody += str;
        syncNativeInput();
      }
    }

    function backspaceOneChar() {
      const chars = Array.from(game.storyBody);
      if (chars.length > 0) {
        chars.pop();
        game.storyBody = chars.join('');
        syncNativeInput();
      }
    }

    const nativeInput = document.getElementById("native-story-input");
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

    function handleInputDown(e) {
      if (!game.ready) return;
      const pos = getVirtualPos(e);
      const id = hit(pos);

      if (id === "notepad_tap" || (game.screen === "play" && game.phase === "write" && pos.y >= 240 && pos.y <= (isPortrait ? 550 : 430) && id !== "txt_clear")) {
        if (nativeInput) {
          syncNativeInput();
          nativeInput.focus();
        }
      }

      if (id === "") return;

      if (id === "btn_help") {
        game.showHelp = true;
        sndClick();
      } else if (id === "close_help") {
        game.showHelp = false;
        sndClick();
      } else if (id === "home" || id === "other") {
        game.screen = "hello";
        game.screenT = 0;
        game.showHelp = false;
        sndClick();
      } else if (id === "shuffle") {
        dealAll();
        toast("5 new story cards dealt!");
        sndFlip();
      } else if (id === "flip_all") {
        game.cards.forEach(c => { c.target = 1; });
        sndFlip();
      } else if (id === "mark_done") {
        game.cards.forEach(c => { c.target = 1; c.used = true; });
        spawnBurst(VW / 2, 360, 32);
        toast("Awesome story! Try another level or shuffle new cards!");
        sndFanfare();
      } else if (id === "tm_30" || id === "tm_45" || id === "tm_60") {
        const sec = parseInt(id.slice(3), 10);
        game.timerMax = sec;
        game.timerLeft = sec;
        game.timerRunning = true;
        sndClick();
      } else if (id === "tm_skip") {
        game.timerLeft = 0;
        game.timerRunning = false;
        game.cards.forEach(c => { c.target = 1; });
        spawnBurst(VW / 2, 220, 20);
        sndFlip();
      } else if (id === "tm_reset") {
        game.timerMax = 0;
        game.timerLeft = 0;
        game.timerRunning = false;
        sndClick();
      } else if (id === "twist_reveal") {
        game.sentenceOpen = true;
        spawnBurst(920, 175, 24);
        sndTwist();
      } else if (id === "twist_next") {
        game.sentenceIdx = (game.sentenceIdx + 1) % SENTENCES.length;
        spawnBurst(920, 175, 16);
        sndTwist();
      } else if (id === "go_write") {
        game.cards.forEach(c => { c.target = 1; });
        game.sentenceOpen = true;
        game.phase = "write";
        sndClick();
      } else if (id === "back_cards" || id === "edit_story") {
        game.phase = (id === "edit_story") ? "write" : "cards";
        sndClick();
      } else if (id === "go_showcase") {
        game.phase = "showcase";
        spawnBurst(VW / 2, 260, 36);
        sndFanfare();
      } else if (id === "celebrate") {
        spawnBurst(VW / 2, 300, 40);
        sndFanfare();
      } else if (id === "txt_clear") {
        game.storyBody = "";
        syncNativeInput();
        sndClick();
      } else if (id === "ins_twist") {
        const sp = (game.storyBody.length > 0 && !game.storyBody.endsWith(" ")) ? " " : "";
        appendStoryText(`${sp}"${SENTENCES[game.sentenceIdx]}" `);
        sndTwist();
      } else if (id.startsWith("ins_start_")) {
        const idx = (parseInt(id.slice(10), 10) || 1) - 1;
        appendStoryText(STORY_STARTERS[idx]);
        sndClick();
      } else if (id === "key_space") {
        appendStoryText(" ");
        sndClick();
      } else if (id === "key_back") {
        backspaceOneChar();
        sndClick();
      } else if (id === "key_shift") {
        game.shiftOn = !game.shiftOn;
        sndClick();
      } else if (id.startsWith("key_")) {
        const ch = id.slice(4);
        appendStoryText(ch);
        if (game.shiftOn) game.shiftOn = false;
        sndClick();
      } else if (id.startsWith("card")) {
        const i = (parseInt(id.slice(4), 10) || 1) - 1;
        const c = game.cards[i];
        if (!c) return;
        if (game.phase === "write") {
          const item = CardsData[c.cat].items[c.item];
          const word = cleanItemLabel(item.name).toLowerCase();
          appendStoryText(word + " ");
          sndClick();
        } else {
          if (c.target < 0.5) {
            c.target = 1;
            sndFlip();
          } else if (c.flip > 0.85) {
            c.used = !c.used;
            if (c.used) {
              spawnBurst(VW / 2, 380, 14);
              sndCheck();
            } else {
              sndClick();
            }
          }
        }
      } else if (id.startsWith("lv")) {
        const idx = (parseInt(id.slice(2), 10) || 1) - 1;
        startLevel(idx);
        sndClick();
      }
    }

    let lastDownTs = 0;
    function onUniversalDown(e) {
      const now = Date.now();
      if (now - lastDownTs < 45) return;
      lastDownTs = now;
      handleInputDown(e);
    }

    canvas.addEventListener('pointerdown', onUniversalDown);
    canvas.addEventListener('touchstart', onUniversalDown, { passive: true });

    window.addEventListener('keydown', (e) => {
      if (!game.ready) return;
      if (e.key === "Escape" && game.showHelp) {
        game.showHelp = false;
        e.preventDefault();
        return;
      }
      if (game.screen === "play" && game.phase === "write") {
        if (e.key === "Backspace") {
          backspaceOneChar();
          sndClick();
          e.preventDefault();
        } else if (e.key === "Enter") {
          appendStoryText("\n");
          sndClick();
          e.preventDefault();
        } else if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
          appendStoryText(e.key);
          sndClick();
          e.preventDefault();
        }
      }
    });

    bootstrap();
  </script>
</body>
</html>
