"""
TD Music Player - Runtime Asset Generator
==========================================
Generates all UI icons programmatically using Pillow.
No external image files required.
"""

import os
from PIL import Image, ImageDraw, ImageFont

ASSET_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")

def _ensure_dir():
    os.makedirs(ASSET_DIR, exist_ok=True)

def _save(img, name, size=(64, 64)):
    _ensure_dir()
    if size:
        img = img.resize(size, Image.Resampling.LANCZOS)
    path = os.path.join(ASSET_DIR, name)
    img.save(path, "PNG")
    return path

def _circle(draw, cx, cy, r, fill, outline=None, width=0):
    # Convert "transparent" to None for PIL
    if fill == "transparent":
        fill = None
    if outline == "transparent":
        outline = None
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=width)

def gen_icon(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size // 2, size // 2
    r = size // 2 - 10
    _circle(d, cx, cy, r, "#1DB954", "#1ED760", 4)
    hr = size // 8
    hx = cx + size // 10
    hy = cy + size // 5
    _circle(d, hx, hy, hr, "white")
    sw = size // 20
    st = cy - size // 3
    d.rectangle([hx, st, hx+sw, hy], fill="white")
    d.polygon([(hx+sw, st), (hx+sw+size//6, st+size//8), (hx+sw, st+size//5)], fill="white")
    return img

def gen_play(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _circle(d, size//2, size//2, size//2-8, "#1DB954", "#1ED760", 3)
    m = size // 3
    d.polygon([(m, m), (size-m, size//2), (m, size-m)], fill="white")
    return img

def gen_pause(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _circle(d, size//2, size//2, size//2-8, "#1DB954", "#1ED760", 3)
    bw = size // 8
    gap = size // 10
    lx = size//2 - gap - bw
    rx = size//2 + gap
    top = size // 4
    bot = size - size // 4
    d.rounded_rectangle([lx, top, lx+bw, bot], radius=6, fill="white")
    d.rounded_rectangle([rx, top, rx+bw, bot], radius=6, fill="white")
    return img

def gen_stop(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    _circle(d, size//2, size//2, size//2-8, "#ff4444", "#ff6666", 3)
    m = size // 3
    d.rounded_rectangle([m, m, size-m, size-m], radius=8, fill="white")
    return img

def gen_next(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = size // 5
    d.polygon([(m, m), (size-m*2, size//2), (m, size-m)], fill="white")
    bw = size // 12
    d.rounded_rectangle([size-m*1.5, m, size-m*1.5+bw, size-m], radius=3, fill="white")
    return img

def gen_prev(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    m = size // 5
    bw = size // 12
    d.rounded_rectangle([m, m, m+bw, size-m], radius=3, fill="white")
    d.polygon([(size-m, m), (m*2, size//2), (size-m, size-m)], fill="white")
    return img

def gen_search(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size//2 - size//10, size//2 - size//10
    r = size // 4
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline="white", width=size//14)
    x1, y1 = cx + int(r*0.7), cy + int(r*0.7)
    x2, y2 = cx + int(r*1.6), cy + int(r*1.6)
    d.line([(x1, y1), (x2, y2)], fill="white", width=size//12)
    return img

def gen_menu(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bh = size // 10
    gap = size // 6
    for i in range(3):
        y = size//4 + i*(bh + gap)
        d.rounded_rectangle([size//6, y, size-size//6, y+bh], radius=bh//2, fill="white")
    return img

def gen_volume(mute=False, size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    sw = size // 4
    sh = size // 3
    x1, y1 = size//6, size//2 - sh//2
    d.polygon([
        (x1, y1), (x1+sw, y1), (x1+sw+size//6, size//2-sh//2-size//8),
        (x1+sw+size//6, size//2+sh//2+size//8), (x1+sw, y1+sh), (x1, y1+sh)
    ], fill="white")
    if not mute:
        cx = x1 + sw + size//6
        cy = size // 2
        for i in range(2):
            r = size//8 + i*size//10
            d.arc([cx-r, cy-r, cx+r, cy+r], start=-60, end=60, fill="white", width=size//20)
    else:
        cx = x1 + sw + size//4
        cy = size // 2
        r = size // 8
        d.line([(cx-r, cy-r), (cx+r, cy+r)], fill="#ff4444", width=size//14)
        d.line([(cx+r, cy-r), (cx-r, cy+r)], fill="#ff4444", width=size//14)
    return img

def gen_shuffle(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w = size // 18
    y1, y2, y3 = size//4, size//2, size-size//4
    x1, x2 = size//6, size-size//6
    d.line([(x1, y1), (x2, y2)], fill="white", width=w)
    d.polygon([(x2, y2), (x2-size//8, y2-size//8), (x2-size//8, y2+size//8)], fill="white")
    d.line([(x1, y3), (x2, y2)], fill="white", width=w)
    d.polygon([(x2, y2), (x2-size//8, y2-size//8), (x2-size//8, y2+size//8)], fill="white")
    d.line([(x1, y2), (x2, y1)], fill="white", width=w)
    d.polygon([(x1, y2), (x1+size//8, y2-size//8), (x1+size//8, y2+size//8)], fill="white")
    d.line([(x1, y2), (x2, y3)], fill="white", width=w)
    d.polygon([(x1, y2), (x1+size//8, y2-size//8), (x1+size//8, y2+size//8)], fill="white")
    return img

def gen_repeat(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size//2, size//2
    r = size//3
    d.arc([cx-r, cy-r, cx+r, cy+r], start=30, end=330, fill="white", width=size//14)
    ax = cx + int(r*0.866)
    ay = cy - int(r*0.5)
    d.polygon([(ax, ay), (ax-size//6, ay-size//8), (ax-size//6, ay+size//8)], fill="white")
    return img

def gen_repeat_one(size=256):
    img = gen_repeat(size)
    d = ImageDraw.Draw(img)
    d.text((size//2-8, size//2-12), "1", fill="white")
    return img

def gen_folder(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fh = size // 3
    fw = size // 2
    tw = size // 4
    x, y = size//6, size//3
    d.rounded_rectangle([x, y, x+fw+size//6, y+fh], radius=10, fill="#FFD700", outline="#FFA500", width=3)
    d.rounded_rectangle([x, y-size//10, x+tw, y+size//15], radius=5, fill="#FFD700", outline="#FFA500", width=2)
    return img

def gen_heart(filled=True, size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = "#ff4444" if filled else "white"
    r = size // 5
    cx1, cx2 = size//2 - r + 5, size//2 + r - 5
    cy = size // 3
    _circle(d, cx1, cy, r, color)
    _circle(d, cx2, cy, r, color)
    d.polygon([(cx1-r, cy), (cx2+r, cy), (size//2, size - size//5)], fill=color)
    return img

def gen_lyrics(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bh = size // 12
    gap = size // 8
    for i in range(4):
        y = size//5 + i*(bh + gap)
        w = size - size//3 - (i * size//10)
        d.rounded_rectangle([size//6, y, size//6 + w, y+bh], radius=bh//2, fill="white")
    return img

def gen_timer(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size//2, size//2
    r = size//3
    d.ellipse([cx-r, cy-r, cx+r, cy+r], outline="white", width=size//16)
    d.line([(cx, cy), (cx, cy-r+size//12)], fill="white", width=size//20)
    d.line([(cx, cy), (cx+r-size//6, cy)], fill="white", width=size//20)
    return img

def gen_speed(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Gauge
    cx, cy = size//2, size//2 + size//10
    r = size//3
    d.arc([cx-r, cy-r, cx+r, cy-r+size//5], start=200, end=340, fill="white", width=size//20)
    # Needle
    angle = 270
    import math
    nx = cx + int(r*0.7 * math.cos(math.radians(angle)))
    ny = cy - size//10 + int(r*0.7 * math.sin(math.radians(angle)))
    d.line([(cx, cy-size//10), (nx, ny)], fill="white", width=size//20)
    return img

def gen_equalizer(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bw = size // 14
    gap = size // 20
    heights = [0.3, 0.6, 0.4, 0.8, 0.5, 0.9, 0.3]
    for i, h in enumerate(heights):
        x = size//8 + i*(bw + gap)
        bar_h = int(h * size * 0.6)
        y = size - size//4 - bar_h
        d.rounded_rectangle([x, y, x+bw, size-size//4], radius=3, fill="white")
    return img

def gen_settings(size=256):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx, cy = size//2, size//2
    # Gear
    for i in range(8):
        angle = i * 45
        import math
        x1 = cx + int(size//4 * math.cos(math.radians(angle)))
        y1 = cy + int(size//4 * math.sin(math.radians(angle)))
        x2 = cx + int(size//3 * math.cos(math.radians(angle)))
        y2 = cy + int(size//3 * math.sin(math.radians(angle)))
        d.line([(x1, y1), (x2, y2)], fill="white", width=size//15)
    _circle(d, cx, cy, size//6, "white")
    _circle(d, cx, cy, size//12, None)
    return img

def gen_empty_cover(size=400):
    img = Image.new("RGB", (size, size), (20, 20, 20))
    d = ImageDraw.Draw(img)
    cx, cy = size//2, size//2
    r = size//4
    d.ellipse([cx-r//2, cy+r//2, cx+r//2, cy+r*1.2], fill=(60, 60, 60))
    d.rectangle([cx+r//2, cy-r, cx+r//2+size//20, cy+r//2], fill=(60, 60, 60))
    d.polygon([
        (cx+r//2+size//20, cy-r),
        (cx+r, cy-r//2),
        (cx+r//2+size//20, cy-r//4)
    ], fill=(60, 60, 60))
    return img

GENERATORS = {
    "icon.png": gen_icon,
    "play.png": gen_play,
    "pause.png": gen_pause,
    "stop.png": gen_stop,
    "next.png": gen_next,
    "previous.png": gen_prev,
    "search.png": gen_search,
    "maximize.png": gen_menu,
    "volume.png": lambda: gen_volume(mute=False),
    "volume_mute.png": lambda: gen_volume(mute=True),
    "shuffle.png": gen_shuffle,
    "repeat.png": gen_repeat,
    "repeat_one.png": gen_repeat_one,
    "folder.png": gen_folder,
    "heart.png": lambda: gen_heart(filled=True),
    "heart_empty.png": lambda: gen_heart(filled=False),
    "lyrics.png": gen_lyrics,
    "timer.png": gen_timer,
    "speed.png": gen_speed,
    "equalizer.png": gen_equalizer,
    "settings.png": gen_settings,
    "empty_cover.jpg": gen_empty_cover,
}

def generate_all():
    _ensure_dir()
    for name, gen in GENERATORS.items():
        path = os.path.join(ASSET_DIR, name)
        if not os.path.exists(path):
            img = gen()
            if name.endswith(".jpg"):
                img.save(path, "JPEG", quality=90)
            else:
                _save(img, name, size=(64, 64))
    # Icon
    icon_path = os.path.join(os.path.dirname(ASSET_DIR), "icon.ico")
    if not os.path.exists(icon_path):
        gen_icon(256).resize((128, 128), Image.Resampling.LANCZOS).save(icon_path, format="ICO", sizes=[(128, 128)])

def check_and_generate():
    required = ["play.png", "pause.png", "next.png", "previous.png", "volume.png", "heart.png"]
    if any(not os.path.exists(os.path.join(ASSET_DIR, f)) for f in required):
        generate_all()
        return True
    return False

def get_asset_path(name):
    return os.path.join(ASSET_DIR, name)
