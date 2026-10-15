"""Compare TPS43 pad placements on the right Chocofi half (Fusion model coords, mm).

Run: uv run --with shapely python3 Hardware/scripts/pad_placement.py
"""
import math

from shapely.affinity import rotate, translate
from shapely.geometry import box

PAD_L, PAD_W, PAD_R = 43.3, 40.3, 2.0  # TPS43 outline, corner radius
CLR, BEZEL = 0.3, 2.5  # pocket clearance, bezel width
INNER_WALL_X = 150.77
NANO = box(155.19, 2.21, 172.97, 35.23)
INDEX_HOME = (184.68, 10.61)
THUMB_CENTRE = (167.93, -29.78)


def keycap(x, y, angle):
    return rotate(translate(box(-8.75, -8.25, 8.75, 8.25), x, y), angle, origin=(x, y))


THUMB = keycap(167.93, -29.78, 30)
INDEX_BOTTOM = keycap(184.68, -6.39, 0)


def outline(length, width, grow):
    core = box(-(length / 2 - PAD_R), -(width / 2 - PAD_R), length / 2 - PAD_R, width / 2 - PAD_R)
    return core.buffer(PAD_R + grow, quad_segs=32)


def place(shape, cx, cy, angle):
    return translate(rotate(shape, angle, origin=(0, 0)), cx, cy)


def report(name, cx, cy, angle, length=PAD_L, width=PAD_W):
    tile = place(outline(length, width, CLR + BEZEL), cx, cy, angle)
    pocket = place(outline(length, width, CLR), cx, cy, angle)
    minx, miny, maxx, maxy = tile.bounds
    dist = lambda p: math.hypot(p[0] - cx, p[1] - cy)
    print(
        f"{name:30} centre ({cx:.1f}, {cy:.1f}) {angle:>3} deg | tile x {minx:.1f}..{maxx:.1f} y {miny:.1f}..{maxy:.1f}"
        f" | past wall {INNER_WALL_X - minx:.1f} | to index home {dist(INDEX_HOME):.1f} | to inner thumb {dist(THUMB_CENTRE):.1f}"
        f" | gap thumb {tile.distance(THUMB):.1f} index {tile.distance(INDEX_BOTTOM):.1f} | pocket over nano {pocket.intersection(NANO).area:.0f} mm2"
    )


def index_aligned(length, width, index_gap=1.9, thumb_gap=1.5):
    """0 deg pad: tile right edge `index_gap` from the index keycaps, then lowered until `thumb_gap` from the inner thumb keycap."""
    tile = outline(length, width, CLR + BEZEL)
    half_x = (tile.bounds[2] - tile.bounds[0]) / 2
    cx = 175.93 - index_gap - half_x
    for step in range(-300, 300):
        cy = step / 10
        if translate(tile, cx, cy).distance(THUMB) >= thumb_gap:
            return cx, cy


if __name__ == "__main__":
    report("v2 (Toucan, 30 deg)", 142.3, -6.2, 30)
    report("v3 long side along x", *index_aligned(PAD_L, PAD_W), 0)
    report("v3 long side along y", *index_aligned(PAD_W, PAD_L), 0, PAD_W, PAD_L)
