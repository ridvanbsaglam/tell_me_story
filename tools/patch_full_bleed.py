with open(r'c:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\main.luau', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update Game type
old_type = """    scale: number,
    ox: number,
    oy: number,"""
new_type = """    scale: number,
    ox: number,
    oy: number,
    winW: number,
    winH: number,"""
assert old_type in text, "old_type not found"
text = text.replace(old_type, new_type, 1)

# 2. Update resize
old_resize = """local function resize(self: Game, size: Vector, _pixelRatio: number)
    self.scale = math.min(size.x / VW, size.y / VH)
    self.ox = (size.x - VW * self.scale) * 0.5
    self.oy = (size.y - VH * self.scale) * 0.5
end"""
new_resize = """local function resize(self: Game, size: Vector, _pixelRatio: number)
    self.winW = size.x
    self.winH = size.y
    self.scale = math.min(size.x / VW, size.y / VH)
    self.ox = (size.x - VW * self.scale) * 0.5
    self.oy = (size.y - VH * self.scale) * 0.5
end"""
assert old_resize in text, "old_resize not found"
text = text.replace(old_resize, new_resize, 1)

# 3. Update return factory
old_fact = """        scale = 1,
        ox = 0,
        oy = 0,"""
new_fact = """        scale = 1,
        ox = 0,
        oy = 0,
        winW = 1280,
        winH = 720,"""
assert old_fact in text, "old_fact not found"
text = text.replace(old_fact, new_fact, 1)

# 4. Update drawBackground & bubbles
old_drawbg = """local function drawBackground(self: Game, r: Renderer)
    local bgImg = self.images["ui_bg"]
    local sampler = self.sampler
    if bgImg ~= nil and sampler ~= nil and bgImg.width > 0 then
        r:save()
        r:transform(Mat2D.withScale(VW / bgImg.width, VH / bgImg.height))
        r:drawImage(bgImg, sampler, 'srcOver', 1)
        r:restore()
    else
        local bands = 24
        local bh = VH / bands
        for i = 0, bands - 1 do
            local t = i / (bands - 1)
            drawRect(r, 0, i * bh, VW, bh + 1, 0, fill(lerp(18, 8, t), lerp(124, 82, t), lerp(156, 112, t), 255))
        end
    end

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
end"""

new_drawbg = """local function drawBackground(self: Game, r: Renderer)
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
end"""
assert old_drawbg in text, "old_drawbg not found"
text = text.replace(old_drawbg, new_drawbg, 1)

# 5. Update draw function to do full-bleed background first
old_draw = """local function draw(self: Game, renderer: Renderer)
    table.clear(self.zones)
    renderer:save()
    renderer:transform(Mat2D.withTranslation(self.ox, self.oy) * Mat2D.withScale(self.scale, self.scale))

    drawBackground(self, renderer)"""

new_draw = """local function draw(self: Game, renderer: Renderer)
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

    drawBackground(self, renderer)"""
assert old_draw in text, "old_draw not found"
text = text.replace(old_draw, new_draw, 1)

with open(r'c:\Users\rsagl\.gemini\antigravity\scratch\Rive\tell_me_story\main.luau', 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print("Successfully patched main.luau for full-bleed background!")
