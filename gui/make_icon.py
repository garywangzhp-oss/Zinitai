# -*- coding: utf-8 -*-
"""图标候选 v3/v4：A=对称极简熊猫脸；B=熊猫脚印+朱红印。"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
S = 2048
FINAL = 512

PAPER = (250, 250, 247, 255)
PAPER_DK = (240, 239, 232, 255)
INK = (28, 28, 26, 255)
CINNABAR = (192, 58, 43, 255)
WHITE = (255, 255, 255, 255)


def tile():
    img = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([6, 6, S - 6, S - 6], radius=230, fill=PAPER, outline=INK, width=40)
    return img, d


def mirror(draw_fn, cx=1024):
    """画一次左半，镜像出右半——保证严格对称。"""
    layer = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(layer))
    img_m = layer.transpose(Image.FLIP_LEFT_RIGHT)
    return layer, img_m


def seal(img, box=(1520, 1500, 1880, 1860), char="护", fsize=190):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle(list(box), radius=44, fill=CINNABAR, outline=PAPER, width=16)
    font = None
    for name in ("simhei.ttf", "msyh.ttc", "simsun.ttc"):
        p = Path("C:/Windows/Fonts") / name
        if p.exists():
            font = ImageFont.truetype(str(p), fsize)
            break
    if font:
        cx, cy = (box[0] + box[2]) // 2, (box[1] + box[3]) // 2
        bbox = d.textbbox((0, 0), char, font=font)
        w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        d.text((cx - w / 2 - bbox[0], cy - h / 2 - bbox[1]), char, font=font, fill=WHITE)


def save(img, name):
    f = img.resize((FINAL, FINAL), Image.LANCZOS)
    f.save(HERE / name)
    print("生成", name)


# ---------- v3：对称极简熊猫脸 ----------
img, d = tile()
CX, CY, R = 1024, 1060, 560

# 耳朵（左右镜像）
def ears(dr):
    dr.ellipse([CX - 430 - 260, CY - 430 - 260, CX - 430 + 260, CY - 430 + 260], fill=INK)

l, m = mirror(ears)
img.alpha_composite(l)
img.alpha_composite(m)

# 脸
d.ellipse([CX - R, CY - R, CX + R, CY + R], fill=WHITE, outline=INK, width=30)

# 眼圈（斜椭圆，镜像）
def patches(dr):
    p = Image.new("RGBA", (460, 580), (0, 0, 0, 0))
    pd = ImageDraw.Draw(p)
    pd.ellipse([30, 40, 430, 540], fill=INK)
    p = p.rotate(24, resample=Image.BICUBIC)
    dr._image.alpha_composite(p, (CX - 350 - 230, CY - 190 - 280))

l, m = mirror(patches)
img.alpha_composite(l)
img.alpha_composite(m)

# 眼白
d2 = ImageDraw.Draw(img)
d2.ellipse([CX - 330 - 68, CY - 190 - 68, CX - 330 + 68, CY - 190 + 68], fill=WHITE)
d2.ellipse([CX + 330 - 68, CY - 190 - 68, CX + 330 + 68, CY - 190 + 68], fill=WHITE)

# 鼻 + 嘴
d2.ellipse([CX - 105, CY + 120, CX + 105, CY + 245], fill=INK)
d2.line([CX, CY + 245, CX, CY + 340], fill=INK, width=24)
d2.arc([CX - 155, CY + 290, CX + 155, CY + 490], start=25, end=155, fill=INK, width=24)

seal(img, (1560, 1560, 1870, 1870))
save(img, "icon_v3.png")

# 正式图标 = v3（对称熊猫脸）
f = img.resize((FINAL, FINAL), Image.LANCZOS)
f.save(HERE / "icon.ico",
       sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
f.save(HERE / "icon_preview.png")
print("已写入 icon.ico（v3 对称熊猫脸）")

# ---------- v4：熊猫脚印 + 朱红印 ----------
img, d = tile()

# 脚印：大掌 + 四趾（严格居中，墨黑）
pad_cx, pad_cy = 1024, 1290
d.ellipse([pad_cx - 330, pad_cy - 200, pad_cx + 330, pad_cy + 420], fill=INK)
toe_y = 830
for i, dx in enumerate((-430, -160, 160, 430)):
    r = 118 if i in (1, 2) else 104
    ty = toe_y + (36 if i in (0, 3) else 0)
    d.ellipse([pad_cx + dx - r, ty - r, pad_cx + dx + r, ty + r], fill=INK)

seal(img, (1470, 1460, 1830, 1820), fsize=180)
save(img, "icon_v4.png")
print("完成")
