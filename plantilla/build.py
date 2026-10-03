# -*- coding: utf-8 -*-
"""
video-imperio-edit · PLANTILLA  — copia este archivo a <proyecto>/build.py, llena la parte "TU VIDEO" y corre:

    PY build.py              -> index.html + final_audio.wav (para la vista previa y el render)
    PY build.py --sin-audio  -> solo index.html (más rápido mientras ajustas textos y tiempos)

Los tiempos se escriben con FRASES tal como quedaron en words.json ("la implementación") o con segundos (12.4).
Cada pieza aparece cuando se dice su frase y TODO va debajo de la barbilla (face.json), nunca sobre la cara.
"""
import sys, os, json, html

P = os.path.dirname(os.path.abspath(__file__))
SKILL = open(os.path.join(P, '_work', 'skill.txt'), encoding='utf-8').read().strip()
sys.path.insert(0, os.path.join(SKILL, 'scripts'))
import kit as K

# =====================================================================================================
#                                     TU VIDEO  (edita solo esta parte)
# =====================================================================================================
ESTILO = 'fucsia'            # 'tablero' (sticker blanco + pizarra a mano + subtítulo de 1 palabra en MAYÚSCULAS)
                             # 'fucsia'  (título a mano + palabra activa resaltada + tarjetas de logo y ficha)
                             # 'stickers' (palabras a mano + papel rasgado + etiquetas + X rojas)
COLOR = '#D304C2'            # color de acento (resaltado de subtítulos, números, bordes)
QUITAR_MARCA = False         # True si el video trae marca de agua en una esquina de abajo (BIGVU, etc.)
MUSICA = 'auto'              # 'auto' = primera pista de recursos/musica · None = sin música · o 'ruta/pista.mp3'
VOLUMEN_MUSICA = 0.28        # 0.20 suave · 0.30 se nota · 0.35 fuerte (siempre baja sola cuando hablas)
CORRECCIONES = {'cloud': 'Claude', 'chatgpt': 'ChatGPT'}   # palabras que whisper escribe mal -> como deben salir

GANCHO = ['5 skills de Claude que hacen', 'que tu web no parezca', 'hecha con IA']   # renglones; sale desde el segundo 0
GANCHO_HASTA = 4.0           # frase o segundo en que se quita el gancho

ESCENAS = [
    # --- ejemplos de cada tipo (bórralos y escribe los de tu video) ---
    # {'tipo': 'lista', 'desde': 'primero', 'hasta': 'segundo paso', 'titulo': 'Lo que necesitas',
    #  'items': [('una cuenta', '✅ una cuenta'), ('un celular', '📱 un celular')]},
    # {'tipo': 'tarjeta', 'desde': 'te pagan', 'hasta': 'y los primeros', 'titulo': 'Te pagan', 'grande': '$500 – $2.000', 'sub': 'al mes'},
    # {'tipo': 'logos', 'desde': 'con Claude', 'hasta': 'para que', 'titulo': 'Automatizaciones con',
    #  'logos': [('Claude', 'claude', 'Claude', '#D97757'), ('ChatGPT', 'openai', 'ChatGPT', '#111111')]},
    # {'tipo': 'logo', 'desde': 'primera', 'acerca_desde': 'una colección', 'hasta': 'dos',
    #  'svg': None, 'nombre': 'Awesome Design', 'oscuro': True,
    #  'acerca': 'Colección de sistemas de diseño de marcas top.', 'url': 'getdesign.md'},
    # {'tipo': 'imagen', 'desde': 'mis resultados', 'hasta': 'y por eso', 'src': 'assets/resultado.jpg', 'completa': False},
    # {'tipo': 'video', 'desde': 'con este combo', 'hasta': 'el resultado', 'src': 'assets/web.mp4', 'etiqueta': '🌐 la web real'},
    # {'tipo': 'tachado', 'desde': 'sin abrir', 'hasta': 'y puedo', 'items': [('software', '🖥️ software'), ('editor', '✂️ editor')]},
    # {'tipo': 'chat', 'desde': 'le mando', 'hasta': 'y él mismo', 'app': 'WhatsApp', 'texto': '¿Te monto una automatización?'},
    # {'tipo': 'terminal', 'desde': 'escribe', 'hasta': 'y luego', 'comando': '/rc', 'resultado': '● listo'},
]
ZOOMS = []                   # golpes de zoom en frases fuertes: [('entendí algo', 1.25, 2.0)]  (frase, escala, segundos)
CTA = {'desde': 'comenta', 'palabra': 'CLASE', 'sub': 'y te lo envío 👇', 'usuario': ''}   # usuario: '@tucuenta' (opcional)
# =====================================================================================================

ARGS = sys.argv[1:]
CUT = json.load(open(os.path.join(P, 'cutmap.json'))); DUR = round(CUT['dur'], 3); W, H = 1080, 1920
WD = K.load_words(P, CORRECCIONES)
CROP = K.CROP_WM if QUITAR_MARCA else 1.0
FACE = K.Face(P, crop=CROP); ZB = 1.10

def T(x, after=0.0):
    return float(x) if isinstance(x, (int, float)) else K.find(WD, x, after)

def safe(a, b, extra=0):
    return FACE.safe_top(a, b, ZB) + extra

init, tw, parts, sfx = [], [], [], []
esc = html.escape

def pop(el, t, g=0.25, fx='pop', sc=0.85, dur=0.28, ease='back.out(1.7)'):
    init.append(f'gsap.set("{el}",{{opacity:0,scale:{sc}}});')
    tw.append(f'tl.to("{el}",{{opacity:1,scale:1,duration:{dur},ease:"{ease}"}},{max(0, t):.3f});')
    if fx: sfx.append((max(0, t), fx + '.wav', g))

def out(el, t, dur=0.16):
    tw.append(f'tl.to("{el}",{{opacity:0,duration:{dur},ease:"power1.in"}},{max(0, t - dur):.3f});')

def grupo(gid, a, b, inner, cls, dy=0, fx='pop'):
    parts.append(f'<div id="{gid}" class="grp {cls}" style="top:{safe(a, b, dy)}px">{inner}</div>')
    pop('#' + gid, a, fx=fx, g=0.2, sc=0.92, dur=0.24, ease='power2.out'); out('#' + gid, b)

def escribir(el, t, dur=0.45):            # revelado tipo "escrito a mano" (izquierda -> derecha)
    init.append(f'gsap.set("{el}",{{clipPath:"inset(0% 100% 0% 0%)"}});')
    tw.append(f'tl.to("{el}",{{clipPath:"inset(0% 0% 0% 0%)",duration:{dur},ease:"none"}},{t:.3f});')

def tipear(eid, texto, t, cps=24):
    s = ''.join(f'<span id="{eid}_{i}">{esc(c)}</span>' for i, c in enumerate(texto))
    for i, _ in enumerate(texto):
        init.append(f'gsap.set("#{eid}_{i}",{{opacity:0}});'); tw.append(f'tl.set("#{eid}_{i}",{{opacity:1}},{t + i / cps:.3f});')
        if i % 3 == 0: sfx.append((t + i / cps, 'click.wav', 0.10))
    return s

CAJA = {'tablero': 'board', 'fucsia': 'dark', 'stickers': 'stk'}[ESTILO]

# ---------------- GANCHO (segundo 0) ----------------
g1 = T(GANCHO_HASTA)
if ESTILO == 'tablero':
    inner = '<br>'.join(f'<span>{esc(x)}</span>' for x in GANCHO)
    parts.append(f'<div id="hook" class="ig" style="top:{safe(0, g1, 20)}px">{inner}</div>')
elif ESTILO == 'fucsia':
    parts.append(f'<div id="hook" class="hand" style="top:{safe(0, g1, 50)}px">{"<br>".join(esc(x).upper() for x in GANCHO)}</div>')
else:
    rest = ''.join(f'<div class="row"><span class="torn">{esc(x)}</span></div>' for x in GANCHO[1:])
    parts.append(f'<div id="hook" class="grp" style="top:{safe(0, g1)}px"><div class="script">{esc(GANCHO[0])}</div>{rest}</div>')
init.append('gsap.set("#hook",{opacity:1});'); tw.append(f'tl.set("#hook",{{opacity:0}},{g1:.3f});')

# ---------------- ESCENAS ----------------
for n, E in enumerate(ESCENAS):
    gid = f'e{n}'; a = T(E['desde']); b = T(E['hasta'], a) - 0.05 if E.get('hasta') is not None else DUR
    tipo = E['tipo']
    if tipo == 'lista':
        filas = ''.join(f'<div class="item" id="{gid}i{k}">{esc(txt)}</div>' for k, (_, txt) in enumerate(E['items']))
        grupo(gid, a, b, f'<div class="ttl" id="{gid}t">{esc(E.get("titulo", ""))}</div>{filas}', CAJA)
        if ESTILO == 'tablero': escribir(f'#{gid}t', a + 0.05)
        for k, (fr, _) in enumerate(E['items']): pop(f'#{gid}i{k}', T(fr, a))
    elif tipo == 'tarjeta':
        grupo(gid, a, b, f'<div class="ttl">{esc(E.get("titulo", ""))}</div><div class="big" id="{gid}g">{esc(E["grande"])}</div><div class="sub">{esc(E.get("sub", ""))}</div>', CAJA)
        pop(f'#{gid}g', a + 0.25, fx='ding', g=0.22)
    elif tipo == 'logos':
        tiles = '<span class="plus">+</span>'.join(f'<div class="tile" id="{gid}l{k}">{K.logo_svg(svg, col)}<span>{esc(nom)}</span></div>' for k, (_, svg, nom, col) in enumerate(E['logos']))
        grupo(gid, a, b, f'<div class="ttl">{esc(E.get("titulo", ""))}</div><div class="tiles">{tiles}</div>', CAJA)
        for k, (fr, _, _, _) in enumerate(E['logos']): pop(f'#{gid}l{k}', T(fr, a) - 0.05)
    elif tipo == 'logo':
        a2 = T(E['acerca_desde'], a) if E.get('acerca_desde') else b
        ico = K.logo_svg(E['svg'], E.get('color', '#ffffff' if E.get('oscuro', True) else '#111111')) if E.get('svg') else ''
        cls = 'lgcard ' + ('oscuro' if E.get('oscuro', True) else 'claro')
        parts.append(f'<div id="{gid}" class="grp" style="top:{safe(a, a2, 40)}px"><div class="{cls}">{ico}<span>{esc(E["nombre"])}</span></div></div>')
        pop('#' + gid, a, g=0.2); out('#' + gid, a2)
        if E.get('acerca'):
            parts.append(f'<div id="{gid}b" class="grp" style="top:{safe(a2, b, 20)}px"><div class="about"><div class="abh">Acerca de</div>'
                         f'<div class="abd">{esc(E["acerca"])}</div><div class="abl">🔗 {esc(E.get("url", ""))}</div></div></div>')
            pop(f'#{gid}b', a2, g=0.15); out(f'#{gid}b', b)
    elif tipo == 'imagen':
        if E.get('completa'):
            parts.append(f'<div id="{gid}" class="full"><img src="{esc(E["src"])}"></div>'); pop('#' + gid, a, fx='whoosh', g=0.4, sc=1.1); out('#' + gid, b)
        else:
            grupo(gid, a, b, f'<div class="foto"><img src="{esc(E["src"])}"></div>', 'nada')
    elif tipo == 'video':
        parts.append(f'<div id="{gid}" class="full"><video id="{gid}v" class="clip" data-start="{a:.3f}" data-duration="{b - a:.3f}" data-media-start="0" '
                     f'data-track-index="1" src="{esc(E["src"])}" muted playsinline></video><div class="lab">{esc(E.get("etiqueta", ""))}</div></div>')
        pop('#' + gid, a, fx='whoosh', g=0.45, sc=1.1, dur=0.32, ease='power3.out'); out('#' + gid, b)
    elif tipo == 'tachado':
        cajas = ''.join(f'<div class="xbox" id="{gid}x{k}"><span>{esc(txt)}</span><b class="xx" id="{gid}r{k}">✕</b></div>' for k, (_, txt) in enumerate(E['items']))
        grupo(gid, a, b, f'<div class="xrow">{cajas}</div>', 'nada', fx=None)
        for k, (fr, _) in enumerate(E['items']):
            t = T(fr, a); pop(f'#{gid}x{k}', t - 0.35, fx=None); pop(f'#{gid}r{k}', t, fx='thump', g=0.45, sc=2.4, dur=0.2, ease='power3.out')
    elif tipo == 'chat':
        app = esc(E.get('app', 'WhatsApp'))
        grupo(gid, a, b, f'<div class="chat"><div class="chh">{app}</div><div class="bub">{tipear(gid + "c", E["texto"], a + 0.3, 30)}</div></div>', 'nada', fx='ding')
    elif tipo == 'terminal':
        tc = T(E.get('en', E['desde']), a)
        grupo(gid, a, b, f'<div class="term"><div class="tb"><i></i><i></i><i></i></div><div class="tbody"><div class="cmd">&gt; {tipear(gid + "k", E["comando"], tc, 10)}</div>'
                         f'<div class="res" id="{gid}r">{esc(E.get("resultado", ""))}</div></div></div>', 'nada', fx=None)
        if E.get('resultado'): pop(f'#{gid}r', tc + len(E['comando']) / 10 + 0.3, fx='ding', g=0.2, sc=0.95)
    else:
        raise SystemExit(f'tipo de escena desconocido: {tipo}')

# ---------------- CTA ----------------
ca = T(CTA['desde'])
if ESTILO == 'tablero':
    lines = [f'Comenta <b>“{esc(CTA["palabra"])}”</b>', esc(CTA.get('sub', ''))]
    inner = '<br>'.join(f'<span>{x}</span>' for x in lines if x)
    if CTA.get('usuario'): inner += f'<div class="usr"><span>{esc(CTA["usuario"])}</span></div>'
    parts.append(f'<div id="cta" class="ig" style="top:{safe(ca, DUR, 10)}px">{inner}</div>')
elif ESTILO == 'fucsia':
    parts.append(f'<div id="cta" class="hand big" style="top:{safe(ca, DUR, 60)}px">COMENTA “{esc(CTA["palabra"]).upper()}”</div>')
else:
    parts.append(f'<div id="cta" class="grp" style="top:{safe(ca, DUR)}px"><div class="script">Comenta</div><div class="row"><span class="torn xl">“{esc(CTA["palabra"])}”</span></div>'
                 f'<div class="script sm">{esc(CTA.get("sub", ""))}</div></div>')
pop('#cta', ca, g=0.3, sc=0.7)

# ---------------- CÁMARA: zoom alterno en cada corte + golpes ----------------
tw += K.zoom_alterno(CUT, ZB)
for fr, z, d in ZOOMS:
    t = T(fr); tw.append(f'tl.to("#cam",{{scale:{z},duration:0.14,ease:"power2.out"}},{t - 0.05:.3f});tl.to("#cam",{{scale:1,duration:0.2}},{t + d:.3f});')
    sfx.append((t - 0.05, 'whoosh.wav', 0.3))

# ---------------- SUBTÍTULOS (según estilo) ----------------
caps = []
if ESTILO == 'tablero':                       # una palabra, MAYÚSCULAS (junta palabras de 1-2 letras)
    i = 0; chunks = []
    while i < len(WD):
        ch = [WD[i]]
        while len(K.norm(ch[-1]['text'])) <= 2 and i + 1 < len(WD) and WD[i + 1]['start'] - ch[-1]['end'] < 0.25 and len(ch) < 2:
            i += 1; ch.append(WD[i])
        chunks.append(ch); i += 1
    for k, ch in enumerate(chunks):
        s = ch[0]['start']; nxt = chunks[k + 1][0]['start'] if k + 1 < len(chunks) else DUR
        e = min(max(ch[-1]['end'], s + 0.18) + 0.12, nxt - 0.02)
        caps.append(f'<div id="k{k}" class="cap">{esc(" ".join(x["text"] for x in ch).upper().strip(",."))}</div>')
        init.append(f'gsap.set("#k{k}",{{opacity:0}});'); tw.append(f'tl.set("#k{k}",{{opacity:1}},{max(0, s - 0.03):.3f});tl.set("#k{k}",{{opacity:0}},{e:.3f});')
else:                                          # fucsia: 3-4 palabras con la activa resaltada · stickers: 2-3 palabras
    maxw, maxc = (4, 24) if ESTILO == 'fucsia' else (3, 18)
    lines = []; cur = []
    for w in WD:
        cur.append(w); txt = ' '.join(x['text'] for x in cur)
        if (w['text'][-1:] in '.?!,' and len(cur) >= 2) or len(cur) >= maxw or len(txt) >= maxc: lines.append(cur); cur = []
    if cur: lines.append(cur)
    for li, ln in enumerate(lines):
        s = ln[0]['start']; nxt = lines[li + 1][0]['start'] if li + 1 < len(lines) else DUR
        e = min(ln[-1]['end'] + 0.25, nxt - 0.03)
        if ESTILO == 'fucsia':
            spans = ''.join(f'<span id="w{li}_{k}" class="cw">{esc(x["text"])}</span> ' for k, x in enumerate(ln))
            for k, x in enumerate(ln):
                e2 = ln[k + 1]['start'] if k + 1 < len(ln) else min(x['end'] + 0.1, e)
                tw.append(f'tl.set("#w{li}_{k}",{{backgroundColor:"{COLOR}"}},{x["start"]:.3f});tl.set("#w{li}_{k}",{{backgroundColor:"rgba(0,0,0,0)"}},{e2:.3f});')
        else:
            spans = esc(' '.join(x['text'] for x in ln))
        caps.append(f'<div id="L{li}" class="cap">{spans}</div>')
        init.append(f'gsap.set("#L{li}",{{opacity:0}});'); tw.append(f'tl.set("#L{li}",{{opacity:1}},{max(0, s - 0.04):.3f});tl.set("#L{li}",{{opacity:0}},{e:.3f});')

# ---------------- AUDIO ----------------
if '--sin-audio' not in ARGS:
    K.mix_audio(P, DUR, MUSICA, music_gain=VOLUMEN_MUSICA, sfx=sfx)

# ---------------- HTML ----------------
FUENTES = [('Montserrat', 900, 'montserrat-900'), ('Inter', 400, 'inter-400'), ('Inter', 600, 'inter-600'), ('Inter', 700, 'inter-700'),
           ('Marker', 400, 'permanentmarker-400'), ('Poppins', 700, 'poppins-700'), ('Poppins', 800, 'poppins-800'),
           ('Hand', 400, 'patrickhandsc-400'), ('Caveat', 700, 'caveat-700'), ('Serif', 400, 'dmserifdisplay-400'), ('JBM', 600, 'jetbrainsmono-600')]
K.copy_fonts(P, [f for _, _, f in FUENTES])
cx, cy = int(FACE.cx), int(FACE.cy)
CAPCSS = {
 'tablero': '.cap{top:1590px;font-family:"Montserrat";font-weight:900;font-size:70px;letter-spacing:1px;text-shadow:0 5px 0 rgba(0,0,0,.9),0 0 22px rgba(0,0,0,.6)}',
 'fucsia': '.cap{top:1600px;font-family:"Poppins";font-weight:700;font-size:52px;text-shadow:0 3px 8px rgba(0,0,0,.85),0 0 2px #000}.cw{padding:2px 10px;border-radius:10px}',
 'stickers': '.cap{top:1610px;font-family:"Poppins";font-weight:700;font-size:50px;text-shadow:0 3px 8px rgba(0,0,0,.9),0 0 2px #000}',
}[ESTILO]
CSS = K.font_faces(FUENTES) + f'''
*{{margin:0;padding:0;box-sizing:border-box}}
#root{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#000;font-family:"Inter",sans-serif}}
#cam{{position:absolute;inset:0;transform-origin:{cx}px {cy}px}}
#v{{position:absolute;inset:0;width:{W}px;height:{H}px;object-fit:cover}}
{K.CROP_CSS if QUITAR_MARCA else '#crop{position:absolute;inset:0}'}
.grp{{position:absolute;left:0;width:{W}px;z-index:30;display:flex;flex-direction:column;align-items:center;gap:10px}}
/* tablero: pizarra blanca con letra de marcador */
.board{{left:70px;width:940px;background:#fbfbf8;border:9px solid #cfd4d9;border-radius:20px;padding:24px 34px 28px;box-shadow:0 20px 50px rgba(0,0,0,.45)}}
.board .ttl{{font-family:"Marker";font-size:60px;color:#1d1d1f}} .board .item{{font-family:"Marker";font-size:50px;color:#1d1d1f;align-self:flex-start;margin-left:30px}}
.board .big{{font-family:"Marker";font-size:110px;color:{COLOR}}} .board .sub{{font-family:"Marker";font-size:46px;color:#1d1d1f}}
/* fucsia: tarjetas oscuras con brillo */
.dark{{left:80px;width:920px;background:#0d1117;border:2px solid #30363d;border-radius:22px;padding:28px 36px;box-shadow:0 0 0 5px rgba(255,255,255,.7),0 0 30px rgba(255,255,255,.4),0 18px 40px rgba(0,0,0,.5)}}
.dark .ttl{{font-family:"Inter";font-weight:700;font-size:46px;color:#f0f6fc}} .dark .item{{font-family:"Inter";font-weight:600;font-size:44px;color:#c9d1d9;align-self:flex-start;margin-left:20px}}
.dark .big{{font-family:"Poppins";font-weight:800;font-size:110px;color:{COLOR};line-height:1}} .dark .sub{{font-family:"Inter";font-weight:600;font-size:40px;color:#c9d1d9}}
/* stickers: etiquetas de marcador sobre papel */
.stk .ttl{{font-family:"Caveat";font-size:78px;color:#fff;text-shadow:0 3px 10px rgba(0,0,0,.75)}}
.stk .item{{font-family:"Marker";font-size:50px;color:#111;background:#fff;padding:8px 24px;border-radius:10px;box-shadow:0 8px 18px rgba(0,0,0,.4)}}
.stk .big{{font-family:"Serif";font-size:110px;color:#111;background:#fdfdfb;padding:4px 30px 10px;box-shadow:0 8px 18px rgba(0,0,0,.4)}} .stk .sub{{font-family:"Caveat";font-size:60px;color:#fff;text-shadow:0 3px 10px rgba(0,0,0,.75)}}
.nada{{}}
/* gancho / CTA */
.ig{{position:absolute;left:0;width:{W}px;text-align:center;z-index:30;font-family:"Inter";font-weight:700;font-size:54px;line-height:1.36}}
.ig span{{background:#fff;color:#111;padding:6px 22px;border-radius:16px;-webkit-box-decoration-break:clone;box-decoration-break:clone;box-shadow:0 6px 18px rgba(0,0,0,.22)}}
.ig b{{font-weight:800}} .ig .usr{{margin-top:22px;font-size:42px}}
.hand{{position:absolute;left:0;width:{W}px;text-align:center;z-index:30;font-family:"Hand";font-size:74px;line-height:1.08;color:#fff;letter-spacing:1px;text-shadow:0 0 2px #000,0 2px 2px rgba(0,0,0,.9),0 4px 14px rgba(0,0,0,.55)}}
.hand.big{{font-size:96px}}
.script{{font-family:"Caveat";font-size:84px;color:#fff;line-height:1;text-shadow:0 3px 10px rgba(0,0,0,.75),0 0 2px #000}} .script.sm{{font-size:60px}}
.row{{display:flex;justify-content:center}}
.torn{{display:inline-block;font-family:"Serif";font-size:84px;color:#111;background:#fdfdfb;padding:6px 30px 12px;line-height:1.05;transform:rotate(-2deg);
  clip-path:polygon(0% 8%,4% 0%,9% 6%,15% 1%,22% 7%,30% 2%,37% 8%,45% 1%,53% 7%,61% 2%,69% 8%,77% 1%,85% 7%,92% 2%,100% 7%,99% 93%,94% 100%,88% 94%,80% 99%,72% 93%,64% 100%,56% 94%,48% 99%,40% 93%,32% 100%,24% 94%,16% 99%,8% 93%,1% 99%);filter:drop-shadow(0 8px 14px rgba(0,0,0,.45))}}
.torn.xl{{font-size:130px}}
/* logos y fichas */
.tiles{{display:flex;align-items:center;gap:26px}} .tile{{width:240px;height:180px;border-radius:28px;background:#fff;border:3px solid #e6e6e6;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px}}
.tile svg{{width:90px;height:90px}} .tile span{{font-family:"Poppins";font-weight:800;font-size:34px;color:#111}} .plus{{font-family:"Marker";font-size:70px;color:#1d1d1f}}
.lgcard{{display:flex;align-items:center;gap:22px;border-radius:22px;padding:30px 50px;box-shadow:0 0 0 5px rgba(255,255,255,.75),0 0 34px rgba(255,255,255,.55),0 18px 40px rgba(0,0,0,.45)}}
.lgcard.oscuro{{background:#0b0b0c;color:#fff}} .lgcard.claro{{background:#fff;color:#111}} .lgcard svg{{width:96px;height:96px}} .lgcard span{{font-family:"Inter";font-weight:600;font-size:76px}}
.about{{width:900px;background:#0d1117;border:2px solid #30363d;border-radius:20px;padding:30px 38px;box-shadow:0 0 0 5px rgba(255,255,255,.7),0 0 30px rgba(255,255,255,.45),0 18px 40px rgba(0,0,0,.5)}}
.abh{{font-family:"Inter";font-weight:700;font-size:44px;color:#f0f6fc;margin-bottom:14px}} .abd{{font-family:"Inter";font-weight:400;font-size:40px;line-height:1.38;color:#c9d1d9}}
.abl{{margin-top:16px;font-family:"Inter";font-weight:600;font-size:36px;color:#4493f8}}
/* imagen / video real */
.foto{{width:900px;border-radius:22px;overflow:hidden;border:6px solid #fff;box-shadow:0 20px 50px rgba(0,0,0,.55)}} .foto img{{display:block;width:100%;max-height:440px;object-fit:cover}}
.full{{position:absolute;inset:0;z-index:35;background:#000}} .full img,.full video{{position:absolute;inset:0;width:{W}px;height:{H}px;object-fit:cover}}
.lab{{position:absolute;left:50%;transform:translateX(-50%);bottom:440px;white-space:nowrap;background:rgba(10,10,12,.88);color:#fff;font-family:"Poppins";font-weight:700;font-size:42px;padding:14px 30px;border-radius:40px}}
/* tachado */
.xrow{{display:flex;gap:36px;justify-content:center}} .xbox{{position:relative;background:#fff;border-radius:16px;padding:22px 34px;font-family:"Marker";font-size:52px;color:#111;box-shadow:0 10px 24px rgba(0,0,0,.4)}}
.xx{{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-family:"Poppins";font-weight:800;font-size:150px;color:#E5322D;line-height:1}}
/* chat y terminal */
.chat{{width:900px;background:#ECE5DD;border-radius:28px;padding:20px 26px 30px;box-shadow:0 18px 40px rgba(0,0,0,.45)}} .chh{{font-family:"Inter";font-weight:700;font-size:32px;color:#075E54;margin-bottom:12px}}
.bub{{background:#DCF8C6;color:#111;font-family:"Inter";font-weight:600;font-size:44px;line-height:1.3;padding:22px 30px;border-radius:26px 26px 26px 6px}}
.term{{width:900px;background:#1b1b1f;border-radius:22px;overflow:hidden;border:2px solid #34343c;box-shadow:0 20px 50px rgba(0,0,0,.55)}}
.tb{{display:flex;gap:10px;background:#26262b;padding:14px 20px}} .tb i{{width:16px;height:16px;border-radius:50%;background:#ff5f57}} .tb i:nth-child(2){{background:#febc2e}} .tb i:nth-child(3){{background:#28c840}}
.tbody{{padding:24px 32px 30px;font-family:"JBM";font-weight:600}} .cmd{{font-size:60px;color:#fff}} .res{{margin-top:14px;font-size:32px;color:#4ade80}}
/* subtítulos */
.cap{{position:absolute;left:0;width:{W}px;text-align:center;z-index:45;color:#fff}}
{CAPCSS}
'''
HTML = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
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
print(f'OK index.html | estilo {ESTILO} | {DUR}s | escenas {len(ESCENAS)} | subtítulos {len(caps)} | efectos {len(sfx)}')
