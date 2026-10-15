"""Print triangle count, bounding box and enclosed volume of binary STL files."""
import struct
import sys

for path in sys.argv[1:]:
    data = open(path, "rb").read()
    n = struct.unpack_from("<I", data, 80)[0]
    lo = [1e9] * 3
    hi = [-1e9] * 3
    vol = 0.0
    for i in range(n):
        v = struct.unpack_from("<12f", data, 84 + i * 50)
        a, b, c = v[3:6], v[6:9], v[9:12]
        for p in (a, b, c):
            for k in range(3):
                lo[k] = min(lo[k], p[k])
                hi[k] = max(hi[k], p[k])
        vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0]) + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6
    size = [round(hi[k] - lo[k], 2) for k in range(3)]
    print(f"{path.split('/')[-1]}: {n} tris, size {size} mm, z {lo[2]:.2f}..{hi[2]:.2f}, volume {vol / 1000:.3f} cm3")
