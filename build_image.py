#!/usr/bin/env python3
"""Draw the 19 November 2026 world-news front page (1024x1024 PNG).

Every element is drawn with PIL primitives: no photos, no copied art.
Palette is a newspaper front page: warm paper, dark ink, one red accent.
"""
import math
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (248, 244, 233)
INK = (24, 26, 32)
RED = (178, 34, 34)
NAVY = (31, 58, 95)
TEAL = (18, 96, 92)
SLATE = (84, 90, 102)
WHITE = (255, 255, 255)

def _find_font_dir():
    """Locate the DejaVu fonts across OSes (Debian/Ubuntu, Fedora, macOS, Windows)."""
    override = os.environ.get("FONT_DIR")
    candidates = [override] if override else []
    candidates += [
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/dejavu/",
        "/usr/local/share/fonts/dejavu/",
        "/Library/Fonts/",
        "/System/Library/Fonts/",
        "C:/Windows/Fonts/",
    ]
    need = ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSerif-Bold.ttf")
    for d in candidates:
        if d and all(os.path.isfile(os.path.join(d, f)) for f in need):
            return d
    raise RuntimeError(
        "DejaVu fonts not found; set FONT_DIR to a folder holding "
        "DejaVuSans.ttf / DejaVuSans-Bold.ttf / DejaVuSerif-Bold.ttf")

FDIR = _find_font_dir()
def font(name, size):
    return ImageFont.truetype(os.path.join(FDIR, name), size)

SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS = lambda s: font("DejaVuSans.ttf", s)

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

def wrap(text, fnt, width):
    """Greedy wrap by measured pixel width.

    Raises ValueError instead of silently overflowing: a single word
    wider than the box, or a caller that truncates lines, must fail
    loudly rather than print broken text.
    """
    words, lines, cur = text.split(), [], ""
    for w in words:
        if fnt.getlength(w) > width:
            raise ValueError(f"word too wide for its box: {w!r}")
        trial = (cur + " " + w).strip()
        if fnt.getlength(trial) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def balance_two_lines(lines, fnt, width):
    """If a headline wrapped to two lines with a lone word on line 2,
    move the last word of line 1 down so both lines read evenly.

    Re-checks the pixel width of the new line 2: moving a word down can
    make it overflow the panel, and that must fail loudly like wrap().
    """
    if len(lines) == 2:
        first, last = lines[0].split(), lines[1].split()
        if len(last) == 1 and len(first) > 1:
            new = [" ".join(first[:-1]), first[-1] + " " + lines[1]]
            if fnt.getlength(new[1]) > width:
                raise ValueError(f"balanced headline line 2 too wide: {new[1]!r}")
            return new
    return lines

def centred_text(x0, x1, y, text, fnt, fill=INK):
    w = fnt.getlength(text)
    if w > x1 - x0:
        raise ValueError(f"centred text too wide: {text!r}")
    d.text(((x0 + x1 - w) / 2, y), text, font=fnt, fill=fill)

def flag(drw, x, y, w, h, kind):
    """Tiny simplified flag: stripes / disc / stars, drawn, not copied."""
    if kind == "us":
        for i in range(7):
            drw.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                          fill=(178, 34, 52) if i % 2 == 0 else WHITE)
        drw.rectangle([x, y, x + w * 0.4, y + h * 4 / 7], fill=(30, 50, 110))
    elif kind == "cn":
        drw.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
        # One large star + four small stars on an arc (real flag geometry).
        # The old loop drew five identical stars stacked on one point.
        def _star(cx, cy, r1, r2, rot=-math.pi / 2):
            pts = []
            for j in range(10):
                r = r1 if j % 2 == 0 else r2
                ang = rot + j * math.pi / 5
                pts.append((cx + r * math.cos(ang), cy + r * math.sin(ang)))
            drw.polygon(pts, fill=(255, 222, 0))
        _star(x + w * 0.18, y + h * 0.27, h * 0.17, h * 0.075)
        for sx, sy in [(0.36, 0.10), (0.46, 0.22), (0.46, 0.40), (0.36, 0.52)]:
            _star(x + w * sx, y + h * sy, h * 0.06, h * 0.026)
    elif kind == "ru":
        for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
            drw.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)
    drw.rectangle([x, y, x + w, y + h], outline=INK, width=1)

# ---------------------------------------------------------------- masthead
d.rectangle([0, 0, W, 6], fill=RED)
centred_text(0, W, 26, "THE WORLD IN ONE DAY", SERIF_B(52))
centred_text(0, W, 92, "One day's world news, in one picture", SANS(17), fill=SLATE)
d.line([60, 128, W - 60, 128], fill=INK, width=2)
d.line([60, 133, W - 60, 133], fill=INK, width=1)
centred_text(0, W, 142, "THURSDAY  ·  19 NOVEMBER 2026", SANS_B(34), fill=RED)
d.line([60, 192, W - 60, 192], fill=INK, width=2)

# ---------------------------------------------------------------- icons
def icon_skyline(x, y, w, h):
    """Shenzhen skyline at dusk with three flags."""
    d.rectangle([x, y, x + w, y + h], fill=(253, 214, 130))
    d.ellipse([x + 106, y + 10, x + 126, y + 30], fill=(240, 120, 40))
    base = y + h
    for bx, bw, bh in [(0, 34, 62), (38, 26, 88), (68, 40, 52),
                       (112, 30, 96), (146, 36, 66), (186, 28, 84),
                       (218, 42, 58), (264, 66, 78)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=NAVY)
        for wy in range(base - bh + 8, base - 6, 14):
            for wx in range(x + bx + 6, x + bx + bw - 4, 12):
                d.rectangle([wx, wy, wx + 5, wy + 6], fill=(253, 214, 130))
    d.rectangle([x, y + h - 4, x + w, y + h], fill=INK)
    flag(d, x + 14, y + 6, 46, 26, "us")
    flag(d, x + w // 2 - 23, y + 6, 46, 26, "cn")
    flag(d, x + w - 60, y + 6, 46, 26, "ru")

def icon_bridge(x, y, w, h):
    """Broken bridge arch over water, with a blast star."""
    d.rectangle([x, y, x + w, y + h], fill=(183, 214, 232))
    d.rectangle([x, y + h - 26, x + w, y + h], fill=(46, 110, 160))
    for i in range(5):
        d.arc([x + 8 + i * 58, y + h - 34, x + 52 + i * 58, y + h - 10],
              180, 360, fill=(255, 255, 255), width=3)
    d.rectangle([x + 10, y + 52, x + w // 2 - 26, y + 66], fill=(90, 90, 96))
    d.rectangle([x + w // 2 + 26, y + 52, x + w - 10, y + 66], fill=(90, 90, 96))
    # Broken arch: two segments with a gap at the top centre, where the
    # road span fell. Both feet stay inside the icon box (y + 60 < y + h).
    d.arc([x + w // 2 - 78, y + 28, x + w // 2 + 78, y + 92],
          180, 255, fill=(90, 90, 96), width=8)
    d.arc([x + w // 2 - 78, y + 28, x + w // 2 + 78, y + 92],
          285, 360, fill=(90, 90, 96), width=8)
    for k in range(8):
        a = k * math.pi / 4
        r1 = 26
        x1 = x + w // 2 + r1 * math.cos(a)
        y1 = y + 44 + r1 * math.sin(a)
        d.line([x + w // 2, y + 44, x1, y1], fill=(255, 170, 0), width=5)
    d.ellipse([x + w // 2 - 12, y + 32, x + w // 2 + 12, y + 56],
              fill=(255, 120, 0))
    d.line([x + 18, y + 52, x + 18, y + 66], fill=INK, width=3)
    d.line([x + w - 18, y + 52, x + w - 18, y + 66], fill=INK, width=3)

def icon_radar(x, y, w, h):
    """Tanker on the sea with a blast star; small radar rings top-left.

    No drone, no interceptor: UKMTO reported an *unknown* projectile,
    so the icon must not imply a weapon type.
    """
    d.rectangle([x, y, x + w, y + h], fill=(24, 40, 58))
    # Small radar rings, top-left.
    rx, ry = x + 42, y + 30
    for r in (18, 12, 6):
        d.ellipse([rx - r, ry - r, rx + r, ry + r],
                  outline=(90, 200, 120), width=2)
    d.pieslice([rx - 18, ry - 18, rx + 18, ry + 18],
               205, 250, fill=(90, 200, 120))
    # Sea band + waves.
    d.rectangle([x, y + 70, x + w, y + h], fill=(46, 110, 160))
    for i in range(5):
        d.arc([x + 8 + i * 58, y + h - 34, x + 52 + i * 58, y + h - 10],
              180, 360, fill=(255, 255, 255), width=3)
    # Tanker hull + superstructure.
    d.polygon([(x + 70, y + 56), (x + 262, y + 56), (x + 276, y + 64),
               (x + 262, y + 74), (x + 70, y + 74)], fill=(150, 50, 45))
    d.rectangle([x + 70, y + 56, x + 262, y + 60], fill=(220, 220, 220))
    d.rectangle([x + 214, y + 36, x + 246, y + 56], fill=(230, 230, 225))
    d.rectangle([x + 248, y + 30, x + 258, y + 56], fill=(90, 90, 96))
    for wy in range(y + 40, y + 54, 7):
        d.rectangle([x + 218, wy, x + 224, wy + 3], fill=(24, 40, 58))
    # Blast star above midship: the tanker was hit (weapon unknown).
    bx, by = x + 150, y + 38
    for k in range(8):
        a = k * math.pi / 4
        x1 = bx + 16 * math.cos(a)
        y1 = by + 16 * math.sin(a)
        d.line([bx, by, x1, y1], fill=(255, 170, 0), width=4)
    d.ellipse([bx - 8, by - 8, bx + 8, by + 8], fill=(255, 120, 0))

def icon_cyclone(x, y, w, h):
    """Spiral storm over a coastline."""
    d.rectangle([x, y, x + w, y + h], fill=(200, 222, 238))
    d.rectangle([x, y + h - 22, x + w, y + h], fill=(232, 196, 120))
    d.polygon([(x + 18, y + h - 22), (x + 60, y + h - 52), (x + 110, y + h - 22)],
              fill=(120, 160, 90))
    d.polygon([(x + w - 120, y + h - 22), (x + w - 70, y + h - 44),
               (x + w - 16, y + h - 22)], fill=(120, 160, 90))
    # Spiral bound: at 270 deg in turn 2 the radius is 32 + 9 = 41,
    # plus half line width 2.5 -> 43.5 px above centre. cy = y + 47
    # keeps the top at y + 3.5 and the bottom at y + 84.5, inside the box.
    cx, cy = x + w // 2, y + h // 2 - 3
    for turn in range(3):
        r0 = 8 + turn * 12
        for a in range(0, 360, 6):
            a1 = math.radians(a + turn * 360)
            a2 = math.radians(a + 6 + turn * 360)
            r1 = r0 + (a / 360.0) * 12
            r2 = r0 + ((a + 6) / 360.0) * 12
            d.line([cx + r1 * math.cos(a1), cy + r1 * math.sin(a1),
                    cx + r2 * math.cos(a2), cy + r2 * math.sin(a2)],
                   fill=(31, 58, 95), width=5)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=(31, 58, 95))

def icon_chip(x, y, w, h):
    """Computer chip with a rising chart arrow."""
    d.rectangle([x, y, x + w, y + h], fill=(226, 238, 226))
    # cy centred: pins reach cy +/- 48, i.e. y + 2 .. y + 98, inside the box.
    cx, cy = x + 62, y + h // 2
    for px in (-34, -12, 12, 34):
        d.line([cx + px, cy - 34, cx + px, cy - 48], fill=(31, 58, 95), width=4)
        d.line([cx + px, cy + 34, cx + px, cy + 48], fill=(31, 58, 95), width=4)
    for py in (-22, 0, 22):
        d.line([cx - 34, cy + py, cx - 48, cy + py], fill=(31, 58, 95), width=4)
        d.line([cx + 34, cy + py, cx + 48, cy + py], fill=(31, 58, 95), width=4)
    d.rectangle([cx - 34, cy - 34, cx + 34, cy + 34], fill=(31, 58, 95))
    # Blue core (not Nvidia green) and a green rising arrow: in US
    # markets red reads as "down", green as "up".
    d.rectangle([cx - 18, cy - 18, cx + 18, cy + 18], fill=(46, 110, 180))
    _ai_w = SANS_B(20).getlength("AI")
    d.text((cx - _ai_w / 2, cy - 13), "AI", font=SANS_B(20), fill=WHITE)
    pts = [(x + 150, y + h - 22), (x + 185, y + 62), (x + 212, y + 82),
           (x + 246, y + 34), (x + 272, y + 46), (x + 292, y + 18)]
    d.line(pts, fill=(20, 130, 70), width=5, joint="curve")
    d.polygon([(x + 292, y + 18), (x + 276, y + 14), (x + 288, y + 34)],
              fill=(20, 130, 70))

def icon_eu(x, y, w, h):
    """EU flag motif: a ring of twelve gold stars on blue, over a table."""
    d.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
    # Table first, then the star ring on top, so the two lowest stars
    # stay visible instead of being buried behind the table.
    d.ellipse([x + w // 2 - 52, y + 66, x + w // 2 + 52, y + 92],
              fill=(139, 92, 42))
    d.ellipse([x + w // 2 - 52, y + 60, x + w // 2 + 52, y + 76],
              fill=(176, 124, 66))
    cx, cy = x + w // 2, y + 46
    for k in range(12):
        a = -math.pi / 2 + k * math.pi / 6
        sx, sy = cx + 36 * math.cos(a), cy + 36 * math.sin(a)
        pts = []
        for j in range(10):
            r = 7 if j % 2 == 0 else 3
            ang = -math.pi / 2 + j * math.pi / 5
            pts.append((sx + r * math.cos(ang), sy + r * math.sin(ang)))
        d.polygon(pts, fill=(255, 204, 0))

def icon_game(x, y, w, h):
    """Night city skyline with a big VI."""
    d.rectangle([x, y, x + w, y + h], fill=(26, 18, 52))
    for sx, sy in [(20, 14), (70, 26), (130, 10), (200, 22), (260, 12), (290, 28)]:
        d.ellipse([x + sx, y + sy, x + sx + 4, y + sy + 4], fill=WHITE)
    base = y + h
    for bx, bw, bh, lit in [(0, 30, 46, True), (34, 24, 70, False),
                            (62, 36, 54, True), (102, 26, 52, False),
                            (132, 34, 48, True), (170, 28, 66, False),
                            (202, 38, 58, True), (244, 30, 76, False),
                            (278, 22, 50, True)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(12, 8, 30))
        if lit:
            for wy in range(base - bh + 8, base - 6, 14):
                d.rectangle([x + bx + 6, wy, x + bx + 12, wy + 6],
                            fill=(255, 200, 60))
    _vi = SERIF_B(52)
    d.text((x + w // 2 - _vi.getlength("VI") / 2, y + 6), "VI", font=_vi,
           fill=(255, 90, 200), stroke_width=2, stroke_fill=(255, 255, 255))

# ---------------------------------------------------------------- lead story
LX, LY, LW, LH = 26, 204, 972, 184
d.rectangle([LX, LY, LX + LW, LY + LH], outline=INK, width=3, fill=WHITE)
icon_skyline(LX + 14, LY + 14, 330, LH - 28)
d.line([LX + 358, LY + 14, LX + 358, LY + LH - 14], fill=SLATE, width=1)
tx = LX + 378
d.text((tx, LY + 16), "LEAD  ·  ASIA-PACIFIC", font=SANS_B(16), fill=RED)
lines = wrap("Xi, Trump and Putin meet", SANS_B(30), LW - 378 - 20)
yy = LY + 40
for ln in lines:
    d.text((tx, yy), ln, font=SANS_B(30), fill=INK)
    yy += 36
body = ("Xi Jinping hosted the APEC summit in Shenzhen. Trump and "
        "Putin joined him for the first three-way talks. Their "
        "'peace declaration' pledges nuclear-risk talks, fuel "
        "supplies and UN reform — no arms deal, no mention of "
        "Ukraine.")
lead_body_lines = wrap(body, SANS(18), LW - 378 - 20)
if len(lead_body_lines) > 4:
    raise ValueError("lead body too long for its box")
# A 2-line headline would push yy +36 and silently overflow the box.
if yy + len(lead_body_lines) * 24 > LY + LH - 8:
    raise ValueError("lead body overflows its box")
for ln in lead_body_lines:
    d.text((tx, yy), ln, font=SANS(18), fill=INK)
    yy += 24

# ---------------------------------------------------------------- grid panels
PANELS = [
    ("CULTURE  ·  GAMES", "GTA VI GOES ON SALE",
     "GTA VI went on sale at midnight for PS5 and Xbox. Metacritic "
     "scores it 99 of 100; 2.5m watched on Twitch.",
     icon_game, (90, 30, 110)),
    ("EUROPE  ·  WAR IN UKRAINE", "CRIMEA BRIDGE HIT AGAIN",
     "A third strike hit the rail span; trains resumed on one "
     "track. Road traffic stays shut; Kyiv says an arch fell.",
     icon_bridge, NAVY),
    ("MIDDLE EAST  ·  GULF", "TANKER HIT OFF OMAN",
     "A UAE tanker was hit off Oman; one crew member is missing. "
     "The US and Iran traded strikes.",
     icon_radar, TEAL),
    ("ASIA  ·  WEATHER", "CYCLONE AKVAN NEARS INDIA",
     "Akvan is forecast to cross Narsapur-Puri by noon Friday, "
     "winds 90-100 km/h. Schools shut.", icon_cyclone, (38, 96, 140)),
    ("BUSINESS  ·  TECH", "ANTHROPIC'S $81.3BN IPO",
     "The Claude maker priced its shares at $83, the largest "
     "IPO on record. ANT closed up 17% at $97.17.",
     icon_chip, (60, 90, 30)),
    ("EUROPE  ·  ALLIES", "ALLIES MEET IN BERLIN",
     "Allies met in Berlin to back Ukraine's air defences and "
     "energy grid. The UK pledged 1,000+ long-range drones.",
     icon_eu, (30, 60, 140)),
]

GX, GY = 26, 400
GW, GH = 316, 270
GAP = 12
for i, (kicker, head, body, icon, accent) in enumerate(PANELS):
    col, row = i % 3, i // 3
    px = GX + col * (GW + GAP)
    py = GY + row * (GH + GAP)
    d.rectangle([px, py, px + GW, py + GH], outline=INK, width=2, fill=WHITE)
    d.rectangle([px, py, px + GW, py + 8], fill=accent)
    icon(px + 8, py + 16, GW - 16, 100)
    if SANS_B(13).getlength(kicker) > GW - 24:
        raise ValueError(f"kicker too wide for panel: {kicker}")
    d.text((px + 12, py + 122), kicker, font=SANS_B(13), fill=accent)
    yy = py + 142
    head_lines = balance_two_lines(wrap(head, SANS_B(19), GW - 24),
                                   SANS_B(19), GW - 24)
    if len(head_lines) > 2:
        raise ValueError(f"headline too long for panel: {head}")
    for ln in head_lines:
        d.text((px + 12, yy), ln, font=SANS_B(19), fill=INK)
        yy += 23
    yy += 3
    body_lines = wrap(body, SANS(15), GW - 24)
    if len(body_lines) > 3:
        raise ValueError(f"body too long for panel: {head}")
    if yy + len(body_lines) * 19 > py + GH - 6:
        raise ValueError(f"body overflows panel: {head}")
    for ln in body_lines:
        d.text((px + 12, yy), ln, font=SANS(15), fill=(40, 42, 50))
        yy += 19

# ---------------------------------------------------------------- footer
FY = 962
d.line([26, FY, W - 26, FY], fill=INK, width=2)
d.text((26, FY + 10), "ALSO TODAY", font=SANS_B(15), fill=RED)
_also = "A Van Gogh sold for an artist-record $190.4m at Sotheby's in New York."
if SANS(15).getlength(_also) > W - 150 - 26:
    raise ValueError("ALSO TODAY line too long")
d.text((150, FY + 10), _also, font=SANS(15), fill=INK)
_src = ("Sources: Reuters, NYT, BBC, IMD, CNN, Le Monde  ·  Events of "
        "Thursday 19 November 2026, as reported by 20 Nov, 08:30 WIB.")
if SANS(13).getlength(_src) > W - 52:
    raise ValueError("Sources line too wide")
d.text((26, FY + 34), _src, font=SANS(13), fill=SLATE)

OUT = Path(__file__).resolve().parent / "entry.png"
img.save(OUT, optimize=True)
print("saved entry.png")
