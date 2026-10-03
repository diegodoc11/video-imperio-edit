# -*- coding: utf-8 -*-
# RECETA DE REFERENCIA (no se corre tal cual): es el build.py REAL de un reel de Diego Osorio hecho con esta skill.
# Úsala para copiar efectos avanzados a tu build.py (los textos, frases y fotos de prueba son de ese video; no vienen incluidos).
# Estilo: stickers. Lo más reutilizable: gancho cinético (papel rasgado + logo que salta), máquina de escribir con clics, chat de app con nota de voz, X rojas, diagrama con flechas dibujadas, terminal, maqueta de celular con caja roja.
# Reel "Acabo de unir mi celular con mi PC" — modelado sobre la referencia de ChatGPT (ref2):
#   gancho cinético (palabras a mano + etiquetas de papel rasgado + logo que salta), stickers que aparecen
#   al decir cada cosa, X rojas, capturas/maquetas de app, máquina de escribir, CTA "Comenta" + etiqueta.
# Todo debajo de la barbilla (face.json); solo el clip real manejando cubre la toma.
import sys, os, json, html
SKILL = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_work', 'skill.txt'), encoding='utf-8').read().strip()
sys.path.insert(0, os.path.join(SKILL, 'scripts'))
import kit as K

P = os.path.dirname(os.path.abspath(__file__))
DO_AUDIO = '--no-audio' not in sys.argv
CUT = json.load(open(os.path.join(P, 'cutmap.json')))
DUR = round(CUT['dur'], 3); W, H = 1080, 1920
FIX = {'cloud': 'Claude', 'cloudrc': '/rc', 'pixel': 'píxel', 'instaladas': 'instalados'}
WD = K.load_words(P, FIX)
f = lambda ph, after=0: K.find(WD, ph, after)
fe = lambda ph, after=0: K.find_end(WD, ph, after)
FACE = K.Face(P, crop=K.CROP_WM)
ZOOM_B = 1.10
st = lambda a, b: FACE.safe_top(a, b, ZOOM_B)
init, tw, parts, sfx = [], [], [], []
ORANGE = '#D97757'; RED = '#E5322D'

def pop(el, t, fx='pop', g=0.26, ease='back.out(2)', sc=0.4, dur=0.3):
    init.append(f'gsap.set("{el}",{{opacity:0,scale:{sc}}});')
    tw.append(f'tl.to("{el}",{{opacity:1,scale:1,duration:{dur},ease:"{ease}"}},{t:.3f});')
    if fx: sfx.append((t, fx + '.wav', g))

def out(el, t, dur=0.15):
    tw.append(f'tl.to("{el}",{{opacity:0,duration:{dur},ease:"power1.in"}},{t - dur:.3f});')

def group(gid, t0, t1, inner, dy=0, cls='grp'):
    top = st(t0, t1) + dy
    parts.append(f'<div id="{gid}" class="{cls}" style="top:{top}px">{inner}</div>')
    init.append(f'gsap.set("#{gid}",{{opacity:0}});')
    tw.append(f'tl.set("#{gid}",{{opacity:1}},{t0:.3f});'); out('#' + gid, t1)
    return top

def typewrite(el, text, t, cps=22, g=0.10):
    """máquina de escribir: revela letra a letra (spans) con clics"""
    spans = ''.join(f'<span class="ch" id="{el}_{i}">{html.escape(c)}</span>' for i, c in enumerate(text))
    for i, _ in enumerate(text):
        init.append(f'gsap.set("#{el}_{i}",{{opacity:0}});')
        tw.append(f'tl.set("#{el}_{i}",{{opacity:1}},{t + i / cps:.3f});')
        if i % 3 == 0: sfx.append((t + i / cps, 'click.wav', g))
    return spans

def torn(text, size=78, rot=-2, cls=''):
    return f'<span class="torn {cls}" style="font-size:{size}px;transform:rotate({rot}deg)">{text}</span>'

def tag(text, rot=0, cls=''):
    return f'<span class="tag {cls}" style="transform:rotate({rot}deg)">{text}</span>'

LG_CLAUDE = K.logo_svg('claude', ORANGE)
BARS = ''.join(f'<i style="height:{h}px"></i>' for h in [14,30,46,22,38,52,26,44,18,36,50,24,40,16,32,48,20,34,12,28])
LG_META = open(os.path.join(P, 'assets', 'meta.svg'), encoding='utf-8').read()

# ================= GANCHO cinético (desde el segundo 0) =================
t_cel = f('celular'); t_pc = f('computador'); t_pide = f('le puedo pedir'); t_ej = f('Por ejemplo')
group('g0', 0, t_pide - 0.02, f'''
<div class="hk1" id="hw1">acabo de unir</div>
<div class="hkrow"><span id="hw2">{torn('mi celular 📱', 84, -3)}</span></div>
<div class="hkrow r"><span class="plus" id="hw3">+</span><span id="hw4">{torn('mi PC 💻', 84, 2)}</span></div>''', dy=0)
pop('#hw1', 0.0, fx=None, sc=0.7); pop('#hw2', t_cel - 0.1); pop('#hw3', t_pc - 0.2, fx=None); pop('#hw4', t_pc - 0.05)

# "le puedo pedir cosas a Claude Code" (tipo "how to create" de la ref: máquina de escribir + etiqueta + logo)
t_cc = f('Claude Code', t_pide)
txt = 'le puedo pedir cosas a'
group('g1', t_pide, t_ej - 0.05, f'''
<div class="hk1 sm">{typewrite('tw1', txt, t_pide, 26)}</div>
<div class="hkrow"><span id="cc">{torn('Claude Code', 92, -2)}</span><span class="lgpop" id="cclg">{LG_CLAUDE}</span></div>
<div class="hkrow sp"><span id="hr">{tag('⏳ horas', -5)}</span><span id="pa">{tag('💸 pagarle a alguien', 4)}</span></div>''', dy=-10)
pop('#cc', t_cc - 0.05); pop('#cclg', t_cc + 0.15, fx='pop', g=0.2, ease='back.out(3)')
pop('#hr', f('horas', t_pide)); pop('#pa', f('pagarle', t_pide))

# ================= "estoy manejando" -> clip real a pantalla completa =================
d0 = f('estoy manejando') - 0.1; d1 = f('le mando') + 0.05
parts.append(f'<div id="drw" class="full"><video id="drv" class="clip" data-start="{d0:.3f}" data-duration="{d1 - d0:.3f}" data-media-start="0" data-track-index="1" src="assets/drive.mp4" muted playsinline></video><div class="fslab">🚗 manejando…</div></div>')
init.append('gsap.set("#drw",{opacity:0,scale:1.12});')
tw.append(f'tl.to("#drw",{{opacity:1,scale:1,duration:0.3,ease:"power3.out"}},{d0:.3f});')
tw.append(f'tl.to("#drw",{{opacity:0,duration:0.15}},{d1 - 0.15:.3f});')
sfx.append((d0, 'whoosh.wav', 0.5))

# ================= nota de voz + pedido (chat estilo app de Claude) =================
c0 = f('le mando'); c1 = f('Y él mismo') - 0.05
t_req = f('le pido una página')
req = 'Hazme una página web para vender mi servicio de automatizaciones con IA'
group('g2', c0, c1, f'''<div class="app"><div class="apph"><span class="lgs">{LG_CLAUDE}</span> Claude</div>
<div class="vn" id="vn"><span class="play">▶</span><span class="wave">{BARS}</span><span class="vt">0:12</span></div>
<div class="msg" id="msg">{typewrite('tw2', req, t_req, 30, 0.08)}</div></div>''', dy=0)
pop('#vn', c0 + 0.05, fx='pop'); pop('#msg', t_req - 0.05, fx=None, sc=0.9)

# ================= él mismo hace todo: etiquetas una por una =================
a = f('Y él mismo'); b = f('Yo solo') - 0.05
group('g3', a, b, f'''<div class="hk1 sm">él mismo hace todo</div>
<div class="tags"><span id="t1">{tag('✍️ copy', -4)}</span><span id="t2">{tag('🖼️ imágenes', 3)}</span>
<span id="t3">{tag('🌐 dominio', 2)}</span><span id="t4">{tag('🔗 link funcionando ✅', -3, 'grn')}</span></div>''')
pop('#t1', f('copy', a)); pop('#t2', f('imágenes', a)); pop('#t3', f('dominio', a)); pop('#t4', f('link', a), fx='ding', g=0.22)

# ================= "yo solo lo abro y reviso" -> maqueta de la web lista =================
a = f('Yo solo'); b = f('Ahora,') - 0.05
group('g4', a, b, '''<div class="brow"><div class="bbar"><i></i><i></i><i></i><span>🔒 tuservicio-ia.com</span></div>
<div class="bbody"><div class="bh">Automatiza tu negocio con IA</div><div class="bs">Agentes que trabajan por ti 24/7</div><div class="bb">Agenda tu llamada →</div></div>
<div class="stamp" id="stp">✓ FUNCIONA</div></div>''')
pop('#stp', f('reviso', a), fx='thump', g=0.4, sc=2.2, ease='power3.out', dur=0.22)

# ================= guiones + anuncios + listos =================
a = f('Ahora,'); b = f('sin abrir') - 0.05
group('g5', a, b, f'''<div class="hk1 sm" id="g5t">ahora a promocionarlo</div>
<div class="tags"><span id="u1">{tag('📝 guiones', -3)}</span><span id="u2">{tag('🎬 anuncios en video', 2)}</span><span id="u3">{tag('✅ listos para publicar', -2, 'grn')}</span></div>''')
pop('#g5t', a, fx=None, sc=0.8); pop('#u1', f('guiones', a)); pop('#u2', f('anuncios', a)); pop('#u3', f('listos', a), fx='ding', g=0.22)

# ================= sin software / sin editor (X roja como la ref) =================
a = f('sin abrir'); b = f('y puedo decirle') - 0.05
group('g6', a, b, f'''<div class="xrow"><div class="xbox" id="x1"><span>🖥️ software</span><b class="xx" id="xx1">✕</b></div>
<div class="xbox" id="x2"><span>✂️ editor</span><b class="xx" id="xx2">✕</b></div></div>''')
pop('#x1', a, fx=None); pop('#xx1', f('software', a), fx='thump', g=0.45, sc=2.5, ease='power3.out', dur=0.2)
pop('#x2', f('sin pagarle', a), fx=None); pop('#xx2', f('editor', a), fx='thump', g=0.45, sc=2.5, ease='power3.out', dur=0.2)

# ================= Meta Ads + etiquetas una por una =================
a = f('y puedo decirle'); b = f('Y fue allí') - 0.05
group('g7', a, b, f'''<div class="meta"><div class="mlogo" id="mlg">{LG_META}<span>Meta Ads</span></div>
<div class="mtags"><span id="m1">{tag('⚙️ configuraciones', -2)}</span><span id="m2">{tag('🎯 segmentaciones', 2)}</span>
<span id="m3">{tag('📍 píxel', -3)}</span><span id="m4">{tag('💰 clientes', 3, 'grn')}</span></div></div>''')
pop('#mlg', f('Meta', a) - 0.1, fx='pop', g=0.3)
pop('#m1', f('configuraciones', a)); pop('#m2', f('segmentaciones', a)); pop('#m3', f('píxel', a)); pop('#m4', f('clientes', a), fx='ding', g=0.25)

# ================= "no estoy usando el celular para pedirle cosas a una IA" =================
a = f('No estoy'); b = f('Estoy usándolo') - 0.05
group('g8', a, b, f'''<div class="xrow"><div class="xbox wide" id="n1"><span>💬 pedirle cosas a una IA</span><b class="xx" id="nx1">✕</b></div></div>''')
pop('#n1', a, fx=None); pop('#nx1', f('pedirle', a) + 0.2, fx='thump', g=0.45, sc=2.5, ease='power3.out', dur=0.2)

# ================= DIAGRAMA: celular -> PC (Claude Code) -> equipo de agentes =================
a = f('Estoy usándolo'); b = f('Tan solo') - 0.05
group('g9', a, b, f'''<div class="dia">
<div class="node n1" id="dn1"><b>📱</b><span>tu celular</span></div>
<svg class="arr" width="150" height="40"><path id="ar1" d="M6 20 L136 20" stroke="#fff" stroke-width="7" stroke-linecap="round" fill="none"/><path d="M118 6 L140 20 L118 34" stroke="#fff" stroke-width="7" stroke-linecap="round" fill="none" id="ah1"/></svg>
<div class="node n2" id="dn2"><b>💻</b><span class="lgs2">{LG_CLAUDE}</span><span>Claude Code</span></div>
<svg class="arr" width="120" height="260"><path id="ar2" d="M6 130 L110 30 M6 130 L110 130 M6 130 L110 230" stroke="#fff" stroke-width="6" stroke-linecap="round" fill="none"/></svg>
<div class="agents"><div class="ag" id="ag1">🤖 web</div><div class="ag" id="ag2">🤖 anuncios</div><div class="ag" id="ag3">🤖 Meta Ads</div></div></div>''')
pop('#dn1', f('Estoy usándolo') + 0.05, fx='pop')
init.append('gsap.set("#ar1",{strokeDasharray:140,strokeDashoffset:140});gsap.set("#ah1",{opacity:0});')
ta = f('trabajo pesado', a); tw.append(f'tl.to("#ar1",{{strokeDashoffset:0,duration:0.35}},{ta:.3f});tl.set("#ah1",{{opacity:1}},{ta + 0.3:.3f});')
pop('#dn2', ta + 0.3, fx='pop')
init.append('gsap.set("#ar2",{strokeDasharray:420,strokeDashoffset:420});')
te = f('equipo de agentes', a); tw.append(f'tl.to("#ar2",{{strokeDashoffset:0,duration:0.4}},{te:.3f});')
pop('#ag1', te + 0.15); pop('#ag2', te + 0.45); pop('#ag3', te + 0.75)

# ================= terminal: escribe /rc =================
a = f('Tan solo'); b = f('y luego ve') - 0.05
t_rc = f('/rc', a)
group('g10', a, b, f'''<div class="term"><div class="tbar"><i></i><i></i><i></i><span>Claude Code — tu computador</span></div>
<div class="tbody"><div class="tl1">✻ Claude Code</div><div class="tl2"><span class="pr">&gt;</span> {typewrite('tw3', '/rc', t_rc - 0.1, 8, 0.25)}<span class="cur">▌</span></div>
<div class="tl3" id="tok">● Remote Control activo · ábrelo en la app</div></div></div>''')
pop('#tok', t_rc + 0.6, fx='ding', g=0.2, sc=0.9)

# ================= pasos en la app del celular (cajas rojas como la ref) =================
a = f('y luego ve'); b = f('¿Quieres') - 0.05
group('g11', a, b, f'''<div class="steps">
<div class="phone"><div class="ph-top">Claude</div>
<div class="ph-row" id="ps1">💻 Mi computador <em>● en línea</em></div>
<div class="ph-nav"><span>Chats</span><span class="code" id="pcode">Código</span><span>Proyectos</span></div>
<div class="redbox" id="rb1"></div></div>
<div class="stl"><span id="s1">{tag('1 · abre la app', -2)}</span><span id="s2">{tag('2 · ve a Código', 2)}</span><span id="s3">{tag('3 · agrega tu PC', -2)}</span><span id="s4">{tag('✅ sesión lista', 2, 'grn')}</span></div></div>''')
pop('#s1', f('la app', a)); pop('#s2', f('código', a)); pop('#rb1', f('código', a) + 0.1, fx=None, sc=1.3)
pop('#s3', f('agrega', a)); pop('#ps1', f('agrega', a) + 0.3, fx=None, sc=0.9); pop('#s4', f('lista', a) - 0.3, fx='ding', g=0.22)

# ================= CTA (estilo ref: "Comment" a mano + etiqueta) =================
a = f('¿Quieres'); tc = f('Comenta', a)
group('g12', a, tc - 0.02, f'''<div class="hk1">¿quieres mis agentes?</div><div class="hkrow"><span id="q1">{tag('🤖 hacen todo el marketing por mí', -2)}</span></div>''')
pop('#q1', f('todo el trabajo', a))
top = st(tc, DUR)
parts.append(f'<div id="cta" class="grp" style="top:{top + 10}px"><div class="hk1 big">Comenta</div><div class="hkrow">{torn('“CLASE”', 130, -2)}</div><div class="hk1 sm2">y te muestro cómo 👇</div></div>')
pop('#cta', tc, fx='pop', g=0.32, sc=0.6)

# ================= ZOOM: alterno en cortes + golpe en "entendí algo" =================
ox, oy = int(FACE.cx), int(FACE.cy)
acc = 0.0; bounds = []
for s0, s1 in CUT['keep']:
    acc += s1 - s0; bounds.append(round(acc, 3))
init.append('gsap.set("#cam",{scale:1});'); z = 1.0
for t in bounds[:-1]:
    z = ZOOM_B if z == 1.0 else 1.0
    tw.append(f'tl.set("#cam",{{scale:{z}}},{t:.3f});')
te0 = f('Y fue allí'); te1 = f('No estoy') - 0.05
tw.append(f'tl.to("#cam",{{scale:1.28,duration:0.14,ease:"power2.out"}},{f("entendí", te0) - 0.05:.3f});tl.set("#cam",{{scale:{z}}},{te1:.3f});')
sfx.append((f('entendí', te0) - 0.05, 'whoosh.wav', 0.35))

# ================= SUBTÍTULOS (pequeños, 2-3 palabras, como la ref) =================
chunks = []; cur = []
for w in WD:
    cur.append(w); txt = ' '.join(x['text'] for x in cur)
    if w['text'][-1:] in '.?!,' or len(cur) >= 3 or len(txt) >= 18:
        chunks.append(cur); cur = []
if cur: chunks.append(cur)
caps = []
for k, ch in enumerate(chunks):
    s = ch[0]['start']; e = ch[-1]['end']
    nxt = chunks[k + 1][0]['start'] if k + 1 < len(chunks) else DUR
    hide_t = min(e + 0.2, nxt - 0.03)
    caps.append(f'<div id="k{k}" class="cap">{html.escape(" ".join(x["text"] for x in ch))}</div>')
    init.append(f'gsap.set("#k{k}",{{opacity:0}});')
    tw.append(f'tl.set("#k{k}",{{opacity:1}},{max(0, s - 0.03):.3f});tl.set("#k{k}",{{opacity:0}},{hide_t:.3f});')

if DO_AUDIO:
    K.mix_audio(P, DUR, 'dance-playful-night.mp3', music_start=0.0, music_gain=0.26, sfx=sfx)

K.copy_fonts(P, ['caveat-700', 'dmserifdisplay-400', 'permanentmarker-400', 'poppins-700', 'poppins-800', 'inter-600', 'inter-700', 'jetbrainsmono-600'])
CSS = K.font_faces([('Caveat', 700, 'caveat-700'), ('Serif', 400, 'dmserifdisplay-400'), ('Marker', 400, 'permanentmarker-400'),
                    ('Poppins', 700, 'poppins-700'), ('Poppins', 800, 'poppins-800'), ('Inter', 600, 'inter-600'), ('Inter', 700, 'inter-700'),
                    ('JBM', 600, 'jetbrainsmono-600')])
HTML = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
{CSS}
*{{margin:0;padding:0;box-sizing:border-box}}
#root{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#000;font-family:"Inter",sans-serif}}
#cam{{position:absolute;inset:0;transform-origin:{ox}px {oy}px}}
#v{{position:absolute;inset:0;width:{W}px;height:{H}px;object-fit:cover}}
.grp{{position:absolute;left:0;width:{W}px;z-index:30;display:flex;flex-direction:column;align-items:center;gap:8px}}
/* palabras a mano (Caveat) y etiquetas de papel rasgado (serif) */
.hk1{{font-family:"Caveat";font-size:84px;color:#fff;line-height:1;text-shadow:0 3px 10px rgba(0,0,0,.75),0 0 2px #000}}
.hk1.sm{{font-size:70px}} .hk1.big{{font-size:104px}} .hk1.sm2{{font-size:60px}}
.hkrow{{display:flex;align-items:center;justify-content:center;gap:22px}} .hkrow.r{{margin-left:120px}} .hkrow.sp{{gap:40px;margin-top:10px}}
.torn{{display:inline-block;font-family:"Serif";color:#111;background:#fdfdfb;padding:6px 30px 12px;line-height:1.05;
  clip-path:polygon(0% 8%,4% 0%,9% 6%,15% 1%,22% 7%,30% 2%,37% 8%,45% 1%,53% 7%,61% 2%,69% 8%,77% 1%,85% 7%,92% 2%,100% 7%,99% 93%,94% 100%,88% 94%,80% 99%,72% 93%,64% 100%,56% 94%,48% 99%,40% 93%,32% 100%,24% 94%,16% 99%,8% 93%,1% 99%);
  filter:drop-shadow(0 8px 14px rgba(0,0,0,.45))}}
.plus{{font-family:"Caveat";font-size:96px;color:#fff;text-shadow:0 3px 10px rgba(0,0,0,.7)}}
.lgpop{{width:120px;height:120px;border-radius:28px;background:#fff;display:flex;align-items:center;justify-content:center;box-shadow:0 10px 26px rgba(0,0,0,.45)}}
.lgpop svg{{width:84px;height:84px}}
.tag{{display:inline-block;font-family:"Marker";font-size:50px;color:#111;background:#fff;padding:8px 24px;border-radius:10px;box-shadow:0 8px 18px rgba(0,0,0,.4);white-space:nowrap}}
.tag.grn{{background:#d9fbe1}}
.tags{{display:flex;flex-wrap:wrap;justify-content:center;gap:18px 26px;width:960px;margin-top:6px}}
.ch{{display:inline}}
/* clip a pantalla completa */
.full{{position:absolute;inset:0;z-index:35;background:#000}} .full video{{position:absolute;inset:0;width:{W}px;height:{H}px;object-fit:cover}}
.fslab{{position:absolute;left:50%;transform:translateX(-50%);bottom:440px;font-family:"Caveat";font-size:90px;color:#fff;text-shadow:0 4px 14px rgba(0,0,0,.8)}}
/* app de Claude */
.app{{width:900px;background:#F5F4EE;border-radius:30px;padding:22px 26px 30px;box-shadow:0 20px 50px rgba(0,0,0,.5)}}
.apph{{display:flex;align-items:center;gap:12px;font-family:"Inter";font-weight:700;font-size:34px;color:#3d3929;margin-bottom:16px}}
.lgs svg{{width:40px;height:40px;vertical-align:middle}}
.vn{{display:flex;align-items:center;gap:16px;align-self:flex-end;margin-left:auto;width:560px;background:#E8E5DA;border-radius:26px;padding:16px 22px}}
.play{{width:52px;height:52px;border-radius:50%;background:{ORANGE};color:#fff;display:flex;align-items:center;justify-content:center;font-size:24px}}
.wave{{flex:1;display:flex;align-items:center;gap:6px;height:56px}} .wave i{{display:block;width:8px;border-radius:4px;background:#8a8472}} .vt{{font-family:"Inter";font-weight:600;font-size:28px;color:#6b6656}}
.msg{{margin-top:14px;margin-left:auto;width:740px;background:#E8E5DA;border-radius:26px;padding:18px 26px;font-family:"Inter";font-weight:600;font-size:38px;line-height:1.3;color:#2b2a26}}
/* navegador */
.brow{{position:relative;width:900px;background:#fff;border-radius:26px;overflow:visible;box-shadow:0 20px 50px rgba(0,0,0,.5)}}
.bbar{{display:flex;align-items:center;gap:10px;background:#f1f1f3;padding:14px 20px;border-radius:26px 26px 0 0}}
.bbar i,.tbar i{{width:16px;height:16px;border-radius:50%;background:#ff5f57}} .bbar i:nth-child(2),.tbar i:nth-child(2){{background:#febc2e}} .bbar i:nth-child(3),.tbar i:nth-child(3){{background:#28c840}}
.bbar span{{margin-left:12px;background:#fff;border-radius:10px;padding:8px 18px;font-family:"JBM";font-size:26px;color:#444;flex:1}}
.bbody{{padding:34px 40px 38px;background:linear-gradient(135deg,#0f172a,#1e293b);border-radius:0 0 26px 26px}}
.bh{{font-family:"Poppins";font-weight:800;font-size:54px;color:#fff;line-height:1.1}} .bs{{font-family:"Inter";font-weight:600;font-size:32px;color:#94a3b8;margin:10px 0 22px}}
.bb{{display:inline-block;background:{ORANGE};color:#fff;font-family:"Poppins";font-weight:700;font-size:32px;padding:14px 28px;border-radius:14px}}
.stamp{{position:absolute;right:-10px;top:-34px;transform:rotate(8deg);font-family:"Marker";font-size:56px;color:#1a9b46;border:6px solid #1a9b46;border-radius:14px;padding:4px 18px;background:rgba(255,255,255,.92)}}
/* X roja */
.xrow{{display:flex;gap:40px;justify-content:center}}
.xbox{{position:relative;background:#fff;border-radius:16px;padding:22px 34px;font-family:"Marker";font-size:54px;color:#111;box-shadow:0 10px 24px rgba(0,0,0,.4)}}
.xbox.wide{{font-size:52px}}
.xx{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:"Poppins";font-weight:800;font-size:150px;color:{RED};line-height:1;text-shadow:0 4px 10px rgba(0,0,0,.3)}}
/* Meta */
.meta{{display:flex;flex-direction:column;align-items:center;gap:16px}}
.mlogo{{display:flex;align-items:center;gap:16px;background:#fff;border-radius:22px;padding:14px 30px;box-shadow:0 10px 24px rgba(0,0,0,.4)}}
.mlogo svg{{width:90px;height:90px}} .mlogo span{{font-family:"Poppins";font-weight:800;font-size:52px;color:#111}}
.mtags{{display:flex;flex-wrap:wrap;justify-content:center;gap:16px 22px;width:980px}}
/* diagrama */
.dia{{display:flex;align-items:center;justify-content:center;gap:6px;background:rgba(10,10,14,.82);border-radius:28px;padding:26px 24px;border:2px solid rgba(255,255,255,.15)}}
.node{{display:flex;flex-direction:column;align-items:center;gap:6px;background:#fff;border-radius:22px;padding:16px 18px;min-width:180px}}
.node b{{font-size:74px;line-height:1}} .node span{{font-family:"Poppins";font-weight:700;font-size:28px;color:#111}}
.lgs2 svg{{width:44px;height:44px}}
.agents{{display:flex;flex-direction:column;gap:14px}}
.ag{{background:#D97757;color:#fff;font-family:"Poppins";font-weight:700;font-size:32px;padding:12px 20px;border-radius:16px;white-space:nowrap}}
/* terminal */
.term{{width:900px;background:#1b1b1f;border-radius:22px;overflow:hidden;box-shadow:0 20px 50px rgba(0,0,0,.55);border:2px solid #34343c}}
.tbar{{display:flex;align-items:center;gap:10px;background:#26262b;padding:14px 20px}} .tbar span{{margin-left:12px;font-family:"Inter";font-weight:600;font-size:26px;color:#a7a7b3}}
.tbody{{padding:24px 32px 30px;font-family:"JBM";font-weight:600}}
.tl1{{font-size:34px;color:{ORANGE};margin-bottom:16px}} .tl2{{font-size:64px;color:#fff}} .pr{{color:#a7a7b3}}
.cur{{color:{ORANGE};animation:none}} .tl3{{margin-top:16px;font-size:30px;color:#4ade80}}
/* pasos app */
.steps{{display:flex;align-items:center;gap:26px}}
.phone{{position:relative;width:360px;height:430px;background:#F5F4EE;border-radius:40px;border:10px solid #111;padding:22px 16px;box-shadow:0 18px 40px rgba(0,0,0,.5)}}
.ph-top{{font-family:"Inter";font-weight:700;font-size:30px;color:#3d3929;margin-bottom:16px}}
.ph-row{{background:#fff;border-radius:16px;padding:14px;font-family:"Inter";font-weight:700;font-size:24px;color:#222}} .ph-row em{{display:block;font-style:normal;color:#16a34a;font-size:22px;margin-top:4px}}
.ph-nav{{position:absolute;left:12px;right:12px;bottom:14px;display:flex;justify-content:space-around;font-family:"Inter";font-weight:600;font-size:22px;color:#6b6656}}
.ph-nav .code{{color:{ORANGE};font-weight:700}}
.redbox{{position:absolute;left:118px;bottom:2px;width:110px;height:52px;border:5px solid {RED};border-radius:12px}}
.stl{{display:flex;flex-direction:column;gap:14px;align-items:flex-start}} .stl .tag{{font-size:44px}}
/* subtítulos pequeños (ref) */
.cap{{position:absolute;left:0;width:{W}px;top:1610px;text-align:center;z-index:45;font-family:"Poppins";font-weight:700;font-size:50px;color:#fff;
  text-shadow:0 3px 8px rgba(0,0,0,.9),0 0 2px #000}}
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
print(f'OK index.html | {DUR}s | subtítulos {len(chunks)} | efectos {len(sfx)}')
