"""Season 2 Instagram captions (48 posts) -> captions.json + captions.md"""
import json, os, re, datetime as dt
HERE = os.path.dirname(os.path.abspath(__file__)); S2 = os.path.dirname(HERE)
LINES = {l: json.load(open(os.path.join(S2, 'audio', 'lines', l + '.json')))['lines'] for l in ('ml', 'hi', 'ta')}
TITLES = {
 1: ('നാൽപത്', 'चालीस', 'நாற்பது', 'Forty'), 2: ('ടിക്കുന്ന കൈത്തണ്ട', 'टिक-टिक करती कलाई', 'டிக் டிக் மணிக்கட்டு', 'The Ticking Wrist'),
 3: ('ക്ലോക്കുകളുടെ നഗരം', 'घड़ियों का शहर', 'கடிகாரங்களின் நகரம்', 'City of Clocks'), 4: ('വൈകുന്ന പ്രതിബിംബം', 'देर से हिलती परछाईं', 'தாமதமான பிம்பம்', 'Late Reflection'),
 5: ('മായ്ച്ചുകളഞ്ഞ മകൾ', 'मिटाई गई बेटी', 'அழிக்கப்பட்ட மகள்', 'The Erased Daughter'), 6: ('നോക്കിനിൽക്കുന്നവർ', 'देखने वाले', 'பார்ப்பவர்கள்', 'Watchers'),
 7: ('നേഹയുടെ മുന്നറിയിപ്പ്', 'नेहा की चेतावनी', 'நேஹாவின் எச்சரிக்கை', "Neha's Warning"), 8: ('രണ്ടാമത്തെ ഗോപുരം', 'दूसरा घंटाघर', 'இரண்டாவது கோபுரம்', 'The Second Tower'),
 9: ('തിരിക്കരുത്', 'मत घुमाओ', 'சுற்றாதே', "Don't Wind It"), 10: ('ആമ്മച്ചി', 'अम्माची', 'அம்மாச்சி', 'Ammachi'),
 11: ('അർജുന്റെ ഉള്ളിൽ', 'अर्जुन के अंदर', 'அர்ஜுனுக்குள்', 'Inside Arjun'), 12: ('അവളുടെ പാട്ട്', 'उसका गीत', 'அவளின் பாடல்', "The Daughter's Song"),
 13: ('എല്ലാ ഘടികാരങ്ങളും നിലയ്ക്കുന്നു', 'सारी घड़ियाँ रुक गईं', 'எல்லா கடிகாரங்களும் நிற்கின்றன', 'Every Clock Stops'),
 14: ('അവളുടെ മുഖം', 'उसका चेहरा', 'அவள் முகம்', 'Her Face'), 15: ('പൂജ്യം', 'शून्य', 'பூஜ்ஜியம்', 'Zero')}
QUOTE = {1: 'e01_clara_line', 2: 'e02_meera_1', 4: 'e04_refl_1', 5: 'e05_ammachi_2', 6: 'e06_clara_1', 7: 'e07_neha_1', 8: 'e08_aadi_2',
         9: 'e09_arjun_1', 10: 'e10_ammachi_1', 11: 'e11_arjun_1', 12: 'e12_meera_2', 13: 'e13_aadi_1', 14: 'e14_clara_2', 15: 'e15_aadi_1'}
HAND = {(1, 'ml'): 'ഇത്തവണ പത്തല്ല, ആദി.',
        (3, 'ml'): 'എല്ലാ വാതിലിലും അയൽക്കാർ നിൽക്കുന്നു… എണ്ണിക്കൊണ്ട്.',
        (3, 'hi'): 'हर दरवाज़े पर पड़ोसी खड़े हैं… गिनती करते हुए।',
        (3, 'ta'): 'ஒவ்வொரு வாசலிலும் அண்டை வீட்டார்… எண்ணிக்கொண்டே.'}
EN3 = 'Every neighbour stands in their doorway... counting.'
import sys; sys.path.insert(0, os.path.join(S2, 'video', 'tools')); from subs import EN
T = {'ml': dict(ep='എപ്പിസോഡ്', next='അടുത്ത എപ്പിസോഡ് നാളെ രാത്രി 9 മണിക്ക് 🔔', fin='സീസൺ 2 ഫിനാലെ 🕰️ കണ്ടതിന് നന്ദി!',
                  hp='🎧 ഹെഡ്‌ഫോൺ വച്ച് കാണുക', fol='Follow ചെയ്യൂ, ഒരു എപ്പിസോഡും മിസ്സാക്കരുത് 👀', time='9:00 PM',
                  tags='#malayalamhorror #countdownseries #keralahorror #malayalamreels #horrorseries'),
     'hi': dict(ep='एपिसोड', next='अगला एपिसोड कल रात 9:20 बजे 🔔', fin='सीज़न 2 फ़िनाले 🕰️ देखने के लिए धन्यवाद!',
                  hp='🎧 हेडफ़ोन लगाकर देखें', fol='Follow करें, कोई एपिसोड मिस न हो 👀', time='9:20 PM',
                  tags='#hindihorror #horrorstory #countdownseries #hindireels #horrorseries'),
     'ta': dict(ep='எபிசோட்', next='அடுத்த எபிசோட் நாளை இரவு 9:40 மணிக்கு 🔔', fin='சீசன் 2 இறுதி எபிசோட் 🕰️ பார்த்ததற்கு நன்றி!',
                  hp='🎧 ஹெட்ஃபோன் போட்டுப் பாருங்கள்', fol='Follow செய்யுங்கள், எந்த எபிசோடையும் மிஸ் செய்யாதீர்கள் 👀', time='9:40 PM',
                  tags='#tamilhorror #tamilreels #countdownseries #horrorstory #horrorseries')}
CRED = 'Story: Jerin Joseph Sebastian · Created with Claude AI & vidIQ'
SONG = {'ml': ('നാൽപത് മണിയൊച്ച 🕰️ COUNTDOWN സീസൺ 2 ടൈറ്റിൽ സോങ്',
               'പത്തല്ല ഇനി… നാൽപത്.\nസീസൺ 2 നാളെ മുതൽ, എല്ലാ ദിവസവും രാത്രി 9 മണിക്ക് 🔔', 'Forty Chimes · Season 2 title song · Ep 1 tomorrow, 9 PM IST'),
        'hi': ('चालीस घंटियाँ 🕰️ COUNTDOWN सीज़न 2 टाइटल सॉन्ग',
               'अब दस नहीं… चालीस।\nसीज़न 2 कल से, हर रोज़ रात 9:20 बजे 🔔', 'Forty Chimes · Season 2 title song · Ep 1 tomorrow, 9:20 PM IST'),
        'ta': ('நாற்பது மணியோசை 🕰️ COUNTDOWN சீசன் 2 டைட்டில் பாடல்',
               'இனி பத்து இல்லை… நாற்பது.\nசீசன் 2 நாளை முதல், தினமும் இரவு 9:40 மணிக்கு 🔔', 'Forty Chimes · Season 2 title song · Ep 1 tomorrow, 9:40 PM IST')}
LI = {'ml': 0, 'hi': 1, 'ta': 2}
clean = lambda s: re.sub(r'\[[^\]]*\]\s*', '', s).strip()


def quote(n, lang):
    if (n, lang) in HAND: return HAND[(n, lang)]
    return clean(LINES[lang].get(QUOTE[n], [None, ''])[1])


posts = []
for lang, start, tm in (('ml', dt.date(2026, 12, 9), '21:00'), ('hi', dt.date(2026, 12, 10), '21:20'), ('ta', dt.date(2026, 12, 10), '21:40')):
    t = T[lang]; a, b, en = SONG[lang]
    posts.append(dict(lang=lang, kind='song', date=str(start), time=tm, file=f'song/video/out/COUNTDOWN_S2_title_song_promo_{lang}.mp4',
                      caption=f"{a}\n\n{b}\n\n{t['hp']}\n{t['fol']}\n\n{en}\n{CRED}\n\n{t['tags']} #titlesong"))
    for n in range(1, 16):
        d = start + dt.timedelta(days=n); q = quote(n, lang); ti = TITLES[n]
        enq = (EN3 if n == 3 else EN[QUOTE[n]]).replace("Chechi", {"hi": "Didi", "ta": "Akka"}.get(lang, "Chechi"))
        cap = (f"🕰️ COUNTDOWN S2 · {t['ep']} {n}/15 · {ti[LI[lang]]}\n\n“{q}”\n\n{t['fin'] if n == 15 else t['next']}\n{t['hp']}\n{t['fol']}\n\n"
               f"Ep {n}/15 · {ti[3]} · “{enq}”\n{CRED}\n\n{t['tags']}")
        posts.append(dict(lang=lang, kind='episode', ep=n, date=str(d), time=tm, file=f'video/COUNTDOWN_S2_ep{n:02d}_{lang}.mp4', caption=cap))
posts.sort(key=lambda p: (p['date'], p['time']))
json.dump(posts, open(os.path.join(HERE, 'captions.json'), 'w'), ensure_ascii=False, indent=1)
with open(os.path.join(HERE, 'captions.md'), 'w') as f:
    f.write('# COUNTDOWN Season 2 · Instagram posts (48) · times in IST\n\n')
    for p in posts:
        f.write(f"## {p['date']} {p['time']} · {p['lang'].upper()} · {'Title song' if p['kind'] == 'song' else 'Ep ' + str(p['ep'])}\n`{p['file']}`\n```\n{p['caption']}\n```\n\n")
print(len(posts)); missing = [p['file'] for p in posts if not os.path.exists(os.path.join(S2, p['file']))]; print('missing', missing)
