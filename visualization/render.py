#!/usr/bin/env python3
"""Render two exact binary word trees at a common d2 infimum."""
from math import cos, sin, tau
from pathlib import Path
from fractions import Fraction
import argparse

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 680, 610
BG, PANEL = "#0e1a27", "#13283b"
FG, SUBTLE = "#f0f6fc", "#b1c7db"
BLUE, EDGE, GOLD = "#80c9f5", "#58718a", "#ffd07b"
PLOT_DEPTH = 4
NODES = [(d, i) for d in range(PLOT_DEPTH + 1) for i in range(2**d)]


def font_factory(path):
    paths = [path] if path else [
        Path("/System/Library/Fonts/Supplemental"), Path("/usr/share/fonts/truetype/dejavu")
    ]
    for directory in paths:
        for regular, bold in [("Arial.ttf", "Arial Bold.ttf"), ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf")]:
            if all((directory / name).is_file() for name in (regular, bold)):
                return lambda size, strong=False: ImageFont.truetype(
                    str(directory / (bold if strong else regular)), size)
    raise SystemExit("Pass --font-dir containing Arial or DejaVu Sans")


def project(node, angle, center):
    depth, i = node
    phase = angle + tau * (i + .5) / 2**depth
    radius = 0 if depth == 0 else 0.47 + 0.075 * depth
    left = radius * cos(phase)
    front = radius * sin(phase)
    scale = 122 * 6 / (6 + front)
    return center + scale * left, 233 + depth * 47 - front * 17, front


def cost(horizon):
    return Fraction(1, 2) + Fraction(1, 2**(horizon + 2))


def card(draw, font, x, angle, horizon, finite):
    center = x + 155
    draw.rounded_rectangle((x, 118, x+310, 501), 17, fill=PANEL)
    title = "Finite target" if finite else "Full word tree"
    line = "Target: root and two children" if finite else "Target: all words"
    draw.text((x+16, 135), title, font=font(24, True), fill=FG)
    draw.text((x+16, 169), line, font=font(17), fill=SUBTLE)
    draw.text((x+16, 195), "X = {empty word}" if finite else f"X contains all words of length <= {horizon}",
              font=font(17), fill=SUBTLE)
    nodes = {v: project(v, angle, center) for v in NODES}
    def misses(v):
        return v[0] == 0 or (not finite and v[0] >= horizon + 2)
    for d, i in sorted(NODES, key=lambda p: nodes[p][2], reverse=True):
        if not d:
            continue
        near, far = (d-1, i//2), (d,i)
        draw.line((nodes[near][:2], nodes[far][:2]), fill=GOLD if misses(near) and misses(far) else EDGE,
                  width=2)
    for v in sorted(NODES, key=lambda p: nodes[p][2], reverse=True):
        u, y, _ = nodes[v]
        radius = 7 if v[0] == 0 else 5
        draw.ellipse((u-radius, y-radius, u+radius, y+radius), fill=GOLD if misses(v) else BLUE,
                     width=1, outline=PANEL)
    draw.text((x+16, 438), f"Cost {Fraction(1, 2) if finite else cost(horizon)}",
              font=font(24, True), fill=GOLD)
    draw.text((x+16, 472), "Attains 1/2" if finite else "Every finite cutoff leaves a tail",
              font=font(17), fill=FG)


def frame(i, total, font):
    picture = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(picture)
    draw.text((26, 20), "Does a finite assignment attain it?", font=font(35, True), fill=FG)
    draw.text((28, 72), "Worked example  /  Common infimum and threshold 1/2",
              font=font(22), fill=SUBTLE)
    angle = 0.45 + tau * i / total
    horizon = i * 3 // total
    card(draw, font, 20, angle, horizon, True)
    card(draw, font, 350, angle, horizon, False)
    draw.ellipse((29, 536, 45, 552), fill=GOLD)
    draw.text((55, 530), "disagreement", font=font(20), fill=FG)
    draw.ellipse((222, 536, 238, 552), fill=BLUE)
    draw.text((248, 530), "agreement", font=font(20), fill=FG)
    draw.text((28, 572), "Each node is a word. The full binary tree continues below.", font=font(19), fill=SUBTLE)
    return picture.quantize(colors=64)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font-dir", type=Path)
    parser.add_argument("--frames", type=int, default=36)
    parser.add_argument("--out", type=Path, default=ROOT / "attainment-tree.gif")
    args = parser.parse_args()
    if args.frames < 3 or args.frames % 3:
        parser.error("--frames must be a positive multiple of three")
    font = font_factory(args.font_dir)
    frames = [frame(i, args.frames, font) for i in range(args.frames)]
    durations = [110] * len(frames)
    for i in range(args.frames // 3 - 1, args.frames, args.frames // 3):
        durations[i] = 600
    frames[0].save(args.out, save_all=True, append_images=frames[1:], optimize=True,
                   duration=durations, loop=0, disposal=1)


if __name__ == "__main__":
    main()
