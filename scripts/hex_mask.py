"""
Applies a perfect flat-top hexagon mask + dark border to an image.
Flat-top = flat edges at top and bottom, points on left and right.

Output size: TARGET_W x TARGET_H (1024 x 887) — exact hex proportions (2 : sqrt(3)).
The hex fills the entire image with no wasted transparent space on any side.
Uses 4x supersampling for smooth antialiased edges.

Usage:
    py scripts/hex_mask.py <image.png>         # overwrites in place
    py scripts/hex_mask.py <image.png> <out>   # saves to different file
    py scripts/hex_mask.py                     # runs on all Hex *.png in imgs/hexs/
"""
import sys
import math
import glob
import os
from PIL import Image, ImageDraw, ImageChops, ImageOps, ImageFilter

BORDER_WIDTH = 65       # pixels of dark border inset from hex edge
TARGET_W     = 1024
TARGET_H     = round(TARGET_W * math.sqrt(3) / 2)   # 887 — exact flat-top hex height

def make_hex_mask(w, h, r, scale):
    W, H = w * scale, h * scale
    CX, CY = W / 2, H / 2
    R = r * scale
    verts = [
        (CX + R * math.cos(math.radians(60 * i)),
         CY + R * math.sin(math.radians(60 * i)))
        for i in range(6)
    ]
    m = Image.new('L', (W, H), 0)
    ImageDraw.Draw(m).polygon(verts, fill=255)
    return m.resize((w, h), Image.LANCZOS)

def apply_hex_mask(input_path, output_path=None):
    if output_path is None:
        output_path = input_path

    img = Image.open(input_path).convert('RGBA')
    src_w, src_h = img.size

    # Scale to TARGET_W, then center-crop to TARGET_H
    scale_factor = TARGET_W / src_w
    scaled_h = round(src_h * scale_factor)
    img = img.resize((TARGET_W, scaled_h), Image.LANCZOS)

    if scaled_h > TARGET_H:
        top = (scaled_h - TARGET_H) // 2
        img = img.crop((0, top, TARGET_W, top + TARGET_H))
    elif scaled_h < TARGET_H:
        padded = Image.new('RGBA', (TARGET_W, TARGET_H), (0, 0, 0, 0))
        padded.paste(img, (0, (TARGET_H - scaled_h) // 2))
        img = padded

    w, h = TARGET_W, TARGET_H
    r = TARGET_W / 2   # circumradius — hex now fills the image exactly

    scale = 4

    # Outer hex mask (clip shape)
    mask_outer = make_hex_mask(w, h, r, scale)

    # Inner hex mask (defines where border starts)
    mask_inner = make_hex_mask(w, h, r - BORDER_WIDTH, scale)

    # Blur inner mask to create soft gradient toward the edge
    mask_inner_soft = mask_inner.filter(ImageFilter.GaussianBlur(radius=BORDER_WIDTH // 2))

    # Border alpha = inside hex AND NOT inside inner soft zone
    border_alpha = ImageChops.multiply(mask_outer, ImageOps.invert(mask_inner_soft))

    # Apply hex shape as alpha
    img.putalpha(mask_outer)

    # Build black border overlay and composite on top
    border_overlay = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    border_overlay.putalpha(border_alpha)
    result = Image.alpha_composite(img, border_overlay)

    result.save(output_path, 'PNG', optimize=True, compress_level=9)
    print(f'  OK: {os.path.basename(output_path)} {w}x{h}')

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        apply_hex_mask(sys.argv[1], sys.argv[2] if len(sys.argv) >= 3 else None)
    else:
        # Default: all Hex *.png in imgs/hexs/ relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        folder = os.path.join(project_root, 'imgs', 'hexs')
        images = glob.glob(os.path.join(folder, 'Hex *.png'))
        print(f'Processing {len(images)} images in {folder}...')
        for path in sorted(images):
            apply_hex_mask(path)
        print('Done.')
