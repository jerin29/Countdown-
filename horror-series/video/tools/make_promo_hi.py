"""COUNTDOWN Hindi promo (1:41, 9:16) set to the full Hindi title song "दस घंटियाँ".
Song cuts in the song's own gaps (measured + Whisper-aligned): A = 14.4 → 70.9 s (hummed intro, verse 1, chorus 1),
B = 139.0 → end (verse 3, final chorus, outro). Reuses the builder in make_promo_full.py with Hindi panels and text.
Usage: python3 make_promo_hi.py
"""
import os
import make_promo_full as P

P.SONG = os.path.join(P.HS, "audio", "songs", "das-ghantiyan-FULL-hi.mp3")
P.PANELS = os.path.abspath(os.path.join(P.HS, "..", "animation-base", "out", "panels_hd_hi"))
P.A0, P.A1, P.B0 = 14.4, 70.9, 139.0
P.B_LEN = 183.93 - P.B0
P.DUR = round((P.A1 - P.A0) + P.B_LEN - P.XF, 2)          # 101.0 s
P.TT = 92.6
P.FONT = "Noto Sans Devanagari"
P.TITLE2, P.INFO, P.CTA = "काउंटडाउन", "10 एपिसोड · जल्द आ रहा है", "Follow करें · हर रात एक घंटी कम होगी"
P.OUTNAME = "COUNTDOWN_promo_fullsong_hi"
TT, DUR = P.TT, P.DUR
P.SHOTS = [
    (0.0, 3.2, "e01_p02", .50, .50, "push", ""), (3.2, 7.7, "e01_p12", .50, .45, "rise", ""),
    # verse 1
    (7.7, 10.8, "e01_p04", .20, .55, "push", ""), (10.8, 14.0, "e01_p10", .34, .50, "push", ""), (14.0, 17.0, "e01_p14", .58, .50, "stinger", ""),
    (17.0, 20.2, "e02_p11", .50, .56, "push", ""), (20.2, 23.4, "e03_p07", .52, .40, "push", "vhs"), (23.4, 26.6, "e03_p06", .50, .45, "push", ""),
    (26.6, 29.8, "e04_p08", .52, .50, "push", "sepia"), (29.8, 33.1, "e04_p12", .36, .55, "push", ""),
    # chorus 1
    (33.1, 36.0, "e05_p08", .50, .55, "push", "phone"), (36.0, 38.9, "e05_p11", .50, .35, "stinger", "phone"), (38.9, 41.8, "e06_p10", .50, .45, "push", ""),
    (41.8, 44.7, "e07_p06", .74, .45, "push", ""), (44.7, 47.6, "e07_p12", .50, .55, "push", ""), (47.6, 50.5, "e08_p03", .50, .55, "push", ""),
    (50.5, 53.4, "e08_p13", .62, .45, "rise", ""), (53.4, 56.1, "e09_p04", .45, .50, "drift", ""),
    # verse 3
    (56.1, 60.0, "e09_p10", .50, .45, "push", ""), (60.0, 64.0, "e09_p12", .62, .50, "stinger", ""), (64.0, 68.6, "e09_p11", .50, .45, "push", ""),
    (68.6, 73.0, "e10_p07", .47, .55, "push", ""), (73.0, 76.6, "e10_p08", .47, .55, "push", "vhs"), (76.6, 80.6, "e10_p10", .60, .45, "push", ""),
    # final chorus
    (80.6, 84.0, "e10_p09", .62, .45, "stinger", ""), (84.0, 87.4, "e10_p11", .55, .60, "drift", ""), (87.4, 90.2, "e10_p12", .50, .55, "push", ""),
    (90.2, TT, "e10_p13", .30, .45, "push", ""),
    (TT, DUR, "e01_p02", .50, .50, "title", ""),
]
P.LINES = [
    (2.8, 7.4, "मंजुमला का घंटाघर\\N40 साल से खामोश था।"),
    (8.0, 13.6, "एक रात, ठीक 3 बजे...\\Nवो दस बार बजा।"),
    (14.2, 16.8, "सिर्फ़ मीरा ने उसे सुना।"),
    (17.2, 23.0, "हर रात एक घंटी कम होगी।\\Nहर रात कोई एक गायब होगा।"),
    (23.6, 26.4, "और कोई उन्हें याद नहीं रखेगा।"),
    (39.0, 44.5, "वो कभी भागता नहीं...\\Nपर हर बार और करीब होता है।"),
    (50.6, 55.8, "गिनती शून्य होते ही\\Nजिसने सुना, वो उसका।"),
    (64.2, 68.4, "आख़िरी घंटी से पहले...\\Nमीरा को उसे उल्टा घुमाना होगा।"),
    (87.6, 92.3, "चालीस साल बाद...\\Nवो फिर जागेगा।"),
]
P.HITS = [(0.0, 1.0), (14.0, .7), (36.0, .6), (60.0, .7), (80.6, .7), (TT, 1.0)]

if __name__ == "__main__":
    P.main()
