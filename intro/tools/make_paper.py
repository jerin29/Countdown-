# Seeded paper texture (grain + fibres + soft blotches), grayscale PNG 1080x1920, mid-grey centred for overlay blending.
import numpy as np, subprocess, sys
W, H = 1080, 1920; rng = np.random.default_rng(7)
def blur(a, k):
    ker = np.ones(k) / k
    a = np.apply_along_axis(lambda r: np.convolve(r, ker, 'same'), 1, a)
    return np.apply_along_axis(lambda c: np.convolve(c, ker, 'same'), 0, a)
low = blur(rng.standard_normal((H // 8, W // 8)), 9)
low = np.kron(low, np.ones((8, 8)))[:H, :W]; low = low / (np.abs(low).max() + 1e-9)
grain = rng.standard_normal((H, W)) * 0.5 + blur(rng.standard_normal((H // 2, W // 2)), 3).repeat(2, 0).repeat(2, 1)[:H, :W] * 1.2
fib = np.zeros((H, W))
for _ in range(1400):  # short fibres
    x, y = rng.uniform(0, W), rng.uniform(0, H); ang = rng.uniform(0, np.pi); ln = rng.uniform(8, 40)
    for s in np.linspace(0, ln, int(ln)):
        xi, yi = int(x + np.cos(ang) * s), int(y + np.sin(ang) * s)
        if 0 <= xi < W and 0 <= yi < H: fib[yi, xi] += rng.choice([-1, 1]) * 0.8
tex = 128 + low * 18 + grain * 9 + fib * 14
img = np.clip(tex, 0, 255).astype(np.uint8)
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'gray', '-s', f'{W}x{H}', '-i', '-', sys.argv[1]], stdin=subprocess.PIPE)
p.communicate(img.tobytes()); print('ok')
