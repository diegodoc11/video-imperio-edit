# -*- coding: utf-8 -*-
# RECETA DE REFERENCIA (no se corre tal cual): es el build.py REAL de un reel de Diego Osorio hecho con esta skill.
# Úsala para copiar efectos avanzados a tu build.py (los textos, frases y fotos de prueba son de ese video; no vienen incluidos).
# Estilo: tablero. Lo más reutilizable: sticker blanco del gancho, pizarra con write_on() y draw() (círculos, subrayados, ramas), testimonios con destello + zoom + barrido, burbuja de chat, CTA en stickers.
# Reel "La forma más rápida de ganar dinero con IA" — modelado sobre la referencia del tablero (ref1):
#   sticker blanco estilo Instagram en el gancho, subtítulos de UNA palabra en mayúsculas, "tablero" con
#   palabras escritas a mano que aparecen al decirlas, prueba real con flash+zoom, CTA en stickers blancos.
# Todo el apoyo va DEBAJO de la barbilla (face.json) salvo la prueba a pantalla completa.
import sys, os, json, html
SKILL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_work', 'skill.txt'), encoding='utf-8').read().strip()
sys.path.insert(0, os.path.join(SKILL, 'scripts'))
import kit as K

P = os.path.dirname(os.path.abspath(__file__))
PREVIEW_AUDIO = '--no-audio' not in sys.argv
CUT = json.load(open(os.path.join(P, 'cutmap.json')))
DUR = round(CUT['dur'], 3); W, H = 1080, 1920
FIX = {'cloud': 'Claude', 'públicalos': 'Publícalo', 'chatgpt': 'ChatGPT'}
WD = K.load_words(P, FIX)
# dice 'el chico o chica IA' (whisper oye 'chico' dos veces)
for i in range(len(WD) - 2):
    if [K.norm(WD[i]['text']), K.norm(WD[i + 1]['text']), K.norm(WD[i + 2]['text'])] == ['chico', 'o', 'chico']:
        WD[i + 2]['text'] = 'chica'
f = lambda ph, after=0: K.find(WD, ph, after)
fe = lambda ph, after=0: K.find_end(WD, ph, after)
FACE = K.Face(P)
ZOOM_B = 1.10   # zoom alterno en los cortes
st = lambda a, b: FACE.safe_top(a, b, ZOOM_B)

INK = '#1d1d1f'; RED = '#E53935'; BLUE = '#1E5BD7'; GREEN = '#1B9E4B'
init, tw, html_parts, sfx = [], [], [], []

def show(el, t, dur=0.28, ease='back.out(1.6)', fx='pop', g=0.30, sc=0.9):
    init.append(f'gsap.set("{el}",{{opacity:0,scale:{sc}}});')
    tw.append(f'tl.to("{el}",{{opacity:1,scale:1,duration:{dur},ease:"{ease}"}},{t:.3f});')
    if fx: sfx.append((t, fx + '.wav', g))

def hide(el, t, dur=0.18):
    tw.append(f'tl.to("{el}",{{opacity:0,duration:{dur},ease:"power1.in"}},{t - dur:.3f});')

def write_on(el, t, dur=0.45):
    init.append(f'gsap.set("{el}",{{clipPath:"inset(0% 100% 0% 0%)"}});')
    tw.append(f'tl.to("{el}",{{clipPath:"inset(0% 0% 0% 0%)",duration:{dur},ease:"none"}},{t:.3f});')

def draw(el, t, length, dur=0.45):
    init.append(f'gsap.set("{el}",{{strokeDasharray:{length},strokeDashoffset:{length}}});')
    tw.append(f'tl.to("{el}",{{strokeDashoffset:0,duration:{dur},ease:"power1.inOut"}},{t:.3f});')

def board(bid, t0, t1, inner, extra_cls=''):
    top = st(t0, t1)
    html_parts.append(f'<div id="{bid}" class="board {extra_cls}" style="top:{top}px">{inner}</div>')
    show('#' + bid, t0, fx='pop', g=0.22); hide('#' + bid, t1)
    return top

# ================= GANCHO (segundo 0) =================
t_hook_end = fe('de cero') + 0.25
top = st(0, t_hook_end)
html_parts.append(f'<div id="hook" style="top:{top + 30}px"><span>La forma más rápida de</span><br><span>ganar dinero con IA 😳</span></div>')
init.append('gsap.set("#hook",{opacity:1,scale:1});')
tw.append(f'tl.to("#hook",{{opacity:0,duration:0.15}},{t_hook_end:.3f});')

# ================= PRUEBA: testimonios (5, 10, incluso 30 mil) =================
t_pers = f('muchas personas'); t5 = f('generar') + 0.05; t10 = f('10', t5); t30 = f('incluso', t10); t_out = f('es tan simple') - 0.05
pt = st(t_pers, t30)
cards = [('tA', 'assets/t_alejandra.jpg', -4, t5), ('tK', 'assets/t_krys.jpg', 3, t10), ('tS', 'assets/t_sergio.jpg', 0, t30)]
for cid, src, rot, t in cards:
    html_parts.append(f'<div id="{cid}" class="proof" style="top:{pt}px;transform:rotate({rot}deg)"><img src="{src}"></div>')
    init.append(f'gsap.set("#{cid}",{{opacity:0,scale:0.55}});')
    tw.append(f'tl.to("#{cid}",{{opacity:1,scale:0.82,duration:0.26,ease:"back.out(1.7)"}},{t:.3f});')
    sfx.append((t, 'pop.wav', 0.32))
# zoom al último (estilo ref: destello + crece al centro), cubre la toma: es material real
html_parts.append('<div id="scrim"></div><div id="flash"></div>')
init.append('gsap.set("#scrim",{opacity:0});gsap.set("#flash",{opacity:0});')
tz = t30 + 0.35
tw.append(f'tl.to("#scrim",{{opacity:0.78,duration:0.25}},{tz:.3f});')
tw.append(f'tl.to("#flash",{{keyframes:[{{opacity:0.9,duration:0.08}},{{opacity:0,duration:0.30}}]}},{tz:.3f});')
tw.append(f'tl.to("#tS",{{y:{640 - pt},scale:1.0,rotation:0,duration:0.35,ease:"power3.out"}},{tz:.3f});')
tw.append(f'tl.to(["#tA","#tK"],{{opacity:0,duration:0.15}},{tz:.3f});')
sfx.append((tz, 'whoosh.wav', 0.55))
# salida con barrido (motion blur) como en la referencia
tw.append(f'tl.to("#tS",{{y:{640 - pt - 560},filter:"blur(14px)",opacity:0,duration:0.24,ease:"power2.in"}},{t_out - 0.24:.3f});')
tw.append(f'tl.to("#scrim",{{opacity:0,duration:0.2}},{t_out - 0.2:.3f});')
sfx.append((t_out - 0.26, 'swipe.wav', 0.45))

# ================= TABLERO 1: implementación 1 a 1 =================
a = f('la implementación') ; b = f('y montarle') - 0.05
board('b1', a, b, '''<div class="mk big" id="b1t">Implementación <span class="red">1 a 1</span></div>
<svg class="ul" width="760" height="24"><path id="b1u" d="M10 14 Q 380 2 750 16" stroke="#E53935" stroke-width="8" fill="none" stroke-linecap="round"/></svg>
<div class="mk row" id="b1a">🧑‍💼 dueños de negocio</div><div class="mk row" id="b1b">🩺 profesionales de tu ciudad</div>''')
write_on('#b1t', a + 0.05, 0.55); draw('#b1u', f('uno a uno'), 800, 0.35)
show('#b1a', f('dueños de negocio'), fx='pop', g=0.25); show('#b1b', f('profesionales'), fx='pop', g=0.25)

# ================= TABLERO 2: Claude + ChatGPT =================
a = f('montarle') ; b = f('para que la IA') - 0.05
lg_claude = K.logo_svg('claude', '#D97757'); lg_gpt = K.logo_svg('openai', '#111111')
board('b2', a, b, f'''<div class="mk mid" id="b2t">Automatizaciones con</div>
<div class="tiles"><div class="tile" id="b2c">{lg_claude}<span>Claude</span></div><div class="plus mk">+</div><div class="tile" id="b2g">{lg_gpt}<span>ChatGPT</span></div></div>''')
write_on('#b2t', a + 0.05, 0.5); show('#b2c', f('Claude', a) - 0.05, fx='pop'); show('#b2g', f('ChatGPT', a) - 0.05, fx='pop')

# ================= TABLERO 3: la IA conoce... =================
a = f('para que la IA'); b = f('armarles') - 0.05
board('b3', a, b, '''<div class="mk mid" id="b3t">Que la IA conozca:</div>
<div class="mk row" id="b3a"><span class="ok">✓</span> su negocio</div><div class="mk row" id="b3b"><span class="ok">✓</span> su profesión</div><div class="mk row" id="b3c"><span class="ok">✓</span> sus proyectos</div>''')
write_on('#b3t', a + 0.05, 0.5)
show('#b3a', f('su negocio', a)); show('#b3b', f('su profesión', a)); show('#b3c', f('sus proyectos', a))

a = f('armarles'); b = fe('funcionando') + 0.35
board('b4', a, b, '''<div class="mk row" id="b4a">⚡ skills</div><div class="mk row" id="b4b">🤖 automatizaciones</div><div class="mk row big2" id="b4c">✅ ¡todo funcionando!</div>''')
show('#b4a', f('skills', a)); show('#b4b', f('automatizaciones', a)); show('#b4c', f('funcionando', a), fx='ding', g=0.25)

# ================= TABLERO 4: ¿básico? + burbuja (como "Basic" encerrado en la ref) =================
a = f('te suena básico') - 0.1; b = f('Afuera') - 0.05
board('b5', a, b, '''<div class="circ"><div class="mk huge" id="b5t">¿Básico?</div>
<svg class="ell" width="620" height="230"><ellipse id="b5e" cx="310" cy="115" rx="290" ry="98" stroke="#E53935" stroke-width="9" fill="none"/></svg></div>
<div class="mk row blue" id="b5b">🫧 tu burbuja: noticias de IA</div>''')
write_on('#b5t', a + 0.05, 0.45); draw('#b5e', f('básico') + 0.25, 1300, 0.5); show('#b5b', f('burbuja'))

# ================= TABLERO 5: dinero =================
a = f('te pagan'); b = f('Y los primeros') - 0.05
board('b6', a, b, '''<div class="mk mid" id="b6t">Te pagan</div>
<div class="money"><span class="mk m" id="b6a">$500</span><span class="mk m dash" id="b6d">–</span><span class="mk m" id="b6b">$2.000</span></div>
<div class="mk row" id="b6c">al mes 💵 (y es lo que me pagan a mí)</div>''')
write_on('#b6t', a, 0.35); show('#b6a', f('500', a), fx='pop'); show('#b6d', f('500', a) + 0.2, fx=None); show('#b6b', f('2 mil', a), fx='ding', g=0.25)
show('#b6c', f('al mes', a))

# ================= TABLERO 6: primeros 10 clientes -> CALIENTE (ramas, como "Warm" de la ref) =================
a = f('los primeros 10'); b = f('Dile a tu familia') - 0.05
board('b7', a, b, '''<div class="mk mid" id="b7t">10 primeros clientes</div>
<div class="mk huge red" id="b7h">🔥 Caliente</div>
<svg class="branches" width="820" height="110"><path id="br1" d="M410 6 L150 96" stroke="#1d1d1f" stroke-width="6" fill="none" stroke-linecap="round"/><path id="br2" d="M410 6 L410 96" stroke="#1d1d1f" stroke-width="6" fill="none" stroke-linecap="round"/><path id="br3" d="M410 6 L670 96" stroke="#1d1d1f" stroke-width="6" fill="none" stroke-linecap="round"/></svg>
<div class="leafs"><span class="mk leaf" id="l1">redes</span><span class="mk leaf" id="l2">estados</span><span class="mk leaf" id="l3">mensajes</span></div>''')
write_on('#b7t', a, 0.45); write_on('#b7h', f('caliente', a), 0.4)
draw('#br1', f('redes', a) - 0.1, 300, 0.25); show('#l1', f('redes', a), fx='pop')
draw('#br2', f('estados', a) - 0.1, 120, 0.25); show('#l2', f('estados', a), fx='pop')
draw('#br3', f('Escríbele', a) - 0.1, 300, 0.25); show('#l3', f('Escríbele', a), fx='pop')

# ================= familia / amigos / excompañeros =================
a = f('Dile a tu familia'); b = f('que estás aprendiendo') - 0.05
board('b8', a, b, '''<div class="icons"><div class="ic" id="i1"><b>👨‍👩‍👧</b><span class="mk">familia</span></div><div class="ic" id="i2"><b>🤝</b><span class="mk">amigos</span></div><div class="ic" id="i3"><b>💼</b><span class="mk">excompañeros</span></div></div>''')
show('#i1', f('familia', a)); show('#i2', f('amigos', a)); show('#i3', f('excompañeros', a))

# ================= el mensaje (burbuja de chat) =================
a = f('que estás aprendiendo'); b = f('¿No tienes') - 0.05
top = st(a, b)
html_parts.append(f'''<div id="chat" style="top:{top + 20}px"><div class="bub">Estoy aprendiendo a montar <b>agentes y automatizaciones con IA</b> 🤖 ¿Te monto una para tu negocio?<span class="tm">10:24 ✓✓</span></div></div>''')
show('#chat', a, fx='ding', g=0.22); hide('#chat', b)

# ================= ¿sin contactos? -> LOCAL (subrayado, como "Local" de la ref) =================
a = f('¿No tienes'); b = f('Toca puertas') - 0.05
board('b9', a, b, '''<div class="mk mid" id="b9t">¿Sin contactos?</div>
<div class="mk huge" id="b9l">LOCAL</div>
<svg class="ul" width="520" height="26"><path id="b9u" d="M10 12 Q 260 24 510 10" stroke="#1E5BD7" stroke-width="9" fill="none" stroke-linecap="round"/></svg>
<div class="mk row" id="b9c">📍 el chico IA de tu ciudad</div>''')
write_on('#b9t', a, 0.45); write_on('#b9l', f('hazlo local', a), 0.4); draw('#b9u', f('hazlo local', a) + 0.4, 560, 0.3)
show('#b9c', f('Conviértete', a))

# ================= lista local =================
a = f('Toca puertas'); b = f('y crea contenido') - 0.05
lg_fb = K.logo_svg('facebook', '#0866FF')
board('b10', a, b, f'''<div class="mk row" id="c1">🚪 toca puertas</div><div class="mk row" id="c2"><span class="lgi">{lg_fb}</span> grupos de Facebook</div>
<div class="mk row" id="c3">🏛️ cámara de comercio</div>''')
show('#c1', a); show('#c2', f('grupos de Facebook', a)); show('#c3', f('cámara de comercio', a))

# ================= crea contenido -> marca en paralelo =================
a = f('y crea contenido'); b = f('Y si quieres') - 0.05
board('b11', a, b, '''<div class="mk mid" id="b11t">📱 Crea contenido</div><div class="mk row" id="b11b">📈 tu marca, en paralelo</div><div class="mk row" id="b11c">🧠 mientras aprendes</div>''')
write_on('#b11t', a + 0.05, 0.45); show('#b11b', f('tu marca', a)); show('#b11c', f('mientras aprendes', a))

# ================= CTA (stickers blancos, como la ref) =================
a = f('Y si quieres'); top = st(a, DUR)
html_parts.append(f'''<div id="cta" style="top:{top + 10}px"><div class="st1"><span>Sígueme y comenta</span><br><span><b>“AUTOMATIZAR”</b> y te lo</span><br><span>mando por interno 👇</span></div>
<div class="st2" id="cta2"><span>@soydiegoosorio</span></div></div>''')
show('#cta', a, fx='pop', g=0.3); show('#cta2', f('comenta', a), fx='pop', g=0.25)

# ================= ZOOM alterno en cada corte (esconde los saltos) =================
ox, oy = int(FACE.cx), int(FACE.cy)
bounds = []; acc = 0.0
for s0, s1 in CUT['keep']:
    acc += s1 - s0; bounds.append(round(acc, 3))
init.append('gsap.set("#cam",{scale:1});')
z = 1.0
for t in bounds[:-1]:
    z = ZOOM_B if z == 1.0 else 1.0
    tw.append(f'tl.set("#cam",{{scale:{z}}},{t:.3f});')

# ================= SUBTÍTULOS: una palabra, MAYÚSCULAS (ref) =================
chunks = []; i = 0
while i < len(WD):
    ch = [WD[i]]
    while len(K.norm(ch[-1]['text'])) <= 2 and i + 1 < len(WD) and WD[i + 1]['start'] - ch[-1]['end'] < 0.25 and len(ch) < 2:
        i += 1; ch.append(WD[i])
    chunks.append(ch); i += 1
caps = []
for k, ch in enumerate(chunks):
    s = ch[0]['start']; e = ch[-1]['end']
    nxt = chunks[k + 1][0]['start'] if k + 1 < len(chunks) else DUR
    hide_t = min(max(e, s + 0.18) + 0.12, nxt - 0.02)
    txt = ' '.join(x['text'] for x in ch).upper().strip(',.')
    caps.append(f'<div id="k{k}" class="cap">{html.escape(txt)}</div>')
    init.append(f'gsap.set("#k{k}",{{opacity:0}});')
    tw.append(f'tl.set("#k{k}",{{opacity:1}},{max(0, s - 0.03):.3f});tl.set("#k{k}",{{opacity:0}},{hide_t:.3f});')

# ================= AUDIO =================
if PREVIEW_AUDIO:
    K.mix_audio(P, DUR, 'action-promo-rock.mp3', music_start=2.0, music_gain=0.30, sfx=sfx)

K.copy_fonts(P, ['montserrat-900', 'inter-600', 'inter-700', 'permanentmarker-400', 'poppins-700', 'poppins-800'])
CSS = K.font_faces([('Montserrat', 900, 'montserrat-900'), ('Inter', 600, 'inter-600'), ('Inter', 700, 'inter-700'),
                    ('Marker', 400, 'permanentmarker-400'), ('Poppins', 700, 'poppins-700'), ('Poppins', 800, 'poppins-800')])
HTML = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
{CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
#root{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#000;font-family:"Inter",sans-serif}}
#cam{{position:absolute;inset:0;transform-origin:{ox}px {oy}px}}
#v{{position:absolute;inset:0;width:{W}px;height:{H}px;object-fit:cover}}
/* gancho estilo sticker de Instagram */
#hook{{position:absolute;left:0;width:{W}px;text-align:center;z-index:30;font-family:"Inter";font-weight:700;font-size:54px;line-height:1.32}}
#hook span,.st1 span,.st2 span{{background:#fff;color:#111;padding:6px 22px;border-radius:16px;-webkit-box-decoration-break:clone;box-decoration-break:clone;box-shadow:0 6px 18px rgba(0,0,0,.22)}}
/* prueba */
.proof{{position:absolute;left:60px;width:960px;z-index:34;border-radius:22px;overflow:hidden;box-shadow:0 22px 60px rgba(0,0,0,.6);border:6px solid #fff;background:#fff}}
.proof img{{display:block;width:100%}}
#scrim{{position:absolute;inset:0;background:#0b0b10;z-index:33}}
#flash{{position:absolute;inset:0;z-index:40;background:radial-gradient(circle at 50% 45%,#fff 0%,#f3e9ff 35%,rgba(170,90,255,.55) 70%,rgba(120,60,255,0) 100%)}}
/* tablero (mini pizarra blanca) */
.board{{position:absolute;left:70px;width:940px;z-index:30;background:#fbfbf8;border:9px solid #cfd4d9;border-radius:20px;padding:26px 36px 30px;
  box-shadow:0 20px 50px rgba(0,0,0,.45);display:flex;flex-direction:column;align-items:center;gap:6px}}
.mk{{font-family:"Marker";color:{INK};line-height:1.15}}
.big{{font-size:70px}} .mid{{font-size:58px}} .huge{{font-size:100px;line-height:1.05}}
.row{{font-size:52px;align-self:flex-start;margin-left:40px}} .big2{{font-size:60px;color:{GREEN}}}
.red{{color:{RED}}} .blue{{color:{BLUE}}} .ok{{color:{GREEN}}}
.ul{{display:block;margin-top:-6px}}
.tiles{{display:flex;align-items:center;gap:30px;margin-top:10px}}
.tile{{width:250px;height:190px;border-radius:30px;background:#fff;border:3px solid #e6e6e6;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;box-shadow:0 8px 20px rgba(0,0,0,.15)}}
.tile svg{{width:96px;height:96px}} .tile span{{font-family:"Poppins";font-weight:800;font-size:36px;color:#111}}
.plus{{font-size:80px}}
.circ{{position:relative;width:620px;height:230px;display:flex;align-items:center;justify-content:center}}
.circ .ell{{position:absolute;inset:0}}
.money{{display:flex;align-items:baseline;gap:18px}} .m{{font-size:118px;color:{GREEN}}} .dash{{color:{INK}}}
.branches{{display:block;margin-top:-4px}}
.leafs{{display:flex;justify-content:space-between;width:900px;margin-top:-8px}} .leaf{{font-size:52px;width:300px;text-align:center}}
.icons{{display:flex;gap:40px;padding:6px 0}} .ic{{display:flex;flex-direction:column;align-items:center;gap:4px}} .ic b{{font-size:110px;line-height:1.1}} .ic span{{font-size:46px}}
.lgi svg{{width:52px;height:52px;vertical-align:-6px}}
/* burbuja de chat */
#chat{{position:absolute;left:90px;width:900px;z-index:30}}
.bub{{background:#DCF8C6;color:#111;font-family:"Inter";font-weight:600;font-size:46px;line-height:1.3;padding:28px 34px 44px;border-radius:30px 30px 30px 6px;position:relative;box-shadow:0 18px 40px rgba(0,0,0,.4)}}
.bub b{{font-weight:700}} .tm{{position:absolute;right:26px;bottom:10px;font-size:26px;color:#5b7f5b}}
/* CTA */
#cta{{position:absolute;left:0;width:{W}px;text-align:center;z-index:30;font-family:"Inter";font-weight:700}}
.st1{{font-size:56px;line-height:1.36}} .st1 b{{font-weight:800}}
.st2{{margin-top:26px;font-size:44px}}
/* subtítulos: una palabra, mayúsculas */
.cap{{position:absolute;left:0;width:{W}px;top:1590px;text-align:center;z-index:45;font-family:"Montserrat";font-weight:900;font-size:70px;
  color:#fff;letter-spacing:1px;text-shadow:0 5px 0 rgba(0,0,0,.9),0 0 22px rgba(0,0,0,.6)}}
{''}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
  <div id="cam" data-layout-allow-overflow><video id="v" class="clip" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="0" src="cut.mp4" muted playsinline></video></div>
  {''.join(html_parts)}
  {''.join(caps)}
  {''}
  <audio id="aud" data-start="0" data-duration="{DUR}" data-media-start="0" data-track-index="2" src="final_audio.wav" data-volume="1"></audio>
</div>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script>const tl=gsap.timeline({{paused:true}});window.__timelines={{"main":tl}};
{chr(10).join(init)}
{chr(10).join(tw)}
</script></body></html>'''
open(os.path.join(P, 'index.html'), 'w', encoding='utf-8').write(HTML)
print(f'OK index.html | {DUR}s | subtítulos {len(chunks)} | efectos {len(sfx)}')
