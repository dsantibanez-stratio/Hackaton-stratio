"""
Stratio Logo Background Remover
================================
Usa este script cuando recibas logos nuevos en formato RGB (sin transparencia).
Detecta automáticamente el color de fondo usando la esquina superior izquierda
y lo elimina, convirtiendo el logo a RGBA con fondo transparente.

Uso:
    python3 remove_bg.py logo-input.png logo-output.png
    python3 remove_bg.py  # procesa los 4 logos estándar desde uploads
"""

import sys
import numpy as np
from PIL import Image


def remove_bg(input_path, output_path, tolerance=25):
    img = Image.open(input_path).convert("RGBA")
    data = np.array(img, dtype=np.int32)

    # Sample background color from top-left corner
    bg = data[0, 0, :3]
    print(f"  Detected background: RGB={bg}")

    # Remove pixels within tolerance of background color
    diff = np.abs(data[:, :, :3] - bg).max(axis=2)
    mask = diff < tolerance

    result = data.astype(np.uint8).copy()
    result[mask, 3] = 0

    Image.fromarray(result).save(output_path, "PNG")
    pct = 100 * mask.sum() / mask.size
    print(f"  ✅ Saved {output_path} — {mask.sum()} px transparent ({pct:.1f}%)")


if len(sys.argv) == 3:
    remove_bg(sys.argv[1], sys.argv[2])
else:
    print("Processing all 4 standard Stratio logos...\n")
    import os
    base = os.path.dirname(__file__)
    uploads = "/mnt/user-data/uploads"

    logos = [
        (f"{uploads}/Stratio_Logo_Black_and_Blue__PNG_.png", f"{base}/logo-dark.png"),
        (f"{uploads}/Stratio_Logo_White_and_Blue__PNG_.png", f"{base}/logo-white.png"),
        (f"{uploads}/Stratio_Logo_Black__PNG_.png",          f"{base}/logo-mono-dark.png"),
        (f"{uploads}/Stratio_Logo_White__PNG_.png",          f"{base}/logo-mono-white.png"),
    ]

    for src, dst in logos:
        print(f"{dst.split('/')[-1]}:")
        remove_bg(src, dst)
