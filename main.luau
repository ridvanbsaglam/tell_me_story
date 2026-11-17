--!strict
local CardsData = require('cards_data')

local VW = 1280
local VH = 720
local DEBUG_MODE = 0
-- 0: Normal (Hello)
-- 1: Level 1 (Rookie) closed cards
-- 2: Level 1 (Rookie) flipped + used cards (matching reference mockup)
-- 3: Level 2 (Expert) time selection & running timer
-- 4: Level 3 (Master) twist sentence revealed
-- 5: Level 4 (Guru) story writing studio
-- 6: Level 4 (Guru) showcase / screenshot card
-- 7: How to Play modal

type HitZone = { id: string, x: number, y: number, w: number, h: number }

type Card = {
    cat: number,
    item: number,
    flip: number,
    target: number,
    used: boolean,
    pop: number,
}

type Sparkle = {
    x: number,
    y: number,
    vx: number,
    vy: number,
    rad: number,
    r: number,
    g: number,
    b: number,
    life: number,
    maxLife: number,
}

type Game = {
    context: Context?,
    bold: Font?,
    medium: Font?,
    images: { [string]: Image? },
    sampler: ImageSampler?,
    screen: string,
    screenT: number,
    time: number,
    levelIdx: number,
    phase: string,
    cards: { Card },
    zones: { HitZone },
    sparkles: { Sparkle },
    hover: string,
    scale: number,
    ox: number,
    oy: number,
    winW: number,
    winH: number,
    toast: string,
    toastT: number,
    timerMax: number,
    timerLeft: number,
    timerRunning: boolean,
    sentenceIdx: number,
    sentenceOpen: boolean,
    sentenceAnim: number,
    storyTitle: string,
    storyBody: string,
    shiftOn: boolean,
    showHelp: boolean,
    pendingKey: string?,
}

local SENTENCES = {
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
}

local STORY_STARTERS = {
    "Once upon a time, ",
    "Suddenly, out of nowhere, ",
    "Nobody believed it when ",
    "In the middle of the storm, ",
    "To everyone's surprise, ",
    "Finally, the secret was out: ",
}

-- Muted Watercolor & Gouache Category Palette (matching reference mockup)
local CAT_COLORS = {
    { 238, 108, 104 }, -- Character (Warm Watercolor Coral)
    { 98, 152, 224 },  -- Place (Cornflower Gouache Blue)
    { 94, 188, 134 },  -- Weather (Sage Mint Watercolor Green)
    { 166, 110, 218 }, -- Twist (Lavender Violet Wash)
    { 244, 154, 58 },  -- Object (Warm Ochre / Tangerine)
}

local LEVELS = {
    {
        id = "lvl_rookie",
        name = "ROOKIE",
        tag = "LEVEL 1",
        sub = "No timer. Take your time.",
        desc = "You will be given 5 random pictures. Start telling your story whenever you feel comfortable.",
        col = { 246, 194, 62 },
    },
    {
        id = "lvl_expert",
        name = "EXPERT",
        tag = "LEVEL 2",
        sub = "Beat the prep clock (30/45/60s).",
        desc = "5 random pictures and three time options to set up your story before you start telling it.",
        col = { 238, 138, 64 },
    },
    {
        id = "lvl_master",
        name = "MASTER",
        tag = "LEVEL 3",
        sub = "Timer + Random Twist Sentence.",
        desc = "5 random pictures, prep timer, plus one secret sentence you MUST weave into your story!",
        col = { 228, 98, 122 },
    },
    {
        id = "lvl_guru",
        name = "GURU",
        tag = "LEVEL 4",
        sub = "Write & Showcase your story.",
        desc = "Full challenge! After unlocking your cards and twist sentence, write and frame your story card.",
        col = { 162, 104, 218 },
    },
}

-- Paper & Ink tokens
local INK_R, INK_G, INK_B = 26, 22, 20
local PAPER_R, PAPER_G, PAPER_B = 246, 241, 229

local function fill(r: number, g: number, b: number, a: number): Paint
    return Paint.with({ style = 'fill', color = Color.rgba(r, g, b, a) })
end

local function stroke(r: number, g: number, b: number, a: number, th: number): Paint
    return Paint.with({ style = 'stroke', color = Color.rgba(r, g, b, a), thickness = th, cap = 'round', join = 'round' })
end

local function rrect(x: number, y: number, w: number, h: number, r: number): Path
    local p = Path.new()
    local cr = math.min(r, math.min(w, h) * 0.5)
    if cr <= 0.5 then
        p:moveTo(Vector.xy(x, y))
        p:lineTo(Vector.xy(x + w, y))
        p:lineTo(Vector.xy(x + w, y + h))
        p:lineTo(Vector.xy(x, y + h))
        p:close()
        return p
    end
    local k = cr * 0.55228475
    p:moveTo(Vector.xy(x + cr, y))
    p:lineTo(Vector.xy(x + w - cr, y))
    p:cubicTo(Vector.xy(x + w - cr + k, y), Vector.xy(x + w, y + cr - k), Vector.xy(x + w, y + cr))
    p:lineTo(Vector.xy(x + w, y + h - cr))
    p:cubicTo(Vector.xy(x + w, y + h - cr + k), Vector.xy(x + w - cr + k, y + h), Vector.xy(x + w - cr, y + h))
    p:lineTo(Vector.xy(x + cr, y + h))
    p:cubicTo(Vector.xy(x + cr - k, y + h), Vector.xy(x, y + h - cr + k), Vector.xy(x, y + h - cr))
    p:lineTo(Vector.xy(x, y + cr))
    p:cubicTo(Vector.xy(x, y + cr - k), Vector.xy(x + cr - k, y), Vector.xy(x + cr, y))
    p:close()
    return p
end

local function drawRect(r: Renderer, x: number, y: number, w: number, h: number, rad: number, paint: Paint)
    r:drawPath(rrect(x, y, w, h, rad), paint)
end

local function drawCircle(r: Renderer, cx: number, cy: number, rad: number, paint: Paint)
    local p = Path.new()
    local k = rad * 0.55228475
    p:moveTo(Vector.xy(cx, cy - rad))
    p:cubicTo(Vector.xy(cx + k, cy - rad), Vector.xy(cx + rad, cy - k), Vector.xy(cx + rad, cy))
    p:cubicTo(Vector.xy(cx + rad, cy + k), Vector.xy(cx + k, cy + rad), Vector.xy(cx, cy + rad))
    p:cubicTo(Vector.xy(cx - k, cy + rad), Vector.xy(cx - rad, cy + k), Vector.xy(cx - rad, cy))
    p:cubicTo(Vector.xy(cx - rad, cy - k), Vector.xy(cx - k, cy - rad), Vector.xy(cx, cy - rad))
    p:close()
    r:drawPath(p, paint)
end

-- Hand-drawn sketchy double-pass rounded rectangle with diagonal cross-hatch shadow
local function drawSketchBox(
    r: Renderer,
    x: number,
    y: number,
    w: number,
    h: number,
    rad: number,
    fr: number,
    fg: number,
    fb: number,
    fa: number,
    seed: number,
    withHatch: boolean
)
    -- 1. Soft dark ink wash under-shadow + diagonal hatch strokes along bottom & right edge
    if withHatch and w > 30 and h > 24 then
        drawRect(r, x + 4, y + 6, w, h, rad, fill(10, 18, 24, 95))
        local hp = Path.new()
        local step = 8
        local xStart = x + rad * 0.6
        local xEnd = x + w - rad * 0.4
        local yBot = y + h
        local idx = 0
        local hx = xStart
        while hx <= xEnd do
            local jitter = ((idx * 17 + seed * 7) % 5) - 2
            hp:moveTo(Vector.xy(hx, yBot + 1))
            hp:lineTo(Vector.xy(hx - 6 + jitter * 0.4, yBot + 8 + (idx % 2) * 2))
            hx += step
            idx += 1
        end
        -- Right edge hatch marks
        local hy = y + rad * 0.8
        while hy <= y + h - rad * 0.5 do
            hp:moveTo(Vector.xy(x + w + 1, hy))
            hp:lineTo(Vector.xy(x + w + 7, hy + 5))
            hy += 9
        end
        r:drawPath(hp, stroke(INK_R, INK_G, INK_B, 175, 1.5))
    end

    -- 2. Main watercolor/paper body fill
    drawRect(r, x, y, w, h, rad, fill(fr, fg, fb, fa))

    -- 3. Subtle inner highlight stroke on top-left to give hand-painted gouache edge
    drawRect(r, x + 2, y + 2, w - 4, h - 4, math.max(2, rad - 2), stroke(255, 255, 255, 65, 1.5))

    -- 4. Double-pass sketchy espresso ink outline (slightly offset wobble pass + main crisp pass)
    local ox1 = ((seed * 13) % 3) - 1
    local oy1 = ((seed * 29) % 3) - 1
    drawRect(r, x - 1.2 + ox1 * 0.5, y - 0.8 + oy1 * 0.5, w + 2.4, h + 1.8, rad + 1, stroke(INK_R, INK_G, INK_B, 145, 1.4))
    drawRect(r, x + 0.8, y + 1.1, w - 0.6, h - 0.8, math.max(2, rad - 0.5), stroke(INK_R, INK_G, INK_B, 110, 1.1))
    drawRect(r, x, y, w, h, rad, stroke(INK_R, INK_G, INK_B, 245, 2.4))
end

-- Hand-drawn sketchy circle (for Home button, badges, checkmarks, bubbles)
local function drawSketchCircle(r: Renderer, cx: number, cy: number, rad: number, fr: number, fg: number, fb: number, fa: number, inkAlpha: number)
    if fa > 0 then
        drawCircle(r, cx + 2, cy + 3, rad, fill(10, 18, 24, 80))
        drawCircle(r, cx, cy, rad, fill(fr, fg, fb, fa))
    end
    drawCircle(r, cx - 0.9, cy + 0.7, rad + 1.2, stroke(INK_R, INK_G, INK_B, math.floor(inkAlpha * 0.55), 1.3))
    drawCircle(r, cx + 0.7, cy - 0.8, math.max(2, rad - 0.8), stroke(INK_R, INK_G, INK_B, math.floor(inkAlpha * 0.45), 1.1))
    drawCircle(r, cx, cy, rad, stroke(INK_R, INK_G, INK_B, inkAlpha, 2.3))
end

-- Hand-drawn chalk/ink bubble ring on watercolor background
local function drawSketchBubble(r: Renderer, cx: number, cy: number, rad: number)
    drawCircle(r, cx, cy, rad, fill(255, 255, 255, 14))
    drawCircle(r, cx, cy, rad, stroke(255, 255, 255, 78, 1.6))
    drawCircle(r, cx + 2.2, cy - 1.8, rad * 0.97, stroke(255, 255, 255, 48, 1.1))
    -- Little curved shine arc inside bubble
    local p = Path.new()
    p:moveTo(Vector.xy(cx - rad * 0.55, cy - rad * 0.35))
    p:cubicTo(
        Vector.xy(cx - rad * 0.35, cy - rad * 0.65),
        Vector.xy(cx - rad * 0.05, cy - rad * 0.68),
        Vector.xy(cx + rad * 0.15, cy - rad * 0.52)
    )
    r:drawPath(p, stroke(255, 255, 255, 95, 1.8))
end

local function label(r: Renderer, font: Font?, str: string, x: number, y: number, size: number, cr: number, cg: number, cb: number, ca: number, align: string)
    if font == nil or str == "" or ca <= 1 then return end
    local t = Text.new()
    -- PatrickHand renders slightly smaller than Montserrat at the same pt size, so boost by 1.15x
    t:append(str, { font = font, size = size * 1.15, paint = fill(cr, cg, cb, math.floor(ca)) })
    local bMin, bMax = t:bounds()
    local bw = bMax.x - bMin.x
    local bh = bMax.y - bMin.y
    local tx = x - bMin.x
    if align == "center" then tx = x - (bMin.x + bw * 0.5) elseif align == "right" then tx = x - bMax.x end
    local ty = y - (bMin.y + bh * 0.5)
    r:save()
    r:transform(Mat2D.withTranslation(tx, ty))
    t:draw(r)
    r:restore()
end

local function drawParagraph(r: Renderer, font: Font?, str: string, x: number, y: number, maxCharsPerLine: number, lineH: number, size: number, cr: number, cg: number, cb: number, ca: number, align: string): number
    if font == nil or str == "" then return 0 end
    local words: { string } = {}
    for w in string.gmatch(str, "%S+") do
        table.insert(words, tostring(w))
    end
    local lines: { string } = {}
    local cur: string = ""
    for _, w in ipairs(words) do
        if string.len(cur) == 0 then
            cur = w
        elseif (string.len(cur) + 1 + string.len(w)) <= maxCharsPerLine then
            cur = cur .. " " .. w
        else
            table.insert(lines, cur)
            cur = w
        end
    end
    if string.len(cur) > 0 then table.insert(lines, cur) end
    for i, ln in ipairs(lines) do
        label(r, font, ln, x, y + (i - 1) * lineH, size, cr, cg, cb, ca, align)
    end
    return #lines
end

local function clamp01(v: number): number
    return math.min(1, math.max(0, v))
end

local function easeOutBack(t: number): number
    local c1 = 1.70158
    local c3 = c1 + 1
    local u = t - 1
    return 1 + c3 * u * u * u + c1 * u * u
end

local function _lerp(a: number, b: number, t: number): number
    return a + (b - a) * t
end

local function drawImg(self: Game, r: Renderer, id: string, cx: number, cy: number, w: number, sx: number, opacity: number)
    local img = self.images[id]
    local sampler = self.sampler
    if img == nil or sampler == nil or img.width <= 0 or opacity <= 0.01 then return end
    local k = w / math.max(img.width, img.height)
    r:save()
    r:transform(Mat2D.withTranslation(cx, cy) * Mat2D.withScale(k * sx, k) * Mat2D.withTranslation(-img.width * 0.5, -img.height * 0.5))
    r:drawImage(img, sampler, 'srcOver', opacity)
    r:restore()
end

local function zone(self: Game, id: string, x: number, y: number, w: number, h: number)
    table.insert(self.zones, { id = id, x = x, y = y, w = w, h = h })
end

local function spawnBurst(self: Game, cx: number, cy: number, count: number)
    local cols = CAT_COLORS
    for i = 1, count do
        local ang = (i / count) * 6.28318 + math.random() * 0.5
        local spd = 80 + math.random() * 180
        local c = cols[(i % #cols) + 1]
        table.insert(self.sparkles, {
            x = cx,
            y = cy,
            vx = math.cos(ang) * spd,
            vy = math.sin(ang) * spd - 60,
            rad = 4 + math.random() * 5,
            r = c[1],
            g = c[2],
            b = c[3],
            life = 0,
            maxLife = 0.7 + math.random() * 0.5,
        })
    end
end

local function dealCard(card: Card, ci: number)
    local list = CardsData[card.cat].items
    local n = #list
    local prev = card.item
    local pick = math.random(1, n)
    if n > 1 and pick == prev then pick = (pick % n) + 1 end
    card.item = pick
    card.flip = 0
    card.target = 0
    card.used = false
    card.pop = -0.07 * ci
end

local function dealAll(self: Game)
    for i, c in ipairs(self.cards) do
        dealCard(c, i - 1)
    end
    local prevS = self.sentenceIdx
    local nextS = math.random(1, #SENTENCES)
    if #SENTENCES > 1 and nextS == prevS then nextS = (nextS % #SENTENCES) + 1 end
    self.sentenceIdx = nextS
    self.sentenceOpen = false
    self.sentenceAnim = 0
    self.timerRunning = false
    self.timerLeft = 0
    self.timerMax = 0
    self.phase = "cards"
end

local function startLevel(self: Game, idx: number)
    self.levelIdx = idx
    self.screen = "play"
    self.screenT = 0
    dealAll(self)
end

local function toast(self: Game, msg: string)
    self.toast = msg
    self.toastT = 2.4
end

local function cleanItemLabel(raw: string): string
    if string.match(raw, "^%d+$") then
        return "SCENE"
    end
    if string.len(raw) > 12 then
        return string.upper(string.sub(raw, 1, 11)) .. "."
    end
    return string.upper(raw)
end

---------------------------------------------------------------- WATERCOLOR & SKETCH UI HELPERS
local function drawBackground(self: Game, r: Renderer)
    -- Hand-drawn sketchy soap bubbles drifting gently across the watercolor canvas
    local bubbles = {
        { x = 145, y = 175, rad = 82 },
        { x = 22,  y = 145, rad = 42 },
        { x = 355, y = 265, rad = 98 },
        { x = 865, y = 475, rad = 92 },
        { x = 1095, y = 655, rad = 115 },
        { x = 1185, y = 160, rad = 54 },
    }
    for i, b in ipairs(bubbles) do
        local dx = math.sin(self.time * 0.35 + i * 1.4) * 12
        local dy = math.cos(self.time * 0.28 + i * 1.9) * 9
        drawSketchBubble(r, b.x + dx, b.y + dy, b.rad)
    end
end

-- Hand-drawn sketchy pill button with double-pass ink outline & diagonal hatch shadow
local function pill(self: Game, r: Renderer, id: string, text: string, cx: number, cy: number, w: number, h: number, cr: number, cg: number, cb: number, tr: number, tg: number, tb: number, fsize: number?)
    local hov = self.hover == id
    local s = hov and 1.05 or 1.0
    local ww = w * s
    local hh = h * s
    local seed = string.byte(id, 1) or 7
    drawSketchBox(r, cx - ww / 2, cy - hh / 2, ww, hh, hh * 0.48, cr, cg, cb, 255, seed, true)
    label(r, self.bold, text, cx, cy, (fsize or 18) * s, tr, tg, tb, 255, "center")
    zone(self, id, cx - w / 2, cy - h / 2, w, h)
end

---------------------------------------------------------------- HELLO SCREEN
local function drawHello(self: Game, r: Renderer)
    local t = self.screenT
    local ts = easeOutBack(clamp01(t / 0.65))
    local bob = math.sin(self.time * 1.8) * 5
    drawImg(self, r, "ui_title", VW / 2, 128 + bob, 310 * ts, 1, clamp01(t / 0.3))

    pill(self, r, "btn_help", "?  How to Play", VW - 125, 44, 195, 46, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17)

    label(r, self.medium, "Choose a difficulty level and unleash your storytelling imagination!", VW / 2, 282, 22, 255, 255, 255, 245 * clamp01((t - 0.25) / 0.4), "center")

    local cw, ch, gap = 254, 314, 26
    local total = 4 * cw + 3 * gap
    local x0 = (VW - total) / 2
    for i, lv in ipairs(LEVELS) do
        local p = easeOutBack(clamp01((t - 0.30 - 0.09 * (i - 1)) / 0.50))
        local cx = x0 + (i - 1) * (cw + gap) + cw / 2
        local cy = 492
        local hov = self.hover == "lv" .. i
        local lift = hov and -10 or 0
        local sc = p * (hov and 1.04 or 1.0)
        local w = cw * sc
        local h = ch * sc

        drawSketchBox(r, cx - w / 2, cy - h / 2 + lift, w, h, 24 * sc, PAPER_R, PAPER_G, PAPER_B, 255, i * 19, true)

        -- Watercolor top header strip inside level card
        drawRect(r, cx - w / 2 + 4, cy - h / 2 + 4 + lift, w - 8, 36 * sc, 18 * sc, fill(lv.col[1], lv.col[2], lv.col[3], 235))
        drawRect(r, cx - w / 2 + 3, cy - h / 2 + 36 * sc + lift, w - 6, 2, 0, fill(INK_R, INK_G, INK_B, 210))
        label(r, self.bold, lv.tag, cx, cy - h / 2 + 22 * sc + lift, 14 * sc, INK_R, INK_G, INK_B, 255, "center")

        drawImg(self, r, lv.id, cx, cy - 24 + lift, 136 * sc, 1, 1)
        label(r, self.bold, lv.name, cx, cy + 74 + lift, 24 * sc, INK_R, INK_G, INK_B, 255, "center")
        label(r, self.medium, lv.sub, cx, cy + 102 + lift, 14 * sc, 75, 70, 65, 255, "center")

        -- Sketchy Play button inside card
        local btnCol = lv.col
        drawSketchBox(r, cx - 74 * sc, cy + 118 * sc + lift, 148 * sc, 30 * sc, 15 * sc, btnCol[1], btnCol[2], btnCol[3], 255, i * 31, false)
        label(r, self.bold, "PLAY NOW", cx, cy + 133 * sc + lift, 13 * sc, INK_R, INK_G, INK_B, 255, "center")

        zone(self, "lv" .. i, cx - cw / 2, cy - ch / 2, cw, ch)
    end

    label(r, self.medium, "Created by Ridvan Saglam  -  Rive Hand-Drawn Edition", VW / 2, 692, 15, 255, 255, 255, 200, "center")
end

---------------------------------------------------------------- HOW TO PLAY MODAL
local function drawHelpModal(self: Game, r: Renderer)
    drawRect(r, 0, 0, VW, VH, 0, fill(6, 22, 32, 205))
    local mw, mh = 920, 545
    local mx, my = (VW - mw) / 2, (VH - mh) / 2
    drawSketchBox(r, mx, my, mw, mh, 26, PAPER_R, PAPER_G, PAPER_B, 255, 77, true)
    drawRect(r, mx + 4, my + 4, mw - 8, 68, 22, fill(246, 194, 62, 240))
    drawRect(r, mx + 4, my + 70, mw - 8, 2.5, 0, fill(INK_R, INK_G, INK_B, 220))
    label(r, self.bold, "HOW TO PLAY TELL ME!", VW / 2, my + 38, 26, INK_R, INK_G, INK_B, 255, "center")

    label(r, self.medium, "Flip 5 random cards and weave them into one creative story!", VW / 2, my + 105, 18, 55, 50, 45, 255, "center")

    for i, lv in ipairs(LEVELS) do
        local ry = my + 142 + (i - 1) * 76
        drawSketchBox(r, mx + 36, ry, mw - 72, 64, 16, 252, 249, 242, 255, i * 11, false)
        drawRect(r, mx + 40, ry + 4, 12, 56, 6, fill(lv.col[1], lv.col[2], lv.col[3], 255))
        drawImg(self, r, lv.id, mx + 86, ry + 32, 46, 1, 1)
        label(r, self.bold, lv.tag .. " - " .. lv.name, mx + 126, ry + 22, 17, INK_R, INK_G, INK_B, 255, "left")
        label(r, self.medium, lv.desc, mx + 126, ry + 45, 15, 75, 70, 65, 255, "left")
    end

    pill(self, r, "close_help", "Got it, let's play!", VW / 2, my + mh - 42, 240, 48, 246, 194, 62, INK_R, INK_G, INK_B, 19)
end

---------------------------------------------------------------- HEADER BAR
local function drawTopBar(self: Game, r: Renderer)
    local lv = LEVELS[self.levelIdx]
    drawRect(r, 0, 0, VW, 86, 0, fill(6, 36, 48, 95))
    -- Sketchy bottom divider line under header bar
    drawRect(r, 0, 85, VW, 2, 0, fill(INK_R, INK_G, INK_B, 175))
    drawRect(r, 0, 87, VW, 1, 0, fill(255, 255, 255, 45))

    -- Hand-drawn sketchy Home Circle button
    drawSketchCircle(r, 48, 43, 25, PAPER_R, PAPER_G, PAPER_B, 255, 245)
    drawImg(self, r, "ui_home", 48, 43, 25, 1, 1)
    zone(self, "home", 20, 15, 56, 56)

    -- Level Hat Icon + Hand-drawn Title
    drawImg(self, r, lv.id, 114, 43, 56, 1, 1)
    label(r, self.bold, lv.tag .. " - " .. lv.name, 156, 33, 26, 255, 255, 255, 255, "left")
    label(r, self.medium, lv.sub, 156, 59, 15, 235, 245, 250, 235, "left")

    -- Right action pills (Cream "New Cards" + Warm Ochre "Try Another Level")
    pill(self, r, "shuffle", "New Cards", VW - 360, 43, 155, 44, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17)
    pill(self, r, "other", "Try Another Level", VW - 145, 43, 235, 44, 246, 188, 68, INK_R, INK_G, INK_B, 17)
end

---------------------------------------------------------------- CARDS ROW (SKETCHBOOK STYLE)
local function drawCardsRow(self: Game, r: Renderer, cy: number, scaleMult: number): (number, number)
    local cardW = 194 * scaleMult
    local cardH = 260 * scaleMult
    local gapx = 24 * scaleMult
    local total = 5 * cardW + 4 * gapx
    local x0 = (VW - total) / 2
    local used, flipped = 0, 0

    for i, c in ipairs(self.cards) do
        if c.target > 0.5 then flipped += 1 end
        if c.used then used += 1 end

        local cx = x0 + (i - 1) * (cardW + gapx) + cardW / 2
        local pop = easeOutBack(clamp01(c.pop / 0.50))
        if c.pop > 0 then
            local hov = self.hover == "card" .. i
            local lift = hov and -8 or 0
            local flipP = c.flip
            local sx = math.abs(math.cos(math.pi * flipP))
            local front = flipP > 0.5
            local sc = pop * (hov and 1.04 or 1.0)
            local w = cardW * sc * math.max(sx, 0.001)
            local h = cardH * sc
            local col = CAT_COLORS[c.cat]
            local data = CardsData[c.cat]
            local cxLeft = cx - w / 2
            local cyTop = cy - h / 2 + lift

            if not front then
                -- Sketchy Card Back with watercolor wash & inner dashed/double ink frame
                drawSketchBox(r, cxLeft, cyTop, w, h, 20 * sc, col[1], col[2], col[3], 255, i * 23, true)
                if sx > 0.35 then
                    drawRect(r, cxLeft + 10 * sx, cyTop + 10, w - 20 * sx, h - 20, 14 * sc, stroke(PAPER_R, PAPER_G, PAPER_B, 195, 2.2))
                    drawRect(r, cxLeft + 12 * sx, cyTop + 12, w - 24 * sx, h - 24, 12 * sc, stroke(INK_R, INK_G, INK_B, 140, 1.4))
                    label(r, self.bold, "?", cx, cy - 10 * scaleMult + lift, 92 * sc * sx * scaleMult, PAPER_R, PAPER_G, PAPER_B, 255 * sx, "center")
                    label(r, self.bold, string.upper(data.label), cx, cy + 82 * scaleMult + lift, 16 * sc * scaleMult, INK_R, INK_G, INK_B, 255 * sx, "center")
                end
            else
                -- Sketchy Warm Cream Card Front (matching uploaded reference mockup!)
                drawSketchBox(r, cxLeft, cyTop, w, h, 20 * sc, PAPER_R, PAPER_G, PAPER_B, 255, i * 29, true)

                -- Top Watercolor Category Banner + sketchy ink separator line
                local banH = 36 * sc * scaleMult
                drawRect(r, cxLeft + 3 * sx, cyTop + 3, w - 6 * sx, banH, 16 * sc, fill(col[1], col[2], col[3], 240))
                -- Watercolor highlight streak on banner
                drawRect(r, cxLeft + 10 * sx, cyTop + 6, (w - 20 * sx) * 0.65, 6 * sc, 3, fill(255, 255, 255, 75))
                -- Sketchy ink line under banner
                drawRect(r, cxLeft + 2 * sx, cyTop + banH + 1, w - 4 * sx, 2.2, 0, fill(INK_R, INK_G, INK_B, 235))
                drawRect(r, cxLeft + 6 * sx, cyTop + banH + 3.5, w - 12 * sx, 1.0, 0, fill(INK_R, INK_G, INK_B, 115))

                if sx > 0.3 then
                    label(r, self.bold, string.upper(data.label), cx, cyTop + banH * 0.52, 15 * scaleMult, INK_R, INK_G, INK_B, 255 * sx, "center")
                    local item = data.items[c.item]
                    drawImg(self, r, item.id, cx, cy + 4 * scaleMult + lift, 132 * sc * scaleMult, sx, c.used and 0.55 or 1)
                    label(r, self.bold, cleanItemLabel(item.name), cx, cy + 96 * scaleMult + lift, 14 * scaleMult, INK_R, INK_G, INK_B, 255 * sx * (c.used and 0.6 or 1), "center")
                end

                -- Hand-drawn Green Checkmark Badge when card is marked used
                if c.used and sx > 0.3 then
                    local bx = cx + cardW / 2 - 26 * scaleMult
                    local by = cy - cardH / 2 + 58 * scaleMult + lift
                    drawSketchCircle(r, bx, by, 18 * scaleMult, 112, 196, 132, 255, 245)
                    local p = Path.new()
                    p:moveTo(Vector.xy(bx - 7 * scaleMult, by + 1))
                    p:lineTo(Vector.xy(bx - 2 * scaleMult, by + 6 * scaleMult))
                    p:lineTo(Vector.xy(bx + 8 * scaleMult, by - 6 * scaleMult))
                    r:drawPath(p, stroke(PAPER_R, PAPER_G, PAPER_B, 255, 3.8))
                    r:drawPath(p, stroke(INK_R, INK_G, INK_B, 220, 1.6))
                end
            end
            zone(self, "card" .. i, cx - cardW / 2, cy - cardH / 2, cardW, cardH)
        end
    end
    return flipped, used
end

---------------------------------------------------------------- TIMER + TWIST CONTROLS (Levels 1..4)
local function drawPlayStage(self: Game, r: Renderer)
    drawTopBar(self, r)

    local hasTopPanel = self.levelIdx >= 2
    local cardsY = hasTopPanel and 425 or 355
    local cardsScale = hasTopPanel and 0.92 or 1.0
    local flipped, used = drawCardsRow(self, r, cardsY, cardsScale)

    if self.levelIdx >= 2 then
        local barY = 175
        if self.levelIdx == 2 then
            drawSketchBox(r, VW / 2 - 360, barY - 62, 720, 124, 22, PAPER_R, PAPER_G, PAPER_B, 255, 41, true)
            if self.timerMax == 0 then
                label(r, self.bold, "How much time do you need to get ready?", VW / 2, barY - 26, 20, INK_R, INK_G, INK_B, 255, "center")
                pill(self, r, "tm_30", "30 sec.", VW / 2 - 180, barY + 24, 145, 44, 94, 188, 134, INK_R, INK_G, INK_B, 17)
                pill(self, r, "tm_45", "45 sec.", VW / 2, barY + 24, 145, 44, 98, 152, 224, INK_R, INK_G, INK_B, 17)
                pill(self, r, "tm_60", "60 sec.", VW / 2 + 180, barY + 24, 145, 44, 246, 188, 68, INK_R, INK_G, INK_B, 17)
            elseif self.timerLeft > 0 then
                local secs = math.ceil(self.timerLeft)
                label(r, self.bold, "PREP TIME: " .. tostring(secs) .. " SECONDS LEFT", VW / 2 - 110, barY - 22, 21, 215, 75, 70, 255, "center")
                local pw = 420
                local px = VW / 2 - 320
                drawSketchBox(r, px, barY + 8, pw, 18, 9, 232, 226, 212, 255, 12, false)
                local ratio = clamp01(self.timerLeft / self.timerMax)
                drawRect(r, px + 2, barY + 10, math.max(14, (pw - 4) * ratio), 14, 7, fill(94, 188, 134, 255))
                label(r, self.medium, "Ready early? Skip the countdown!", px + pw / 2, barY + 42, 14, 85, 80, 75, 255, "center")
                pill(self, r, "tm_skip", "I'm Ready! Start Now", VW / 2 + 215, barY + 6, 220, 48, 246, 188, 68, INK_R, INK_G, INK_B, 17)
            else
                label(r, self.bold, "Time is up! Let's hear your story now!", VW / 2 - 90, barY, 22, 45, 135, 85, 255, "center")
                pill(self, r, "tm_reset", "Reset Timer", VW / 2 + 230, barY, 165, 42, 246, 188, 68, INK_R, INK_G, INK_B, 16)
            end
        else
            local lx = 76
            local lw = 540
            drawSketchBox(r, lx, barY - 62, lw, 124, 22, PAPER_R, PAPER_G, PAPER_B, 255, 53, true)
            if self.timerMax == 0 then
                label(r, self.bold, "1. Choose your prep timer:", lx + lw / 2, barY - 26, 18, INK_R, INK_G, INK_B, 255, "center")
                pill(self, r, "tm_30", "30 sec.", lx + 110, barY + 22, 125, 42, 94, 188, 134, INK_R, INK_G, INK_B, 16)
                pill(self, r, "tm_45", "45 sec.", lx + 270, barY + 22, 125, 42, 98, 152, 224, INK_R, INK_G, INK_B, 16)
                pill(self, r, "tm_60", "60 sec.", lx + 430, barY + 22, 125, 42, 246, 188, 68, INK_R, INK_G, INK_B, 16)
            elseif self.timerLeft > 0 then
                local secs = math.ceil(self.timerLeft)
                label(r, self.bold, "PREP TIMER: " .. tostring(secs) .. "s", lx + 165, barY - 20, 20, 215, 75, 70, 255, "center")
                local pw = 290
                drawSketchBox(r, lx + 24, barY + 12, pw, 16, 8, 232, 226, 212, 255, 19, false)
                drawRect(r, lx + 26, barY + 14, math.max(12, (pw - 4) * clamp01(self.timerLeft / self.timerMax)), 12, 6, fill(94, 188, 134, 255))
                pill(self, r, "tm_skip", "I'm Ready!", lx + 425, barY + 4, 170, 44, 246, 188, 68, INK_R, INK_G, INK_B, 16)
            else
                label(r, self.bold, "Prep complete! Tell your story!", lx + 195, barY, 19, 45, 135, 85, 255, "center")
                pill(self, r, "tm_reset", "Reset", lx + 450, barY, 120, 40, 246, 188, 68, INK_R, INK_G, INK_B, 15)
            end

            local rx = 644
            local rw = 560
            drawSketchBox(r, rx, barY - 62, rw, 124, 22, 252, 243, 215, 255, 67, true)
            if not self.sentenceOpen then
                drawSketchCircle(r, rx + 68, barY, 38, 246, 188, 68, 255, 245)
                label(r, self.bold, "?", rx + 68, barY, 42, INK_R, INK_G, INK_B, 255, "center")
                label(r, self.bold, "2. Secret Twist Sentence!", rx + 130, barY - 18, 19, INK_R, INK_G, INK_B, 255, "left")
                label(r, self.medium, "Tap to reveal the sentence you MUST use!", rx + 130, barY + 12, 15, 95, 80, 60, 255, "left")
                zone(self, "twist_reveal", rx, barY - 62, rw, 124)
            else
                drawSketchBox(r, rx + 18, barY - 46, 138, 26, 13, 238, 108, 104, 255, 3, false)
                label(r, self.bold, "TWIST SENTENCE", rx + 87, barY - 33, 12, INK_R, INK_G, INK_B, 255, "center")
                label(r, self.bold, '"' .. SENTENCES[self.sentenceIdx] .. '"', rx + rw / 2, barY + 8, 19, INK_R, INK_G, INK_B, 255, "center")
                pill(self, r, "twist_next", "New Sentence", rx + rw - 88, barY - 33, 138, 28, 246, 188, 68, INK_R, INK_G, INK_B, 13)
            end
        end
    end

    local footY = 608
    local msg = "Let's pick our cards to start with! Tap each card to flip it."
    if flipped == 5 and used < 5 then
        msg = "When a card is used in your story, tap on it to mark it done (" .. tostring(used) .. "/5)."
    elseif used == 5 then
        if self.levelIdx == 4 then
            msg = "All 5 cards used! Ready to write and frame your story?"
        else
            msg = "Excellent! You used all 5 cards! Why don't you try another level now?"
        end
    end
    label(r, self.medium, msg, VW / 2, footY, 20, 255, 255, 255, 245, "center")

    if self.levelIdx == 4 then
        pill(self, r, "go_write", "Write Your Story Now  ->", VW / 2 - 150, 666, 280, 50, 246, 188, 68, INK_R, INK_G, INK_B, 18)
        pill(self, r, "flip_all", "Flip All Cards", VW / 2 + 155, 666, 220, 50, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 18)
    else
        pill(self, r, "flip_all", "Flip All Cards", VW / 2 - 145, 666, 235, 50, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 18)
        pill(self, r, "mark_done", "It Is Done!", VW / 2 + 145, 666, 235, 50, 112, 196, 132, INK_R, INK_G, INK_B, 18)
    end
end

---------------------------------------------------------------- LEVEL 4: WRITE STUDIO
local KB_ROWS = {
    { "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P" },
    { "A", "S", "D", "F", "G", "H", "J", "K", "L", "!" },
    { "Z", "X", "C", "V", "B", "N", "M", ",", ".", "?" },
}

local function drawWriteStudio(self: Game, r: Renderer)
    drawTopBar(self, r)

    drawSketchBox(r, 48, 96, VW - 96, 74, 18, PAPER_R, PAPER_G, PAPER_B, 255, 17, true)
    label(r, self.bold, "YOUR STORY ELEMENTS:", 72, 120, 13, 95, 85, 75, 255, "left")
    label(r, self.bold, 'Twist: "' .. SENTENCES[self.sentenceIdx] .. '"', 72, 146, 15, INK_R, INK_G, INK_B, 255, "left")

    for i, c in ipairs(self.cards) do
        local data = CardsData[c.cat]
        local item = data.items[c.item]
        local bx = 540 + (i - 1) * 138
        local col = CAT_COLORS[c.cat]
        drawSketchBox(r, bx, 104, 128, 58, 12, 252, 249, 242, 255, i * 13, false)
        drawImg(self, r, item.id, bx + 28, 133, 42, 1, 1)
        label(r, self.bold, data.label, bx + 54, 124, 12, col[1], col[2], col[3], 255, "left")
        label(r, self.medium, cleanItemLabel(item.name), bx + 54, 142, 11, INK_R, INK_G, INK_B, 255, "left")
        zone(self, "card" .. i, bx, 104, 128, 58)
    end

    local px, py, pw, ph = 48, 184, 720, 310
    drawSketchBox(r, px, py, pw, ph, 22, PAPER_R, PAPER_G, PAPER_B, 255, 31, true)
    drawRect(r, px + 3, py + 3, pw - 6, 40, 18, fill(166, 110, 218, 240))
    drawRect(r, px + 3, py + 43, pw - 6, 2, 0, fill(INK_R, INK_G, INK_B, 220))
    label(r, self.bold, "WRITE YOUR STORY BELOW (Type directly with your keyboard, or click chips & cards)", px + 22, py + 23, 15, INK_R, INK_G, INK_B, 255, "left")

    local blink = (math.floor(self.time * 2) % 2 == 0) and "|" or ""
    local displayStr = self.storyBody .. blink
    if #self.storyBody == 0 then
        label(r, self.medium, "Type directly with your keyboard, tap any Story Starter on the right, or click cards...", px + 24, py + 74, 16, 130, 120, 110, 255, "left")
    else
        drawParagraph(r, self.medium, displayStr, px + 24, py + 70, 62, 26, 18, INK_R, INK_G, INK_B, 255, "left")
    end

    label(r, self.medium, tostring(#self.storyBody) .. " chars", px + 24, py + ph - 22, 14, 110, 100, 90, 255, "left")
    pill(self, r, "txt_clear", "Clear Text", px + pw - 80, py + ph - 24, 120, 32, 238, 108, 104, INK_R, INK_G, INK_B, 14)

    local rx, ry, rw, rh = 788, 184, 444, 310
    drawSketchBox(r, rx, ry, rw, rh, 22, PAPER_R, PAPER_G, PAPER_B, 255, 43, true)
    label(r, self.bold, "QUICK INSERT CHIPS (1-Click Add)", rx + 22, ry + 26, 16, INK_R, INK_G, INK_B, 255, "left")

    for i, st in ipairs(STORY_STARTERS) do
        local cy = ry + 58 + (i - 1) * 34
        pill(self, r, "ins_start_" .. i, "+ " .. st, rx + rw / 2, cy, rw - 36, 28, 252, 249, 242, INK_R, INK_G, INK_B, 14)
    end
    pill(self, r, "ins_twist", '+ Insert Twist Sentence', rx + rw / 2, ry + 272, rw - 36, 34, 246, 188, 68, INK_R, INK_G, INK_B, 15)

    local ky = 510
    for rIdx, row in ipairs(KB_ROWS) do
        local kw, kh, kgap = 54, 42, 8
        local rowW = #row * kw + (#row - 1) * kgap
        local kx0 = 48 + (720 - rowW) / 2
        local curY = ky + (rIdx - 1) * (kh + 8)
        for cIdx, ch in ipairs(row) do
            local labelCh = self.shiftOn and ch or string.lower(ch)
            local kcx = kx0 + (cIdx - 1) * (kw + kgap) + kw / 2
            pill(self, r, "key_" .. labelCh, labelCh, kcx, curY + kh / 2, kw, kh, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17)
        end
    end

    pill(self, r, "key_shift", self.shiftOn and "SHIFT (ON)" or "shift", 115, 672, 130, 40, self.shiftOn and 246 or 232, self.shiftOn and 188 or 226, self.shiftOn and 68 or 212, INK_R, INK_G, INK_B, 15)
    pill(self, r, "key_space", "SPACE", 395, 672, 390, 40, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 16)
    pill(self, r, "key_back", "BACKSPACE", 680, 672, 150, 40, 238, 108, 104, INK_R, INK_G, INK_B, 15)

    pill(self, r, "back_cards", "<- Back to Cards", 1010, 555, 440, 48, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17)
    pill(self, r, "go_showcase", "Create Story Card (Share / Screenshot)", 1010, 625, 440, 60, 112, 196, 132, INK_R, INK_G, INK_B, 18)
end

---------------------------------------------------------------- LEVEL 4: SHOWCASE CARD
local function drawShowcaseCard(self: Game, r: Renderer)
    local px, py, pw, ph = 90, 42, 1100, 565
    drawSketchBox(r, px, py, pw, ph, 28, PAPER_R, PAPER_G, PAPER_B, 255, 91, true)
    drawRect(r, px + 4, py + 4, pw - 8, 82, 24, fill(166, 110, 218, 240))
    drawRect(r, px + 4, py + 86, pw - 8, 2.5, 0, fill(INK_R, INK_G, INK_B, 230))

    drawImg(self, r, "ui_title", px + 115, py + 45, 108, 1, 1)
    label(r, self.bold, "MY TELL ME! STORY SHOWCASE", VW / 2 + 20, py + 32, 25, INK_R, INK_G, INK_B, 255, "center")
    label(r, self.medium, "5 Random Cards  -  1 Secret Twist Sentence  -  1 Original Story", VW / 2 + 20, py + 62, 15, 45, 35, 55, 255, "center")
    drawImg(self, r, "lvl_guru", px + pw - 70, py + 45, 56, 1, 1)

    local cy = py + 168
    local cw, ch, gap = 178, 126, 20
    local totalW = 5 * cw + 4 * gap
    local x0 = (VW - totalW) / 2
    for i, c in ipairs(self.cards) do
        local cx = x0 + (i - 1) * (cw + gap) + cw / 2
        local col = CAT_COLORS[c.cat]
        local data = CardsData[c.cat]
        local item = data.items[c.item]
        drawSketchBox(r, cx - cw / 2, cy - ch / 2, cw, ch, 16, 252, 249, 242, 255, i * 17, false)
        drawRect(r, cx - cw / 2 + 3, cy - ch / 2 + 3, cw - 6, 24, 12, fill(col[1], col[2], col[3], 235))
        drawImg(self, r, item.id, cx - 44, cy + 10, 58, 1, 1)
        label(r, self.bold, string.upper(data.label), cx, cy - ch / 2 + 15, 12, INK_R, INK_G, INK_B, 255, "center")
        label(r, self.bold, cleanItemLabel(item.name), cx + 28, cy + 14, 12, INK_R, INK_G, INK_B, 255, "center")
    end

    drawSketchBox(r, px + 56, py + 246, pw - 112, 42, 14, 246, 188, 68, 255, 61, false)
    label(r, self.bold, 'MANDATORY TWIST:  "' .. SENTENCES[self.sentenceIdx] .. '"', VW / 2, py + 267, 16, INK_R, INK_G, INK_B, 255, "center")

    drawSketchBox(r, px + 56, py + 302, pw - 112, 230, 18, 252, 249, 242, 255, 73, false)
    local finalStory = self.storyBody
    if #finalStory == 0 then
        finalStory = 'Once upon a time, our hero stumbled into an unexpected adventure! Just when everything seemed lost, someone whispered: "' .. SENTENCES[self.sentenceIdx] .. '" And from that moment on, nothing was ever the same.'
    end
    drawParagraph(r, self.medium, finalStory, px + 84, py + 336, 78, 30, 19, INK_R, INK_G, INK_B, 255, "left")

    label(r, self.medium, "Take a screenshot of this card to save & share your story with friends!", VW / 2, py + ph - 16, 14, 95, 85, 75, 255, "center")

    pill(self, r, "edit_story", "<- Edit Story", VW / 2 - 260, 662, 210, 46, PAPER_R, PAPER_G, PAPER_B, INK_R, INK_G, INK_B, 17)
    pill(self, r, "celebrate", "Celebrate!", VW / 2, 662, 210, 46, 246, 188, 68, INK_R, INK_G, INK_B, 17)
    pill(self, r, "other", "Try Another Level", VW / 2 + 260, 662, 230, 46, 112, 196, 132, INK_R, INK_G, INK_B, 17)
end

---------------------------------------------------------------- SPARKLES OVERLAY
local function drawSparkles(self: Game, r: Renderer)
    for _, sp in ipairs(self.sparkles) do
        local a = clamp01(1 - sp.life / sp.maxLife)
        drawCircle(r, sp.x, sp.y, sp.rad * a, fill(sp.r, sp.g, sp.b, math.floor(255 * a)))
    end
end

---------------------------------------------------------------- LIFECYCLE
local function applyDebugMode(self: Game)
    if DEBUG_MODE <= 0 then return end
    local sampleIds = { "c1_astronaut", "c2_02", "c3_rain", "c4_unicorn", "c5_lighter" }
    local function setSampleDeck()
        for i, c in ipairs(self.cards) do
            for k, it in ipairs(CardsData[c.cat].items) do
                if it.id == sampleIds[i] then c.item = k end
            end
        end
    end
    if DEBUG_MODE == 1 then
        startLevel(self, 1)
    elseif DEBUG_MODE == 2 then
        startLevel(self, 1)
        setSampleDeck()
        for i, c in ipairs(self.cards) do
            c.target = 1
            c.flip = 1
            if i == 1 then c.used = true end
        end
    elseif DEBUG_MODE == 3 then
        startLevel(self, 2)
        setSampleDeck()
        self.timerMax = 45
        self.timerLeft = 32
        self.timerRunning = true
        for _, c in ipairs(self.cards) do
            c.target = 1
            c.flip = 1
        end
    elseif DEBUG_MODE == 4 then
        startLevel(self, 3)
        setSampleDeck()
        self.timerMax = 60
        self.timerLeft = 48
        self.timerRunning = true
        self.sentenceOpen = true
        for i, c in ipairs(self.cards) do
            c.target = 1
            c.flip = 1
            if i <= 2 then c.used = true end
        end
    elseif DEBUG_MODE == 5 then
        startLevel(self, 4)
        setSampleDeck()
        self.sentenceOpen = true
        for _, c in ipairs(self.cards) do
            c.target = 1
            c.flip = 1
            c.used = true
        end
        self.phase = "write"
        self.storyBody = 'Once upon a time, an astronaut landed at the theater during a storm! Suddenly, out of nowhere, "I am from a different planet." Everyone applauded and shared a sundae.'
    elseif DEBUG_MODE == 6 then
        startLevel(self, 4)
        setSampleDeck()
        self.sentenceOpen = true
        for _, c in ipairs(self.cards) do
            c.target = 1
            c.flip = 1
            c.used = true
        end
        self.phase = "showcase"
        self.storyBody = 'Once upon a time, an astronaut landed at the theater during a storm! Suddenly, out of nowhere, "I am from a different planet." Everyone applauded and shared a sundae.'
    elseif DEBUG_MODE == 7 then
        self.screen = "hello"
        self.showHelp = true
    end
end

local function init(self: Game, context: Context): boolean
    self.context = context
    self.bold = context:font('Bold')
    self.medium = context:font('Medium')
    self.sampler = ImageSampler('clamp', 'clamp', 'bilinear')
    local ids = { "ui_bg", "ui_title", "ui_home", "ui_repeat", "ui_question", "lvl_rookie", "lvl_expert", "lvl_master", "lvl_guru" }
    for _, cat in ipairs(CardsData) do
        for _, it in ipairs(cat.items) do table.insert(ids, it.id) end
    end
    for _, id in ipairs(ids) do self.images[id] = context:image(id) end
    math.randomseed(math.floor(os.clock() * 100000) + 12345)
    for ci = 1, 5 do
        table.insert(self.cards, { cat = ci, item = 1, flip = 0, target = 0, used = false, pop = 0 })
    end
    dealAll(self)
    applyDebugMode(self)
    return true
end

local function resize(self: Game, size: Vector, _pixelRatio: number)
    self.winW = size.x
    self.winH = size.y
    self.scale = math.min(size.x / VW, size.y / VH)
    self.ox = (size.x - VW * self.scale) * 0.5
    self.oy = (size.y - VH * self.scale) * 0.5
end

local function backspaceOneChar(str: string): string
    local len = #str
    if len == 0 then return "" end
    local lastByte = string.byte(str, len)
    if lastByte < 128 then
        return string.sub(str, 1, len - 1)
    end
    local i = len
    while i > 1 and string.byte(str, i) >= 128 and string.byte(str, i) < 192 do
        i -= 1
    end
    return string.sub(str, 1, i - 1)
end

local function appendStoryText(self: Game, str: string)
    if #self.storyBody < 420 then
        self.storyBody = self.storyBody .. str
    end
end

local function advance(self: Game, seconds: number): boolean
    local dt = math.min(seconds, 0.1)
    self.time += dt
    self.screenT += dt
    self.toastT = math.max(0, self.toastT - dt)

    if self.pendingKey ~= nil then
        appendStoryText(self, self.pendingKey)
        self.pendingKey = nil
    end

    if self.timerRunning and self.timerLeft > 0 then
        self.timerLeft = math.max(0, self.timerLeft - dt)
        if self.timerLeft <= 0 then
            self.timerRunning = false
            spawnBurst(self, VW / 2, 180, 22)
        end
    end

    for _, c in ipairs(self.cards) do
        c.pop += dt
        if c.flip < c.target then c.flip = math.min(c.target, c.flip + dt / 0.42)
        elseif c.flip > c.target then c.flip = math.max(c.target, c.flip - dt / 0.42) end
    end

    for i = #self.sparkles, 1, -1 do
        local sp = self.sparkles[i]
        sp.life += dt
        sp.x += sp.vx * dt
        sp.y += sp.vy * dt
        sp.vy += 240 * dt
        if sp.life >= sp.maxLife then
            table.remove(self.sparkles, i)
        end
    end
    return true
end

local function draw(self: Game, renderer: Renderer)
    table.clear(self.zones)

    -- 1. Full-bleed background filling the entire physical window (eliminates any black bars on wide screens)
    drawRect(renderer, 0, 0, self.winW, self.winH, 0, fill(19, 107, 133, 255))
    local bgImg = self.images["ui_bg"]
    local sampler = self.sampler
    if bgImg ~= nil and sampler ~= nil and bgImg.width > 0 and self.winW > 0 and self.winH > 0 then
        renderer:save()
        local s = math.max(self.winW / bgImg.width, self.winH / bgImg.height)
        local bgOx = (self.winW - bgImg.width * s) * 0.5
        local bgOy = (self.winH - bgImg.height * s) * 0.5
        renderer:transform(Mat2D.withTranslation(bgOx, bgOy) * Mat2D.withScale(s, s))
        renderer:drawImage(bgImg, sampler, 'srcOver', 1)
        renderer:restore()
    end

    -- 2. Transformed game artboard (centered 1280x720)
    renderer:save()
    renderer:transform(Mat2D.withTranslation(self.ox, self.oy) * Mat2D.withScale(self.scale, self.scale))

    drawBackground(self, renderer)

    if self.screen == "hello" then
        drawHello(self, renderer)
        if self.showHelp then
            drawHelpModal(self, renderer)
        end
    else
        if self.phase == "write" then
            drawWriteStudio(self, renderer)
        elseif self.phase == "showcase" then
            drawShowcaseCard(self, renderer)
        else
            drawPlayStage(self, renderer)
        end
    end

    drawSparkles(self, renderer)

    if self.toastT > 0 then
        drawSketchBox(renderer, VW / 2 - 230, 662, 460, 42, 21, PAPER_R, PAPER_G, PAPER_B, 255, 99, false)
        label(renderer, self.bold, self.toast, VW / 2, 683, 17, INK_R, INK_G, INK_B, 255, "center")
    end

    renderer:restore()
end

local function hit(self: Game, event: PointerEvent): string
    local vx = (event.position.x - self.ox) / self.scale
    local vy = (event.position.y - self.oy) / self.scale
    for i = #self.zones, 1, -1 do
        local z = self.zones[i]
        if vx >= z.x and vx <= z.x + z.w and vy >= z.y and vy <= z.y + z.h then return z.id end
    end
    return ""
end

local function pointerMove(self: Game, event: PointerEvent)
    self.hover = hit(self, event)
end

local function keyToChar(key: number, shift: boolean): string?
    if key >= 65 and key <= 90 then -- A..Z
        if shift then
            return string.char(key)
        else
            return string.char(key + 32)
        end
    elseif key >= 48 and key <= 57 then -- 0..9
        if not shift then
            return string.char(key)
        else
            local shifted = {
                [48] = ")", [49] = "!", [50] = "@", [51] = "#", [52] = "$",
                [53] = "%", [54] = "^", [55] = "&", [56] = "*", [57] = "("
            }
            return shifted[key]
        end
    elseif key == 32 then -- Space
        return " "
    elseif key == 39 then return shift and '"' or "'"
    elseif key == 44 then return shift and "<" or ","
    elseif key == 45 then return shift and "_" or "-"
    elseif key == 46 then return shift and ">" or "."
    elseif key == 47 then return shift and "?" or "/"
    elseif key == 59 then return shift and ":" or ";"
    elseif key == 61 then return shift and "+" or "="
    elseif key == 91 then return shift and "{" or "["
    elseif key == 92 then return shift and "|" or "\\"
    elseif key == 93 then return shift and "}" or "]"
    elseif key == 96 then return shift and "~" or "`"
    end
    return nil
end

local function keyboardEvent(self: Game, event: KeyboardEvent): boolean
    if event.phase == "up" then
        return false
    end
    if event.key == 256 then -- Escape closes help modal
        if self.showHelp then
            self.showHelp = false
            return true
        end
    end

    if self.screen == "play" and self.phase == "write" then
        if event.key == 259 then -- Backspace
            if #self.storyBody > 0 then
                self.storyBody = backspaceOneChar(self.storyBody)
            end
            self.pendingKey = nil
            return true
        elseif event.key == 257 or event.key == 335 then -- Enter / Numpad Enter
            appendStoryText(self, "\n")
            self.pendingKey = nil
            return true
        else
            local ch = keyToChar(event.key, event.shift)
            if ch ~= nil then
                self.pendingKey = ch
                return true
            end
        end
    end
    return false
end

local function textEvent(self: Game, event: TextInput): boolean
    if self.screen == "play" and self.phase == "write" then
        self.pendingKey = nil -- textEvent handled input, clear fallback!
        if event.text ~= "\r" and event.text ~= "\n" then
            appendStoryText(self, event.text)
            return true
        end
    end
    return false
end

local function pointerDown(self: Game, event: PointerEvent)
    local id = hit(self, event)
    if id == "" then return end
    event:hit()

    if id == "btn_help" then
        self.showHelp = true
    elseif id == "close_help" then
        self.showHelp = false
    elseif id == "home" or id == "other" then
        self.screen = "hello"
        self.screenT = 0
        self.showHelp = false
    elseif id == "shuffle" then
        dealAll(self)
        toast(self, "5 new story cards dealt!")
    elseif id == "flip_all" then
        for _, c in ipairs(self.cards) do
            c.target = 1
        end
    elseif id == "mark_done" then
        for _, c in ipairs(self.cards) do
            c.target = 1
            c.used = true
        end
        spawnBurst(self, VW / 2, 360, 32)
        toast(self, "Awesome story! Try another level or shuffle new cards!")
    elseif id == "tm_30" then
        self.timerMax = 30
        self.timerLeft = 30
        self.timerRunning = true
    elseif id == "tm_45" then
        self.timerMax = 45
        self.timerLeft = 45
        self.timerRunning = true
    elseif id == "tm_60" then
        self.timerMax = 60
        self.timerLeft = 60
        self.timerRunning = true
    elseif id == "tm_skip" then
        self.timerLeft = 0
        self.timerRunning = false
        for _, c in ipairs(self.cards) do
            c.target = 1
        end
        spawnBurst(self, VW / 2, 220, 20)
    elseif id == "tm_reset" then
        self.timerMax = 0
        self.timerLeft = 0
        self.timerRunning = false
    elseif id == "twist_reveal" then
        self.sentenceOpen = true
        spawnBurst(self, 920, 175, 24)
    elseif id == "twist_next" then
        self.sentenceIdx = (self.sentenceIdx % #SENTENCES) + 1
        spawnBurst(self, 920, 175, 16)
    elseif id == "go_write" then
        for _, c in ipairs(self.cards) do
            c.target = 1
        end
        self.sentenceOpen = true
        self.phase = "write"
    elseif id == "back_cards" or id == "edit_story" then
        self.phase = (id == "edit_story") and "write" or "cards"
    elseif id == "go_showcase" then
        self.phase = "showcase"
        spawnBurst(self, VW / 2, 260, 36)
    elseif id == "celebrate" then
        spawnBurst(self, VW / 2, 300, 40)
    elseif id == "txt_clear" then
        self.storyBody = ""
    elseif id == "ins_twist" then
        local sp = (#self.storyBody > 0 and string.sub(self.storyBody, -1) ~= " ") and " " or ""
        appendStoryText(self, sp .. '"' .. SENTENCES[self.sentenceIdx] .. '" ')
    elseif string.sub(id, 1, 10) == "ins_start_" then
        local idx = tonumber(string.sub(id, 11)) or 1
        appendStoryText(self, STORY_STARTERS[idx])
    elseif id == "key_space" then
        appendStoryText(self, " ")
    elseif id == "key_back" then
        if #self.storyBody > 0 then
            self.storyBody = backspaceOneChar(self.storyBody)
        end
    elseif id == "key_shift" then
        self.shiftOn = not self.shiftOn
    elseif string.sub(id, 1, 4) == "key_" then
        local ch = string.sub(id, 5)
        appendStoryText(self, ch)
        if self.shiftOn then self.shiftOn = false end
    elseif string.sub(id, 1, 4) == "card" then
        local i = tonumber(string.sub(id, 5)) or 1
        local c = self.cards[i]
        if self.phase == "write" then
            local item = CardsData[c.cat].items[c.item]
            local word = string.lower(cleanItemLabel(item.name))
            appendStoryText(self, word .. " ")
        else
            if c.target < 0.5 then
                c.target = 1
            elseif c.flip > 0.85 then
                c.used = not c.used
                if c.used then
                    spawnBurst(self, VW / 2, 380, 14)
                end
            end
        end
    elseif string.sub(id, 1, 2) == "lv" then
        local i = tonumber(string.sub(id, 3)) or 1
        startLevel(self, i)
    end
end

return function(): Layout<Game>
    return {
        context = nil,
        bold = nil,
        medium = nil,
        images = {},
        sampler = nil,
        screen = "hello",
        screenT = 0,
        time = 0,
        levelIdx = 1,
        phase = "cards",
        cards = {},
        zones = {},
        sparkles = {},
        hover = "",
        scale = 1,
        ox = 0,
        oy = 0,
        winW = 1280,
        winH = 720,
        toast = "",
        toastT = 0,
        timerMax = 0,
        timerLeft = 0,
        timerRunning = false,
        sentenceIdx = 1,
        sentenceOpen = false,
        sentenceAnim = 0,
        storyTitle = "MY STORY",
        storyBody = "",
        shiftOn = true,
        showHelp = false,
        pendingKey = nil,
        init = init,
        resize = resize,
        advance = advance,
        draw = draw,
        pointerDown = pointerDown,
        pointerMove = pointerMove,
        keyboardEvent = keyboardEvent,
        textEvent = textEvent,
    }
end
