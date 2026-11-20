#!/usr/bin/env python3
"""Render the front page for Thursday 19 November 2026 as a PNG.

A single 1024 by 1024 newspaper page, drawn from scratch with Pillow:
masthead, lead story, six picture panels and a footer strip. Nothing is
pasted in from elsewhere; every mark on the page comes from a drawing
call in this file.
"""
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

CANVAS = (1024, 1024)

PALETTE = {
    "paper": (248, 244, 233),
    "ink": (24, 26, 32),
    "red": (178, 34, 34),
    "navy": (31, 58, 95),
    "teal": (18, 96, 92),
    "slate": (84, 90, 102),
    "white": (255, 255, 255),
}

FONT_FILES = ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSerif-Bold.ttf")
FONT_DIRS = (
    "/usr/share/fonts/truetype/dejavu/",
    "/usr/share/fonts/dejavu/",
    "/usr/local/share/fonts/dejavu/",
    "/Library/Fonts/",
    "/System/Library/Fonts/",
    "C:/Windows/Fonts/",
)


def locate_fonts():
    """Return the first directory holding all three DejaVu faces."""
    roots = []
    env_dir = os.environ.get("FONT_DIR")
    if env_dir:
        roots.append(env_dir)
    roots.extend(FONT_DIRS)
    for root in roots:
        if not root:
            continue
        if all(os.path.isfile(os.path.join(root, name)) for name in FONT_FILES):
            return root
    raise RuntimeError(
        "DejaVu fonts not found; set FONT_DIR to a folder holding "
        "DejaVuSans.ttf / DejaVuSans-Bold.ttf / DejaVuSerif-Bold.ttf"
    )


class FrontPage:
    """Owns the canvas and every drawing routine for the front page."""

    def __init__(self):
        self.font_dir = locate_fonts()
        self._faces = {}
        self.image = Image.new("RGB", CANVAS, PALETTE["paper"])
        self.pen = ImageDraw.Draw(self.image)

    def face(self, filename, size):
        key = (filename, size)
        got = self._faces.get(key)
        if got is None:
            got = ImageFont.truetype(os.path.join(self.font_dir, filename), size)
            self._faces[key] = got
        return got

    def serif_bold(self, size):
        return self.face("DejaVuSerif-Bold.ttf", size)

    def sans_bold(self, size):
        return self.face("DejaVuSans-Bold.ttf", size)

    def sans(self, size):
        return self.face("DejaVuSans.ttf", size)

    def wrap(self, text, font, width):
        """Split text into lines that fit `width` pixels, greedily.

        A word wider than the box on its own is an error, not a silent
        overflow: the caller has to fix the copy or the box.
        """
        words = text.split()
        lines = []
        start = 0
        while start < len(words):
            end = start
            current = ""
            while end < len(words):
                word = words[end]
                if font.getlength(word) > width:
                    raise ValueError(f"word too wide for its box: {word!r}")
                trial = (current + " " + word).strip()
                if font.getlength(trial) > width:
                    break
                current = trial
                end += 1
            lines.append(current)
            start = end
        return lines

    def balance_headline(self, lines, font, width):
        """Even out a two-line headline with a lone word on line two.

        The last word of line one moves down; the new line two is
        re-measured first, because the move can overflow the panel.
        """
        if len(lines) != 2:
            return lines
        upper, lower = lines
        upper_words = upper.split()
        lower_words = lower.split()
        if len(lower_words) != 1 or len(upper_words) < 2:
            return lines
        moved = [" ".join(upper_words[:-1]), upper_words[-1] + " " + lower]
        if font.getlength(moved[1]) > width:
            raise ValueError(f"balanced headline line 2 too wide: {moved[1]!r}")
        return moved

    def centred(self, x0, x1, y, text, font, fill=None):
        """Draw text centred between x0 and x1 at height y."""
        colour = PALETTE["ink"] if fill is None else fill
        width = font.getlength(text)
        if width > x1 - x0:
            raise ValueError(f"centred text too wide: {text!r}")
        self.pen.text(((x0 + x1 - width) / 2, y), text, font=font, fill=colour)

    def star_points(self, cx, cy, outer, inner, rotation=-math.pi / 2):
        """Vertices of a five-pointed star, alternating radii."""
        points = []
        for step in range(10):
            radius = outer if step % 2 == 0 else inner
            angle = rotation + step * math.pi / 5
            points.append((cx + radius * math.cos(angle),
                           cy + radius * math.sin(angle)))
        return points

    def burst(self, cx, cy, reach, colour, width, hub=12, hub_colour=(255, 120, 0)):
        """Eight spokes radiating from a point, with a filled hub."""
        spokes = []
        for k in range(8):
            theta = k * math.pi / 4
            spokes.append((cx + reach * math.cos(theta),
                           cy + reach * math.sin(theta)))
        for tip in spokes:
            self.pen.line([cx, cy, tip[0], tip[1]], fill=colour, width=width)
        self.pen.ellipse([cx - hub, cy - hub, cx + hub, cy + hub],
                         fill=hub_colour)

    def waves(self, x, y, w, h):
        """Five white wave arcs along the bottom of a sea band."""
        for i in range(5):
            self.pen.arc([x + 8 + i * 58, y + h - 34, x + 52 + i * 58, y + h - 10],
                         180, 360, fill=PALETTE["white"], width=3)

    def flag(self, x, y, w, h, kind):
        """Tiny simplified flag: stripes / disc / stars, drawn, not copied."""
        if kind == "us":
            stripes = [((178, 34, 52) if i % 2 == 0 else PALETTE["white"])
                       for i in range(7)]
            for i, colour in enumerate(stripes):
                self.pen.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                                   fill=colour)
            self.pen.rectangle([x, y, x + w * 0.4, y + h * 4 / 7],
                               fill=(30, 50, 110))
        elif kind == "cn":
            self.pen.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
            # One large star + four small stars on an arc (real flag geometry).
            big = self.star_points(x + w * 0.18, y + h * 0.27, h * 0.17, h * 0.075)
            self.pen.polygon(big, fill=(255, 222, 0))
            small_spots = [(0.36, 0.10), (0.46, 0.22), (0.46, 0.40), (0.36, 0.52)]
            for sx, sy in small_spots:
                pts = self.star_points(x + w * sx, y + h * sy, h * 0.06, h * 0.026)
                self.pen.polygon(pts, fill=(255, 222, 0))
        elif kind == "ru":
            bands = [(255, 255, 255), (0, 57, 166), (213, 0, 50)]
            for i, colour in enumerate(bands):
                self.pen.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3],
                                   fill=colour)
        self.pen.rectangle([x, y, x + w, y + h], outline=PALETTE["ink"], width=1)

    def _building(self, x, base, bx, bw, bh):
        """One navy tower with lit windows, standing on `base`."""
        self.pen.rectangle([x + bx, base - bh, x + bx + bw, base],
                           fill=PALETTE["navy"])
        rows = list(range(base - bh + 8, base - 6, 14))
        cols = list(range(x + bx + 6, x + bx + bw - 4, 12))
        for wy in rows:
            for wx in cols:
                self.pen.rectangle([wx, wy, wx + 5, wy + 6],
                                   fill=(253, 214, 130))

    def skyline(self, box):
        """Shenzhen skyline at dusk with three flags."""
        x, y, w, h = box
        self.pen.rectangle([x, y, x + w, y + h], fill=(253, 214, 130))
        self.pen.ellipse([x + 106, y + 10, x + 126, y + 30], fill=(240, 120, 40))
        base = y + h
        towers = [(0, 34, 62), (38, 26, 88), (68, 40, 52),
                  (112, 30, 96), (146, 36, 66), (186, 28, 84),
                  (218, 42, 58), (264, 66, 78)]
        for bx, bw, bh in towers:
            self._building(x, base, bx, bw, bh)
        self.pen.rectangle([x, y + h - 4, x + w, y + h], fill=PALETTE["ink"])
        self.flag(x + 14, y + 6, 46, 26, "us")
        self.flag(x + w // 2 - 23, y + 6, 46, 26, "cn")
        self.flag(x + w - 60, y + 6, 46, 26, "ru")

    def bridge(self, box):
        """Broken bridge arch over water, with a blast star."""
        x, y, w, h = box
        self.pen.rectangle([x, y, x + w, y + h], fill=(183, 214, 232))
        self.pen.rectangle([x, y + h - 26, x + w, y + h], fill=(46, 110, 160))
        self.waves(x, y, w, h)
        spans = [(x + 10, x + w // 2 - 26), (x + w // 2 + 26, x + w - 10)]
        for left, right in spans:
            self.pen.rectangle([left, y + 52, right, y + 66], fill=(90, 90, 96))
        # Broken arch: two segments with a gap at the top centre, where the
        # road span fell. Both feet stay inside the icon box (y + 60 < y + h).
        arch_box = [x + w // 2 - 78, y + 28, x + w // 2 + 78, y + 92]
        for start, end in ((180, 255), (285, 360)):
            self.pen.arc(arch_box, start, end, fill=(90, 90, 96), width=8)
        self.burst(x + w // 2, y + 44, 26, (255, 170, 0), 5)
        for px in (x + 18, x + w - 18):
            self.pen.line([px, y + 52, px, y + 66], fill=PALETTE["ink"], width=3)

    def tanker(self, box):
        """Tanker on the sea with a blast star; small radar rings top-left.

        No drone, no interceptor: UKMTO reported an *unknown* projectile,
        so the icon must not imply a weapon type.
        """
        x, y, w, h = box
        self.pen.rectangle([x, y, x + w, y + h], fill=(24, 40, 58))
        # Small radar rings, top-left.
        rx, ry = x + 42, y + 30
        for r in (18, 12, 6):
            self.pen.ellipse([rx - r, ry - r, rx + r, ry + r],
                             outline=(90, 200, 120), width=2)
        self.pen.pieslice([rx - 18, ry - 18, rx + 18, ry + 18],
                          205, 250, fill=(90, 200, 120))
        # Sea band + waves.
        self.pen.rectangle([x, y + 70, x + w, y + h], fill=(46, 110, 160))
        self.waves(x, y, w, h)
        # Tanker hull + superstructure.
        self.pen.polygon([(x + 70, y + 56), (x + 262, y + 56), (x + 276, y + 64),
                          (x + 262, y + 74), (x + 70, y + 74)], fill=(150, 50, 45))
        self.pen.rectangle([x + 70, y + 56, x + 262, y + 60], fill=(220, 220, 220))
        self.pen.rectangle([x + 214, y + 36, x + 246, y + 56], fill=(230, 230, 225))
        self.pen.rectangle([x + 248, y + 30, x + 258, y + 56], fill=(90, 90, 96))
        for wy in range(y + 40, y + 54, 7):
            self.pen.rectangle([x + 218, wy, x + 224, wy + 3], fill=(24, 40, 58))
        # Blast star above midship: the tanker was hit (weapon unknown).
        self.burst(x + 150, y + 38, 16, (255, 170, 0), 4, hub=8)

    def _polar(self, cx, cy, radius, degrees):
        """Point on a circle: centre (cx, cy), radius, angle in degrees."""
        theta = math.radians(degrees)
        return (cx + radius * math.cos(theta), cy + radius * math.sin(theta))

    def cyclone(self, box):
        """Spiral storm over a coastline."""
        x, y, w, h = box
        self.pen.rectangle([x, y, x + w, y + h], fill=(200, 222, 238))
        self.pen.rectangle([x, y + h - 22, x + w, y + h], fill=(232, 196, 120))
        hills = [[(x + 18, y + h - 22), (x + 60, y + h - 52), (x + 110, y + h - 22)],
                 [(x + w - 120, y + h - 22), (x + w - 70, y + h - 44),
                  (x + w - 16, y + h - 22)]]
        for hill in hills:
            self.pen.polygon(hill, fill=(120, 160, 90))
        # Spiral bound: at 270 deg in turn 2 the radius is 32 + 9 = 41,
        # plus half line width 2.5 -> 43.5 px above centre. cy = y + 47
        # keeps the top at y + 3.5 and the bottom at y + 84.5, inside the box.
        cx, cy = x + w // 2, y + h // 2 - 3
        segments = []
        for turn in range(3):
            r0 = 8 + turn * 12
            for a in range(0, 360, 6):
                r1 = r0 + (a / 360.0) * 12
                r2 = r0 + ((a + 6) / 360.0) * 12
                p1 = self._polar(cx, cy, r1, a + turn * 360)
                p2 = self._polar(cx, cy, r2, a + 6 + turn * 360)
                segments.append((p1[0], p1[1], p2[0], p2[1]))
        for seg in segments:
            self.pen.line(list(seg), fill=PALETTE["navy"], width=5)
        self.pen.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=PALETTE["navy"])

    def chip(self, box):
        """Computer chip with a rising chart arrow."""
        x, y, w, h = box
        self.pen.rectangle([x, y, x + w, y + h], fill=(226, 238, 226))
        # cy centred: pins reach cy +/- 48, i.e. y + 2 .. y + 98, inside the box.
        cx, cy = x + 62, y + h // 2
        pins = []
        for px in (-34, -12, 12, 34):
            pins.append((cx + px, cy - 34, cx + px, cy - 48))
            pins.append((cx + px, cy + 34, cx + px, cy + 48))
        for py in (-22, 0, 22):
            pins.append((cx - 34, cy + py, cx - 48, cy + py))
            pins.append((cx + 34, cy + py, cx + 48, cy + py))
        for pin in pins:
            self.pen.line(list(pin), fill=PALETTE["navy"], width=4)
        self.pen.rectangle([cx - 34, cy - 34, cx + 34, cy + 34],
                           fill=PALETTE["navy"])
        # Blue core (not Nvidia green) and a green rising arrow: in US
        # markets red reads as "down", green as "up".
        self.pen.rectangle([cx - 18, cy - 18, cx + 18, cy + 18],
                           fill=(46, 110, 180))
        ai_font = self.sans_bold(20)
        ai_w = ai_font.getlength("AI")
        self.pen.text((cx - ai_w / 2, cy - 13), "AI", font=ai_font,
                      fill=PALETTE["white"])
        chart = [(x + dx, y + dy) for dx, dy in
                 [(150, h - 22), (185, 62), (212, 82),
                  (246, 34), (272, 46), (292, 18)]]
        self.pen.line(chart, fill=(20, 130, 70), width=5, joint="curve")
        self.pen.polygon([(x + 292, y + 18), (x + 276, y + 14), (x + 288, y + 34)],
                         fill=(20, 130, 70))

    def eu_flag(self, box):
        """EU flag motif: a ring of twelve gold stars on blue, over a table."""
        x, y, w, h = box
        self.pen.rectangle([x, y, x + w, y + h], fill=(0, 51, 153))
        mid = x + w // 2
        # Table first, then the star ring on top, so the two lowest stars
        # stay visible instead of being buried behind the table.
        self.pen.ellipse([mid - 52, y + 66, mid + 52, y + 92], fill=(139, 92, 42))
        self.pen.ellipse([mid - 52, y + 60, mid + 52, y + 76], fill=(176, 124, 66))
        cx, cy = mid, y + 46
        for k in range(12):
            angle = -math.pi / 2 + k * math.pi / 6
            sx = cx + 36 * math.cos(angle)
            sy = cy + 36 * math.sin(angle)
            self.pen.polygon(self.star_points(sx, sy, 7, 3), fill=(255, 204, 0))

    def game_city(self, box):
        """Night city skyline with a big VI."""
        x, y, w, h = box
        self.pen.rectangle([x, y, x + w, y + h], fill=(26, 18, 52))
        star_spots = [(20, 14), (70, 26), (130, 10), (200, 22), (260, 12), (290, 28)]
        for sx, sy in star_spots:
            self.pen.ellipse([x + sx, y + sy, x + sx + 4, y + sy + 4],
                             fill=PALETTE["white"])
        base = y + h
        towers = [
            {"bx": 0, "bw": 30, "bh": 46, "lit": True},
            {"bx": 34, "bw": 24, "bh": 70, "lit": False},
            {"bx": 62, "bw": 36, "bh": 54, "lit": True},
            {"bx": 102, "bw": 26, "bh": 52, "lit": False},
            {"bx": 132, "bw": 34, "bh": 48, "lit": True},
            {"bx": 170, "bw": 28, "bh": 66, "lit": False},
            {"bx": 202, "bw": 38, "bh": 58, "lit": True},
            {"bx": 244, "bw": 30, "bh": 76, "lit": False},
            {"bx": 278, "bw": 22, "bh": 50, "lit": True},
        ]
        for tower in towers:
            bx, bw, bh = tower["bx"], tower["bw"], tower["bh"]
            self.pen.rectangle([x + bx, base - bh, x + bx + bw, base],
                               fill=(12, 8, 30))
            if not tower["lit"]:
                continue
            for wy in range(base - bh + 8, base - 6, 14):
                self.pen.rectangle([x + bx + 6, wy, x + bx + 12, wy + 6],
                                   fill=(255, 200, 60))
        vi_font = self.serif_bold(52)
        vi_w = vi_font.getlength("VI")
        self.pen.text((x + w // 2 - vi_w / 2, y + 6), "VI", font=vi_font,
                      fill=(255, 90, 200), stroke_width=2,
                      stroke_fill=PALETTE["white"])

    def masthead(self):
        """Red rule, title, subtitle, dateline."""
        width, _height = CANVAS
        self.pen.rectangle([0, 0, width, 6], fill=PALETTE["red"])
        self.centred(0, width, 26, "THE WORLD IN ONE DAY", self.serif_bold(52))
        self.centred(0, width, 92, "One day's world news, in one picture",
                     self.sans(17), fill=PALETTE["slate"])
        for rule_y, rule_w in ((128, 2), (133, 1), (192, 2)):
            self.pen.line([60, rule_y, width - 60, rule_y],
                          fill=PALETTE["ink"], width=rule_w)
        self.centred(0, width, 142, "THURSDAY  ·  19 NOVEMBER 2026",
                     self.sans_bold(34), fill=PALETTE["red"])

    def lead(self):
        """Lead story: skyline icon left, text right, inside a ruled box."""
        lx, ly, lw, lh = 26, 204, 972, 184
        self.pen.rectangle([lx, ly, lx + lw, ly + lh],
                           outline=PALETTE["ink"], width=3, fill=PALETTE["white"])
        self.skyline((lx + 14, ly + 14, 330, lh - 28))
        self.pen.line([lx + 358, ly + 14, lx + 358, ly + lh - 14],
                      fill=PALETTE["slate"], width=1)
        tx = lx + 378
        self.pen.text((tx, ly + 16), "LEAD  ·  ASIA-PACIFIC",
                      font=self.sans_bold(16), fill=PALETTE["red"])
        head_font = self.sans_bold(30)
        head_lines = self.wrap("Xi, Trump and Putin meet", head_font, lw - 378 - 20)
        yy = ly + 40
        for line in head_lines:
            self.pen.text((tx, yy), line, font=head_font, fill=PALETTE["ink"])
            yy += 36
        body = ("Xi Jinping hosted the APEC summit in Shenzhen. Trump and "
                "Putin joined him for the first three-way talks. Their "
                "'peace declaration' pledges nuclear-risk talks, fuel "
                "supplies and UN reform — no arms deal, no mention of "
                "Ukraine.")
        body_font = self.sans(18)
        body_lines = self.wrap(body, body_font, lw - 378 - 20)
        if len(body_lines) > 4:
            raise ValueError("lead body too long for its box")
        # A 2-line headline would push yy +36 and silently overflow the box.
        if yy + len(body_lines) * 24 > ly + lh - 8:
            raise ValueError("lead body overflows its box")
        for line in body_lines:
            self.pen.text((tx, yy), line, font=body_font, fill=PALETTE["ink"])
            yy += 24

    def grid(self):
        """Six picture panels in a 3 by 2 grid."""
        panels = [
            {"kicker": "CULTURE  ·  GAMES", "headline": "GTA VI GOES ON SALE",
             "body": ("GTA VI went on sale at midnight for PS5 and Xbox. "
                      "Metacritic scores it 99 of 100; 2.5m watched on Twitch."),
             "icon": self.game_city, "accent": (90, 30, 110)},
            {"kicker": "EUROPE  ·  WAR IN UKRAINE", "headline": "CRIMEA BRIDGE HIT AGAIN",
             "body": ("A third strike hit the rail span; trains resumed on one "
                      "track. Road traffic stays shut; Kyiv says an arch fell."),
             "icon": self.bridge, "accent": PALETTE["navy"]},
            {"kicker": "MIDDLE EAST  ·  GULF", "headline": "TANKER HIT OFF OMAN",
             "body": ("A UAE tanker was hit off Oman; one crew member is missing. "
                      "The US and Iran traded strikes."),
             "icon": self.tanker, "accent": PALETTE["teal"]},
            {"kicker": "ASIA  ·  WEATHER", "headline": "CYCLONE AKVAN NEARS INDIA",
             "body": ("Akvan is forecast to cross Narsapur-Puri by noon Friday, "
                      "winds 90-100 km/h. Schools shut."),
             "icon": self.cyclone, "accent": (38, 96, 140)},
            {"kicker": "BUSINESS  ·  TECH", "headline": "ANTHROPIC'S $81.3BN IPO",
             "body": ("The Claude maker priced its shares at $83, the largest "
                      "IPO on record. ANT closed up 17% at $97.17."),
             "icon": self.chip, "accent": (60, 90, 30)},
            {"kicker": "EUROPE  ·  ALLIES", "headline": "ALLIES MEET IN BERLIN",
             "body": ("Allies met in Berlin to back Ukraine's air defences and "
                      "energy grid. The UK pledged 1,000+ long-range drones."),
             "icon": self.eu_flag, "accent": (30, 60, 140)},
        ]
        gx, gy = 26, 400
        gw, gh = 316, 270
        gap = 12
        for row in range(2):
            for col in range(3):
                panel = panels[row * 3 + col]
                px = gx + col * (gw + gap)
                py = gy + row * (gh + gap)
                accent = panel["accent"]
                self.pen.rectangle([px, py, px + gw, py + gh],
                                   outline=PALETTE["ink"], width=2,
                                   fill=PALETTE["white"])
                self.pen.rectangle([px, py, px + gw, py + 8], fill=accent)
                panel["icon"]((px + 8, py + 16, gw - 16, 100))
                kicker_font = self.sans_bold(13)
                if kicker_font.getlength(panel["kicker"]) > gw - 24:
                    raise ValueError(f"kicker too wide for panel: {panel['kicker']}")
                self.pen.text((px + 12, py + 122), panel["kicker"],
                              font=kicker_font, fill=accent)
                yy = py + 142
                head_font = self.sans_bold(19)
                head_lines = self.balance_headline(
                    self.wrap(panel["headline"], head_font, gw - 24),
                    head_font, gw - 24)
                if len(head_lines) > 2:
                    raise ValueError(f"headline too long for panel: {panel['headline']}")
                for line in head_lines:
                    self.pen.text((px + 12, yy), line, font=head_font,
                                  fill=PALETTE["ink"])
                    yy += 23
                yy += 3
                body_font = self.sans(15)
                body_lines = self.wrap(panel["body"], body_font, gw - 24)
                if len(body_lines) > 3:
                    raise ValueError(f"body too long for panel: {panel['headline']}")
                if yy + len(body_lines) * 19 > py + gh - 6:
                    raise ValueError(f"body overflows panel: {panel['headline']}")
                for line in body_lines:
                    self.pen.text((px + 12, yy), line, font=body_font,
                                  fill=(40, 42, 50))
                    yy += 19

    def footer(self):
        """Also-today strip and the sources line."""
        width, _height = CANVAS
        fy = 962
        self.pen.line([26, fy, width - 26, fy], fill=PALETTE["ink"], width=2)
        self.pen.text((26, fy + 10), "ALSO TODAY",
                      font=self.sans_bold(15), fill=PALETTE["red"])
        also = "A Van Gogh sold for an artist-record $190.4m at Sotheby's in New York."
        also_font = self.sans(15)
        if also_font.getlength(also) > width - 150 - 26:
            raise ValueError("ALSO TODAY line too long")
        self.pen.text((150, fy + 10), also, font=also_font, fill=PALETTE["ink"])
        sources = ("Sources: Reuters, NYT, BBC, IMD, CNN, Le Monde  ·  Events of "
                   "Thursday 19 November 2026, as reported by 20 Nov, 08:30 WIB.")
        sources_font = self.sans(13)
        if sources_font.getlength(sources) > width - 52:
            raise ValueError("Sources line too wide")
        self.pen.text((26, fy + 34), sources, font=sources_font,
                      fill=PALETTE["slate"])

    def save(self):
        out = Path(__file__).resolve().parent / "entry.png"
        self.image.save(out, optimize=True)
        print("saved entry.png")


def main():
    page = FrontPage()
    page.masthead()
    page.lead()
    page.grid()
    page.footer()
    page.save()


if __name__ == "__main__":
    main()
