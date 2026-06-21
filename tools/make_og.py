# -*- coding: utf-8 -*-
"""生成社交分享预览图 site/og.png(1200x630)与 apple-touch-icon site/icon-180.png。
零外部服务,纯 PIL + 文泉驿正黑(容器内已装)。可复跑,确定性输出(固定随机种子)。
配色沿用站点暗色主题与树状图色阶 RAMP,使预览图与实际可视化一致。
"""
import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(ROOT, 'site')
FONT = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'

# 站点调色板(取自 site/index.html)
BG_TOP = (10, 13, 20)      # #0a0d14
BG_BOT = (14, 20, 36)      # 略带蓝,底部稍亮
TEXT = (233, 237, 246)     # #e9edf6
MUTED = (147, 160, 186)    # #93a0ba
SOFT = (107, 120, 150)     # #6b7896
ACCENT = (109, 140, 240)   # #6d8cf0
ACCENT2 = (143, 134, 230)  # #8f86e6
# 树状图色阶(RAMP.dark):teal -> green -> gold -> orange -> red
RAMP = [(64, 160, 150), (128, 178, 108), (224, 190, 104), (226, 138, 84), (206, 78, 94)]


def lerp_ramp(t):
    t = max(0.0, min(1.0, t))
    s = len(RAMP) - 1
    x = t * s
    i = min(s - 1, int(x))
    f = x - i
    a, b = RAMP[i], RAMP[i + 1]
    return tuple(round(a[k] + (b[k] - a[k]) * f) for k in range(3))


def vgradient(w, h, top, bot):
    """竖直渐变(用 1 像素宽竖条放大,快且平滑)。"""
    strip = Image.new('RGB', (1, h))
    for y in range(h):
        f = y / (h - 1)
        strip.putpixel((0, y), tuple(round(top[k] + (bot[k] - top[k]) * f) for k in range(3)))
    return strip.resize((w, h))


def font(size):
    return ImageFont.truetype(FONT, size, index=0)


def fit_font(draw, text, max_w, start, lo=14):
    """返回能让 text 宽度 <= max_w 的最大字号字体。"""
    s = start
    while s > lo:
        fnt = font(s)
        if draw.textlength(text, font=fnt) <= max_w:
            return fnt
        s -= 2
    return font(lo)


# ---- 标准 squarified treemap(移植自 squarify 算法,用于绘制真实树状图 motif)----
def _normalize(sizes, dx, dy):
    total = sum(sizes)
    area = dx * dy
    return [s * area / total for s in sizes]


def _layoutrow(sizes, x, y, dy):
    width = sum(sizes) / dy
    rects = []
    for s in sizes:
        rects.append((x, y, width, s / width))
        y += s / width
    return rects


def _layoutcol(sizes, x, y, dx):
    height = sum(sizes) / dx
    rects = []
    for s in sizes:
        rects.append((x, y, s / height, height))
        x += s / height
    return rects


def _layout(sizes, x, y, dx, dy):
    return _layoutrow(sizes, x, y, dy) if dx >= dy else _layoutcol(sizes, x, y, dx)


def _leftover(sizes, x, y, dx, dy):
    cov = sum(sizes)
    if dx >= dy:
        width = cov / dy
        return (x + width, y, dx - width, dy)
    height = cov / dx
    return (x, y + height, dx, dy - height)


def _worst(sizes, x, y, dx, dy):
    return max(max(w / h, h / w) for (_, _, w, h) in _layout(sizes, x, y, dx, dy))


def squarify(sizes, x, y, dx, dy):
    sizes = [float(s) for s in sizes]
    if not sizes:
        return []
    if len(sizes) == 1:
        return _layout(sizes, x, y, dx, dy)
    i = 1
    while i < len(sizes) and _worst(sizes[:i], x, y, dx, dy) >= _worst(sizes[:i + 1], x, y, dx, dy):
        i += 1
    cur, rest = sizes[:i], sizes[i:]
    lx, ly, ldx, ldy = _leftover(cur, x, y, dx, dy)
    return _layout(cur, x, y, dx, dy) + squarify(rest, lx, ly, ldx, ldy)


def draw_treemap(d, x, y, w, h, weights, seed=7, gap=5, radius=9, alpha=255):
    rng = random.Random(seed)
    sizes = _normalize(sorted(weights, reverse=True), w, h)
    rects = squarify(sizes, x, y, w, h)
    for (rx, ry, rw, rh) in rects:
        score = rng.random()
        col = lerp_ramp(score) + (alpha,)
        d.rounded_rectangle(
            [rx + gap / 2, ry + gap / 2, rx + rw - gap / 2, ry + rh - gap / 2],
            radius=radius, fill=col)


def make_og():
    W, H = 1200, 630
    img = vgradient(W, H, BG_TOP, BG_BOT).convert('RGBA')

    # 右上角柔和强调辉光(低透明,增加层次)
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W - 560, -220, W + 160, 500], fill=ACCENT + (46,))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.alpha_composite(img, glow)

    d = ImageDraw.Draw(img)

    # 右侧树状图 motif(真实 squarify,色阶=站点 RAMP)
    tm_x, tm_y, tm_w, tm_h = 752, 96, 372, 438
    weights = [40, 30, 22, 18, 15, 13, 11, 9, 8, 7, 6, 5, 4, 4, 3, 3, 2]
    draw_treemap(d, tm_x, tm_y, tm_w, tm_h, weights, seed=11, gap=6, radius=10, alpha=235)
    # motif 细边框
    d.rounded_rectangle([tm_x - 2, tm_y - 2, tm_x + tm_w + 2, tm_y + tm_h + 2],
                        radius=14, outline=(40, 50, 70, 180), width=1)

    # 左侧文字区
    x0 = 76
    maxw = tm_x - x0 - 36  # 文字列宽

    # eyebrow
    d.text((x0, 92), '交互树状图 · 中国版', font=font(26), fill=ACCENT)

    # 标题(两行,大号)
    tfont = font(74)
    d.text((x0, 138), 'AI 时代各岗位', font=tfont, fill=TEXT)
    d.text((x0, 224), '冲击图谱', font=tfont, fill=TEXT)
    # 强调短横线
    d.rounded_rectangle([x0 + 2, 320, x0 + 92, 326], radius=3, fill=ACCENT)

    # 副标题
    sub = '看 AI 对中国 1639 个细类职业的潜在冲击'
    d.text((x0, 348), sub, font=fit_font(d, sub, maxw, 32), fill=MUTED)

    # 看图要点
    pts = '面积 = 就业人数,颜色 = 所选维度得分'
    d.text((x0, 396), pts, font=fit_font(d, pts, maxw, 26), fill=ACCENT2)

    # 统计行
    stat = '8 大类 · 79 中类 · 1639 细类 · 13 模型集成 + 匿名投票'
    d.text((x0, 452), stat, font=fit_font(d, stat, maxw, 24), fill=MUTED)

    # 底部来源行
    src = '官方锚定:职业分类大典2022 · 七普就业 · 统计局薪资'
    d.text((x0, 556), src, font=fit_font(d, src, maxw + 30, 21), fill=SOFT)

    out = os.path.join(SITE, 'og.png')
    img.convert('RGB').save(out, 'PNG', optimize=True)
    print('OK og.png', img.size, str(os.path.getsize(out) // 1024) + 'KB')


def make_icon():
    """180x180 apple-touch-icon:暗底圆角 + 小树状图。"""
    S = 180
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, S - 1, S - 1], radius=40, fill=(13, 18, 30, 255))
    # 内嵌迷你树状图
    weights = [34, 22, 16, 12, 9, 7]
    draw_treemap(d, 26, 26, S - 52, S - 52, weights, seed=4, gap=7, radius=9, alpha=255)
    out = os.path.join(SITE, 'icon-180.png')
    img.convert('RGB').save(out, 'PNG', optimize=True)
    print('OK icon-180.png', img.size, str(os.path.getsize(out) // 1024) + 'KB')


if __name__ == '__main__':
    make_og()
    make_icon()
