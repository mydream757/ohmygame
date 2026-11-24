# 포크 전용 "OH" 앱 아이콘을 만든다. Dock 에서 공식 앱·다른 Electron 앱과 구별하려는 것.
# 쓰는 법: python3 -I scripts/make-oh-icon.py  → build/icon.icns 를 덮어쓴다(원본은 git 에 있다)
import os, shutil, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = 1024

def font(size):
    for path, index in (("/System/Library/Fonts/Helvetica.ttc", 1), ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 0)):
        if os.path.exists(path):
            return ImageFont.truetype(path, size, index=index)
    sys.exit("굵은 글꼴을 찾지 못함")

def draw():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    # macOS 아이콘 격자: 824px 둥근 사각형을 가운데 둔다
    inset, box = 100, 824
    bg = Image.new("RGBA", (box, box))
    top, bottom = (124, 58, 237), (49, 16, 120)  # 보라 세로 그라데이션
    for y in range(box):
        t = y / (box - 1)
        ImageDraw.Draw(bg).line([(0, y), (box, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)) + (255,))
    mask = Image.new("L", (box, box), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, box - 1, box - 1], radius=185, fill=255)
    img.paste(bg, (inset, inset), mask)
    d = ImageDraw.Draw(img)
    f = font(400)
    l, t, r, b = d.textbbox((0, 0), "OH", font=f)
    d.text(((S - (r - l)) / 2 - l, (S - (b - t)) / 2 - t), "OH", font=f, fill=(255, 255, 255, 255))
    return img

def main():
    src = draw()
    tmp = tempfile.mkdtemp()
    iconset = os.path.join(tmp, "icon.iconset")
    os.makedirs(iconset)
    for size in (16, 32, 128, 256, 512):
        src.resize((size, size), Image.LANCZOS).save(os.path.join(iconset, f"icon_{size}x{size}.png"))
        src.resize((size * 2, size * 2), Image.LANCZOS).save(os.path.join(iconset, f"icon_{size}x{size}@2x.png"))
    src.save(os.path.join(ROOT, "build", "icon-oh.png"))
    subprocess.run(["iconutil", "-c", "icns", iconset, "-o", os.path.join(ROOT, "build", "icon.icns")], check=True)
    shutil.rmtree(tmp)
    print("build/icon.icns, build/icon-oh.png")

main()
