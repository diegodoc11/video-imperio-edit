# -*- coding: utf-8 -*-
# RECETA DE REFERENCIA (no se corre tal cual): es el build.py REAL de un reel de Diego Osorio hecho con esta skill.
# Úsala para copiar efectos avanzados a tu build.py (los textos, frases y fotos de prueba son de ese video; no vienen incluidos).
# Estilo: fucsia. Lo más reutilizable: título a mano, karaoke fucsia, tarjeta de logo que entra en el ordinal + ficha "Acerca de", video real a pantalla completa, tarjeta x2.
# Reel "Se nota cuando una web fue hecha con IA" — modelado sobre la referencia de las 5 skills (ref3):
#   título escrito a mano (mayúsculas), subtítulos con la palabra activa resaltada en fucsia, por cada skill
#   una tarjeta de logo y luego su ficha "Acerca de" (estilo GitHub), cortes con zoom alterno, CTA "COMENTA".
import sys, os, json, html
SKILL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_work', 'skill.txt'), encoding='utf-8').read().strip()
sys.path.insert(0, os.path.join(SKILL, 'scripts'))
import kit as K

P = os.path.dirname(os.path.abspath(__file__))
DO_AUDIO = '--no-audio' not in sys.argv
CUT = json.load(open(os.path.join(P, 'cutmap.json')))
DUR = round(CUT['dur'], 3); W, H = 1080, 1920
FIX = {'cloud': 'Claude', 'playrack': 'Playwright', 'nota': 'nota a', '2000': '$2.000', 'tops': 'top'}
WD = K.load_words(P, FIX)
# quitar la "y" duplicada que quedó al empalmar la frase repetida
WD = [w for i, w in enumerate(WD) if not (i > 0 and K.norm(w['text']) == 'y' and K.norm(WD[i - 1]['text']) == 'y')]
for w in WD:
    if K.norm(w['text']) == '2000': w['text'] = '$2.000'
f = lambda ph, after=0: K.find(WD, ph, after)
fe = lambda ph, after=0: K.find_end(WD, ph, after)
FACE = K.Face(P, crop=K.CROP_WM)
ZOOM_B = 1.12
st = lambda a, b: FACE.safe_top(a, b, ZOOM_B)
MAG = '#D304C2'
init, tw, parts, sfx = [], [], [], []

def show(el, t, dur=0.22, fx='pop', g=0.18):
    init.append(f'gsap.set("{el}",{{opacity:0,scale:0.94}});')
    tw.append(f'tl.to("{el}",{{opacity:1,scale:1,duration:{dur},ease:"power2.out"}},{t:.3f});')
    if fx: sfx.append((t, fx + '.wav', g))

def hide(el, t, dur=0.14):
    tw.append(f'tl.to("{el}",{{opacity:0,duration:{dur},ease:"power1.in"}},{t - dur:.3f});')

def place(eid, t0, t1, inner, cls, dy=0):
    top = st(t0, t1) + dy
    parts.append(f'<div id="{eid}" class="{cls}" style="top:{top}px">{inner}</div>')
    show('#' + eid, t0); hide('#' + eid, t1)

# ================= TÍTULO (desde el segundo 0) =================
t_aqui = f('Aquí'); t_prim = f('Primera')
top = st(0, t_aqui)
parts.append(f'<div id="h1" class="hand" style="top:{top + 60}px">5 SKILLS DE CLAUDE QUE HACEN<br>QUE TU WEB NO PAREZCA<br>HECHA CON IA</div>')
init.append('gsap.set("#h1",{opacity:1});'); tw.append(f'tl.set("#h1",{{opacity:0}},{t_aqui - 0.02:.3f});')
top = st(t_aqui, t_prim)
parts.append(f'<div id="h2" class="hand sm" style="top:{top + 40}px">5 SKILLS DE CLAUDE 🔥</div>')
init.append('gsap.set("#h2",{opacity:0});'); tw.append(f'tl.set("#h2",{{opacity:1}},{t_aqui:.3f});tl.set("#h2",{{opacity:0}},{t_prim - 0.02:.3f});')

# ================= SKILLS: logo -> "Acerca de" =================
lg_pw = K.logo_svg('playwright', '#2EAD33')
SK = [
 ('Awesome', 'Una colección', 'Dos',
  '<div class="logo dark aw"><span class="col">Collection</span><div class="awt">Awesome<br>DESIGN.md</div></div>',
  'Una colección de archivos DESIGN.md con los sistemas de diseño de marcas populares. Suelta uno en tu proyecto y tu IA genera una interfaz que encaja.', 'getdesign.md'),
 ('Impeccable', 'Guía', 'Tres',
  '<div class="logo dark imp"><span class="slash"></span><span class="impt">IMPECCABLE</span></div>',
  'El lenguaje de diseño que hace que tu IA sea mucho mejor diseñando.', 'impeccable.style'),
 ('Taste', 'Enseña', 'Cuarta',
  '<div class="logo light ts"><div class="tsrow"><span class="tsico">⟁</span><span class="tst">Taste Skill</span></div><div class="tss">The Anti-Slop Frontend Framework for AI Agents</div></div>',
  'Le da buen gusto a tu IA. Impide que genere diseños aburridos y genéricos.', 'tasteskill.dev'),
 ('Emil', 'Una joya', 'quinta',
  '<div class="logo light em"><div class="emn">Emil Kowalski</div><div class="ems">Design Engineer</div></div>',
  'Habilidades para diseñadores e ingenieros: animaciones fluidas y microinteracciones de alto nivel.', 'emilkowal.ski/skill'),
 ('Playwright', 'Conecta', 'Con este mismo',
  f'<div class="logo dark pw"><span class="pwi">{lg_pw}</span><span class="pwt">Playwright</span></div>',
  'Framework para pruebas y automatización web. Prueba Chromium, Firefox y WebKit con una sola API.', 'playwright.dev'),
]
ORD = ['Primera', 'Dos', 'Tres', 'Cuarta', 'quinta']
prev = 0
for n, (kw, about_kw, nxt_kw, logo_html, desc, url) in enumerate(SK, 1):
    t0 = f(ORD[n - 1], prev) - 0.05; prev = t0 + 0.1; t1 = f(about_kw, t0); t2 = f(nxt_kw, t1) - 0.08
    place(f'lg{n}', t0, t1, logo_html, 'card', dy=40)
    place(f'ab{n}', t1, t2, f'<div class="about"><div class="abh">Acerca de</div><div class="abd">{html.escape(desc)}</div>'
                            f'<div class="abl">🔗 <span>{url}</span></div></div>', 'card', dy=20)

# ================= PRUEBA: la web real del glamping (pantalla completa) =================
g0 = f('Con este mismo'); g1 = f('El resultado') - 0.05
parts.append(f'<div id="glw" class="full"><video id="glv" class="clip" data-start="{g0:.3f}" data-duration="{g1 - g0:.3f}" data-media-start="0" data-track-index="1" src="assets/glamping.mp4" muted playsinline></video>'
             f'<div class="chip" id="glc">🌐 laquintaglamping.co · hecha con este combo</div></div>')
init.append('gsap.set("#glw",{opacity:0,scale:1.12});')
tw.append(f'tl.to("#glw",{{opacity:1,scale:1,duration:0.35,ease:"power3.out"}},{g0:.3f});')
tw.append(f'tl.to("#glw",{{opacity:0,duration:0.15}},{g1 - 0.15:.3f});')
sfx.append((g0, 'whoosh.wav', 0.5))
show('#glc', f('quedó como') if True else g0 + 0.6, fx='pop', g=0.2)

# ================= RESULTADO: x2 facturación + testimonio =================
r0 = f('El resultado'); r1 = f('Y no te las') - 0.05 if True else 0
place('res', r0, r1, f'''<div class="stat"><div class="x2">x2</div><div class="stt">facturación<br><b>en 30 días</b> 📈</div></div>''', 'card', dy=10)
sfx.append((f('dobló'), 'ding.wav', 0.25))

# ================= listas para copiar y pegar =================
c0 = f('Y no te las'); c1 = f('Comenta') - 0.05
top = st(c0, c1)
parts.append(f'<div id="cp" class="hand sm" style="top:{top + 60}px">LISTAS PARA COPIAR Y PEGAR 📋</div>')
show('#cp', f('listas', c0), fx='pop', g=0.18); hide('#cp', c1)

# ================= CTA =================
a = f('Comenta'); top = st(a, DUR)
parts.append(f'<div id="cta" class="hand" style="top:{top + 70}px">COMENTA “CLASE”</div>')
show('#cta', a, fx='pop', g=0.3)

# ================= ZOOM alterno en cada corte =================
ox, oy = int(FACE.cx), int(FACE.cy)
acc = 0.0; bounds = []
for s0, s1 in CUT['keep']:
    acc += s1 - s0; bounds.append(round(acc, 3))
init.append('gsap.set("#cam",{scale:1});'); z = 1.0
for t in bounds[:-1]:
    z = ZOOM_B if z == 1.0 else 1.0
    tw.append(f'tl.set("#cam",{{scale:{z}}},{t:.3f});')

# ================= SUBTÍTULOS: 3-4 palabras, palabra activa en fucsia (ref3) =================
lines = []; cur = []
for w in WD:
    if w['start'] < 0: continue
    cur.append(w); txt = ' '.join(x['text'] for x in cur)
    if w['text'][-1:] in '.?!,' and len(cur) >= 2 or len(cur) >= 4 or len(txt) >= 24:
        lines.append(cur); cur = []
if cur: lines.append(cur)
caps = []
for li, ln in enumerate(lines):
    s = ln[0]['start']; e = ln[-1]['end']
    nxt = lines[li + 1][0]['start'] if li + 1 < len(lines) else DUR
    hide_t = min(e + 0.25, nxt - 0.03)
    spans = ''.join(f'<span id="w{li}_{k}" class="cw">{html.escape(x["text"])}</span> ' for k, x in enumerate(ln))
    caps.append(f'<div id="L{li}" class="cap">{spans}</div>')
    init.append(f'gsap.set("#L{li}",{{opacity:0}});')
    tw.append(f'tl.set("#L{li}",{{opacity:1}},{max(0, s - 0.04):.3f});tl.set("#L{li}",{{opacity:0}},{hide_t:.3f});')
    for k, x in enumerate(ln):
        e2 = ln[k + 1]['start'] if k + 1 < len(ln) else min(x['end'] + 0.1, hide_t)
        tw.append(f'tl.set("#w{li}_{k}",{{backgroundColor:"{MAG}"}},{x["start"]:.3f});tl.set("#w{li}_{k}",{{backgroundColor:"rgba(211,4,194,0)"}},{e2:.3f});')

if DO_AUDIO:
    K.mix_audio(P, DUR, 'chill-luxury.mp3', music_start=0.0, music_gain=0.30, sfx=sfx)

K.copy_fonts(P, ['patrickhandsc-400', 'poppins-700', 'poppins-800', 'inter-400', 'inter-600', 'inter-700', 'caveat-700', 'jetbrainsmono-600'])
CSS = K.font_faces([('Hand', 400, 'patrickhandsc-400'), ('Poppins', 700, 'poppins-700'), ('Poppins', 800, 'poppins-800'),
                    ('Inter', 400, 'inter-400'), ('Inter', 600, 'inter-600'), ('Inter', 700, 'inter-700'), ('Caveat', 700, 'caveat-700'),
                    ('JBM', 600, 'jetbrainsmono-600')])
HTML = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
{CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
#root{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#000;font-family:"Inter",sans-serif}}
#cam{{position:absolute;inset:0;transform-origin:{ox}px {oy}px}}
#v{{position:absolute;inset:0;width:{W}px;height:{H}px;object-fit:cover}}
/* títulos escritos a mano */
.hand{{position:absolute;left:0;width:{W}px;text-align:center;z-index:30;font-family:"Hand";font-size:74px;line-height:1.08;color:#fff;letter-spacing:1px;
  text-shadow:0 0 2px #000,0 2px 2px rgba(0,0,0,.9),0 4px 14px rgba(0,0,0,.55);-webkit-text-stroke:1.5px rgba(0,0,0,.55);paint-order:stroke fill}}
.hand.sm{{font-size:64px}}
#cta{{font-size:96px}}
/* tarjetas */
.card{{position:absolute;left:0;width:{W}px;display:flex;justify-content:center;z-index:30}}
.logo{{border-radius:22px;padding:30px 46px;box-shadow:0 0 0 5px rgba(255,255,255,.75),0 0 34px rgba(255,255,255,.55),0 18px 40px rgba(0,0,0,.45)}}
.logo.dark{{background:#0b0b0c;color:#fff}} .logo.light{{background:#fff;color:#111}}
.aw{{position:relative;padding:40px 60px 34px}} .awt{{font-family:"Inter";font-weight:400;font-size:74px;line-height:1.02;letter-spacing:1px}}
.col{{position:absolute;right:26px;top:10px;font-family:"Caveat";font-size:40px;color:#fff}}
.imp{{display:flex;align-items:center;gap:26px;padding:40px 60px}} .slash{{width:46px;height:96px;background:#F5C518;transform:skewX(-18deg)}}
.impt{{font-family:"Inter";font-weight:600;font-size:64px;letter-spacing:12px}}
.tsrow{{display:flex;align-items:center;gap:20px}} .tsico{{font-size:76px;line-height:1}} .tst{{font-family:"Inter";font-weight:700;font-size:78px}}
.tss{{font-family:"Inter";font-weight:400;font-size:26px;color:#555;margin-top:6px;text-align:center}}
.em{{padding:34px 60px}} .emn{{font-family:"Inter";font-weight:600;font-size:74px}} .ems{{font-family:"Inter";font-weight:400;font-size:66px;color:#555}}
.pw{{display:flex;align-items:center;gap:24px;padding:34px 56px}} .pwi svg{{width:100px;height:100px}} .pwt{{font-family:"Inter";font-weight:600;font-size:78px}}
.about{{width:900px;background:#0d1117;border:2px solid #30363d;border-radius:20px;padding:34px 40px;box-shadow:0 0 0 5px rgba(255,255,255,.7),0 0 30px rgba(255,255,255,.45),0 18px 40px rgba(0,0,0,.5)}}
.abh{{font-family:"Inter";font-weight:700;font-size:44px;color:#f0f6fc;margin-bottom:16px}}
.abd{{font-family:"Inter";font-weight:400;font-size:40px;line-height:1.38;color:#c9d1d9}}
.abl{{margin-top:18px;font-family:"Inter";font-weight:600;font-size:36px;color:#4493f8}}
/* prueba a pantalla completa */
.full{{position:absolute;inset:0;z-index:35;background:#000}}
.full video{{position:absolute;inset:0;width:{W}px;height:{H}px;object-fit:cover}}
.chip{{position:absolute;left:50%;transform:translateX(-50%);bottom:430px;white-space:nowrap;background:rgba(10,10,12,.88);color:#fff;font-family:"Poppins";font-weight:700;font-size:40px;padding:16px 30px;border-radius:40px;border:2px solid rgba(255,255,255,.25)}}
.stat{{display:flex;align-items:center;gap:30px;background:#fff;border-radius:26px;padding:26px 46px;box-shadow:0 0 0 5px rgba(255,255,255,.7),0 18px 40px rgba(0,0,0,.45)}}
.x2{{font-family:"Poppins";font-weight:800;font-size:150px;line-height:1;color:{MAG}}}
.stt{{font-family:"Poppins";font-weight:700;font-size:52px;line-height:1.15;color:#111}} .stt b{{font-weight:800}}
/* subtítulos */
.cap{{position:absolute;left:0;width:{W}px;top:1600px;text-align:center;z-index:45;font-family:"Poppins";font-weight:700;font-size:52px;color:#fff;
  text-shadow:0 3px 8px rgba(0,0,0,.85),0 0 2px #000}}
.cw{{padding:2px 10px;border-radius:10px;background:rgba(211,4,194,0)}}
{K.CROP_CSS}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
  <div id="cam" data-layout-allow-overflow><div id="crop" data-layout-allow-overflow><video id="v" class="clip" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="0" src="cut.mp4" muted playsinline></video></div></div>
  {''.join(parts)}
  {''.join(caps)}
  <audio id="aud" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="2" src="final_audio.wav" data-volume="1"></audio>
</div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script>const tl=gsap.timeline({{paused:true}});window.__timelines={{"main":tl}};
{chr(10).join(init)}
{chr(10).join(tw)}
</script></body></html>'''
open(os.path.join(P, 'index.html'), 'w', encoding='utf-8').write(HTML)
print(f'OK index.html | {DUR}s | líneas {len(lines)} | efectos {len(sfx)}')
