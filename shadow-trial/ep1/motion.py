"""2.5D motion renderer: depth-parallax camera, handheld shake, particles, light effects, whip/flash transitions.
render_shot(spec) writes one 1920x1080 mp4 clip."""
import numpy as np, cv2, subprocess, math

W, H, FPS = 1920, 1080, 24
BW, BH = 2400, 1350  # working canvas (margin for camera moves)


def ease(x):  # smoothstep
    x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)


def shake_fn(seed, amp, freq=1.0):
    r = np.random.default_rng(seed); ph = r.uniform(0, 6.28, 6); fr = r.uniform(0.6, 2.2, 6) * freq
    return lambda t: amp * sum(math.sin(t * fr[i] * 6.28 + ph[i]) for i in range(3)) / 3, \
           lambda t: amp * sum(math.sin(t * fr[i] * 6.28 + ph[i]) for i in range(3, 6)) / 3


class Particles:
    def __init__(self, kind, n, seed):
        r = self.r = np.random.default_rng(seed); self.kind = kind
        self.p = np.c_[r.uniform(0, W, n), r.uniform(0, H, n)]
        self.v = {"rain": np.c_[r.uniform(4, 8, n), r.uniform(55, 80, n)],
                  "embers": np.c_[r.uniform(-1.5, 1.5, n), r.uniform(-6, -2, n)],
                  "dust": np.c_[r.uniform(-0.6, 0.6, n), r.uniform(-0.4, 0.4, n)]}[kind]
        self.s = r.uniform(0.4, 1.0, n)

    def draw(self, img, t):
        ov = np.zeros_like(img)
        self.p += self.v * (1 + 0.3 * np.sin(t * 3 + self.s[:, None] * 9) * (self.kind == "embers"))
        self.p[:, 0] %= W; self.p[:, 1] %= H
        for (x, y), (vx, vy), s in zip(self.p, self.v, self.s):
            if self.kind == "rain":
                cv2.line(ov, (int(x), int(y)), (int(x - vx * 0.5), int(y - vy * 0.5)), (int(150 * s),) * 3, 1, cv2.LINE_AA)
            elif self.kind == "embers":
                c = (int(40 * s), int(140 * s), int(255 * s)); cv2.circle(ov, (int(x), int(y)), int(1 + 2 * s), c, -1, cv2.LINE_AA)
            else:
                cv2.circle(ov, (int(x), int(y)), int(1 + 2 * s), (int(90 * s),) * 3, -1, cv2.LINE_AA)
        if self.kind != "rain": ov = cv2.GaussianBlur(ov, (0, 0), 1.6) * 1.8
        return np.clip(img + ov.astype(np.float32), 0, 255)


def render_shot(spec):
    s = spec; dur = s["dur"]; nf = int(round(dur * FPS)); out = s["out"]
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "fast", "-pix_fmt", "yuv420p", out],
                          stdin=subprocess.PIPE)
    if s.get("img") is None:
        parts = Particles("dust", 60, 1) if s.get("dust") else None
        for f in range(nf):
            fr = np.zeros((H, W, 3), np.float32)
            if parts: fr = parts.draw(fr, f / FPS) * 0.5
            ff.stdin.write(fr.astype(np.uint8).tobytes())
        ff.stdin.close(); ff.wait(); return out

    img = cv2.imread(s["img"]);
    if s.get("crop"): x, y, w, h = s["crop"]; img = img[y:y + h, x:x + w]
    dep = cv2.imread(s["depth"], cv2.IMREAD_GRAYSCALE)
    if s.get("crop"): dep = dep[y:y + h, x:x + w]
    img = cv2.resize(img, (BW, BH), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    dep = cv2.GaussianBlur(cv2.resize(dep, (BW, BH)).astype(np.float32) / 255.0, (0, 0), 6)
    warm = None
    if s.get("fire"):  # mask of bright warm pixels for flicker
        b, g, r = img[..., 0], img[..., 1], img[..., 2]
        warm = np.clip((r - b) / 120.0, 0, 1) * np.clip((r + g) / 400.0, 0, 1); warm = cv2.GaussianBlur(warm, (0, 0), 15)[..., None]

    sx, sy = shake_fn(s.get("seed", 1), s.get("shake", 4.0), s.get("shake_freq", 1.0))
    parts = [Particles(k, n, s.get("seed", 1) + i) for i, (k, n) in enumerate(s.get("particles", []))]
    uu, vv = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    cam = s["cam"]  # dict of start/end values: z, x, y, rot, px, py, dolly

    for f in range(nf):
        t = f / FPS; e = ease(t / dur) if s.get("ease", True) else t / dur
        z = cam["z"][0] + (cam["z"][1] - cam["z"][0]) * e
        for (ht, amp) in s.get("punches", []):  # beat punch-ins
            if 0 <= t - ht < 0.6: z *= 1 + amp * math.exp(-(t - ht) * 7)
        cx = BW / 2 + cam.get("x", (0, 0))[0] + (cam.get("x", (0, 0))[1] - cam.get("x", (0, 0))[0]) * e + sx(t)
        cy = BH / 2 + cam.get("y", (0, 0))[0] + (cam.get("y", (0, 0))[1] - cam.get("y", (0, 0))[0]) * e + sy(t)
        rot = math.radians(cam.get("rot", (0, 0))[0] + (cam.get("rot", (0, 0))[1] - cam.get("rot", (0, 0))[0]) * e + 0.15 * sx(t) / max(1, s.get("shake", 4)))
        hit_shake = 0
        for (ht, amp) in s.get("hits", []):
            if t >= ht: hit_shake += amp * math.exp(-(t - ht) * 3.5)
        cx += hit_shake * math.sin(t * 61); cy += hit_shake * math.cos(t * 47)
        # output pixel -> base coords (inverse of zoom/rotate around center)
        sc = (BW / 1.12) / W / z  # base px per output px (12% margin at z=1)
        du, dv = uu - W / 2, vv - H / 2
        cr, sr_ = math.cos(rot), math.sin(rot)
        bx = cx + (du * cr - dv * sr_) * sc
        by = cy + (du * sr_ + dv * cr) * sc
        d = cv2.remap(dep, bx, by, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        px = cam.get("px", (0, 0))[0] + (cam.get("px", (0, 0))[1] - cam.get("px", (0, 0))[0]) * e
        py = cam.get("py", (0, 0))[0] + (cam.get("py", (0, 0))[1] - cam.get("py", (0, 0))[0]) * e
        dol = cam.get("dolly", (0, 0))[0] + (cam.get("dolly", (0, 0))[1] - cam.get("dolly", (0, 0))[0]) * e
        dd = d - 0.5
        bx = bx - dd * px - (bx - cx) * dd * dol
        by = by - dd * py - (by - cy) * dd * dol
        fr = cv2.remap(img, bx, by, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

        bright = 1.0; tint = None
        if warm is not None:
            fl = 1 + 0.35 * (math.sin(t * 23) * 0.5 + math.sin(t * 37 + 1) * 0.3 + math.sin(t * 11) * 0.2)
            wm = cv2.remap(warm[..., 0], bx, by, cv2.INTER_LINEAR)[..., None]
            fr = fr * (1 + (fl - 1) * wm)
        fx = s.get("fx")
        if fx == "police":
            ph = (t * 2.2) % 1
            col = np.array([255, 60, 30] if ph < 0.5 else [30, 40, 255], np.float32)
            side = np.clip((uu - W / 2) / (W / 2) * (1 if ph < 0.5 else -1), 0, 1)[..., None]
            fr = fr + col * side * 0.18 * (0.6 + 0.4 * math.sin(t * 30))
        elif fx == "club":
            beat = (t + s.get("t0", 0) - 42) % (60 / 124)
            bright *= 1 + 0.18 * math.exp(-beat * 9)
            hue = np.array([255, 40, 200] if int((t + s.get("t0", 0)) / (60 / 124 * 4)) % 2 else [255, 120, 40], np.float32)
            fr = fr + hue * 0.05 * math.exp(-beat * 6)
        elif fx == "lightsoff":
            steps = [1.0, 2.4, 3.8, 5.2, 6.6]
            k = sum(1 for st in steps if t >= st); bright *= max(0.12, 1 - 0.18 * k)
            if any(0 <= t - st < 0.12 for st in steps): bright *= 1.6
            bright *= 1 - 0.08 * (math.sin(t * 50) > 0.8)
        elif fx == "stun":
            if 0.6 <= t <= 2.8 and math.sin(t * 55) > 0.4:
                fr = fr + np.array([255, 180, 60], np.float32) * 0.35
            if t > 3.4: bright *= max(0.0, 1 - (t - 3.4) * 3)
        elif fx == "basement":
            bright *= 1 - 0.25 * (math.sin(t * 17) > 0.93) - 0.15 * (math.sin(t * 7.3) > 0.97)
        for (ht, amp) in s.get("flashes", []):
            if t >= ht: fr = fr + 255 * amp * math.exp(-(t - ht) * 6)
        fr = fr * bright
        for p in parts: fr = p.draw(fr, t)
        # chromatic aberration on hits
        ca = sum(amp * 14 * math.exp(-(t - ht) * 4) for ht, amp in s.get("hits", []) if t >= ht) / 10
        ca += s.get("ca", 0)
        if ca > 0.5:
            k = int(ca); fr[..., 2] = np.roll(fr[..., 2], k, 1); fr[..., 0] = np.roll(fr[..., 0], -k, 1)
        # whip transitions (directional blur)
        wi, wo = s.get("whip_in", 0), s.get("whip_out", 0)
        amt = 0
        if wi and t < 0.25: amt = (1 - t / 0.25)
        if wo and t > dur - 0.25: amt = (t - (dur - 0.25)) / 0.25
        if amt > 0.02:
            k = int(9 + 140 * amt) | 1; ker = np.zeros((1, k), np.float32); ker[0] = 1.0 / k
            fr = cv2.filter2D(fr, -1, ker)
        if s.get("fade_in") and t < s["fade_in"]: fr *= t / s["fade_in"]
        if s.get("fade_out") and t > dur - s["fade_out"]: fr *= (dur - t) / s["fade_out"]
        ff.stdin.write(np.clip(fr, 0, 255).astype(np.uint8).tobytes())
    ff.stdin.close(); ff.wait()
    return out
