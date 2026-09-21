# -*- coding: utf-8 -*-
# PLANTILLA — capa de graficos (OVERLAY) para un reel vertical grabado con iPhone (HDR).
#
# Idea: HyperFrames renderiza SOLO los graficos sobre fondo MAGENTA (#FF00FF) y ffmpeg los
# pega con chromakey sobre el video original, que NUNCA se toca (conserva el HDR del iPhone).
#
# Archivos que espera en la carpeta del proyecto:
#   words_fixed.json   -> [{"text","start","end"}, ...] (transcripcion corregida)
#   assets/            -> b-roll (1080x1920, 60fps) e imagenes IA (1080x1920)
#   preview_base.mp4   -> SOLO para el modo preview: copia SDR del crudo con el audio mezclado
#       ffmpeg -i source.mp4 -i final_audio.wav -map 0:v -map 1:a -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,fps=30" -c:v libx264 -preset veryfast -crf 22 -c:a aac preview_base.mp4
#
# Uso:
#   python build_overlay.py preview  -> index.html con el crudo debajo, para revisar en `npx hyperframes preview .`
#   python build_overlay.py          -> index.html magenta, para `npx hyperframes render . --fps 60 --quality high --crf 14`
# (El comando de composicion final esta en SKILL.md, seccion "iPhone HDR reels".)
#
# Reglas que ya estan resueltas aqui:
#   - Todo se anima SOLO con scale (un fade a medias se mezcla con el magenta y el chroma no lo quita).
#   - Centrado con GSAP xPercent/yPercent (con translate(-50%) en CSS las tarjetas salen corridas).
#   - Las listas se encienden UNA POR UNA en el segundo en que se dice cada palabra.
#   - Tarjetas en la franja entre el menton y los subtitulos (Instagram recorta arriba y abajo).
import json, html, sys
PREVIEW = len(sys.argv) > 1 and sys.argv[1] == "preview"
W, H = 1080, 1920
DUR = 60.00                      # duracion EXACTA del crudo (ffprobe), no la de la transcripcion
CARD_TOP = 1260                  # centro de las tarjetas: medir el menton (drawgrid) y dejar >= 100px de aire
GOLD = "#F5C542"; GREEN = "#22C55E"; INK = "#0E0E12"; TERRA = "#D97757"; RED = "#B4402F"

# b-roll a pantalla completa: (id, archivo, "v" video | "i" imagen, inicio, duracion)
CUTS = [
 ("c1", "assets/p_ejemplo.mp4",   "v",  2.00, 2.60),   # primer apoyo ~seg 2 (antes: cara + gancho)
 ("c2", "assets/ia-ejemplo.png",  "i",  6.00, 3.00),
]

# tarjetas simples: (id, aparece, se va, html, clase extra: "" o "top")
CARDS = [
 ("hook", 0.15, 2.75,
  '<div class="hook"><span class="h1">TU GANCHO AQU&Iacute;</span>'
  '<span class="h2">subt&iacute;tulo del <b>gancho</b></span></div>', ""),
 ("dato", 6.20, 8.80, '<div class="money"><b>+5.000 USD</b><span>extra al mes</span></div>', ""),
 ("cta", DUR - 4.0, DUR,
  '<div class="cta"><span class="c1">Comenta</span><span class="c2">PALABRA</span>'
  '<span class="c3">y te env&iacute;o el video &#128071;</span></div>', ""),
]

# listas que se encienden una por una: (id, entra, sale, layout "stack"|"gk", [(item, segundo_de_la_palabra, html)])
def step(n, txt):
    return '<div class="li"><span class="lin">%s</span>%s</div>' % (n, txt)

GROUPS = [
 ("pasos", 10.00, 18.00, "stack", [
   ("p0", 10.20, step(1, "Primer paso")),
   ("p1", 13.40, step(2, "Segundo paso")),
   ("p2", 16.10, step(3, "Tercer paso"))]),
 ("pills", 20.00, 24.00, "stack", [
   ("q0", 20.30, '<div class="pill">M&aacute;s r&aacute;pido</div>'),
   ("q1", 21.40, '<div class="pill g">M&aacute;s barato</div>')]),
]

# subtitulos: SUB_HOLE los oculta mientras suena un clip con su propia voz/texto; SUB_END = cuando entra el CTA
SUB_HOLE = (0.0, 0.0)
SUB_END = DUR - 4.0

init = []; tw = []; parts = []

if PREVIEW:
    parts.append('<video id="base" class="clip" data-start="0" data-duration="%.2f" data-media-start="0" '
                 'data-track-index="0" src="preview_base.mp4" data-has-audio="true" playsinline></video>' % DUR)

for cid, src, kind, st, dur in CUTS:
    if kind == "v":
        parts.append('<video id="%s" class="cut clip" data-start="%.2f" data-duration="%.2f" '
                     'data-media-start="0" data-track-index="1" src="%s" muted playsinline></video>'
                     % (cid, st, dur, src))
    else:
        parts.append('<img id="%s" class="cut clip" data-start="%.2f" data-duration="%.2f" '
                     'data-track-index="1" src="%s">' % (cid, st, dur, src))
    init.append('gsap.set("#%s",{opacity:0,scale:1.10});' % cid)
    tw.append('tl.set("#%s",{opacity:1},%.2f);' % (cid, st))
    tw.append('tl.to("#%s",{scale:1.0,duration:%.2f,ease:"none"},%.2f);' % (cid, dur, st))
    tw.append('tl.set("#%s",{opacity:0},%.2f);' % (cid, st + dur - 0.05))

for cid, s, e, inner, extra in CARDS:
    parts.append('<div class="card %s" id="%s">%s</div>' % (extra, cid, inner))
    init.append('gsap.set("#%s",{xPercent:-50,yPercent:-50,scale:0.001});' % cid)
    tw.append('tl.to("#%s",{scale:1,duration:0.36,ease:"back.out(1.7)"},%.2f);' % (cid, s))
    tw.append('tl.to("#%s",{scale:0.001,duration:0.22,ease:"power2.in"},%.2f);' % (cid, e))

for gid, gin, gout, lay, items in GROUPS:
    inner = "".join('<div class="it" id="%s">%s</div>' % (iid, h) for iid, _, h in items)
    parts.append('<div class="card" id="%s"><div class="%s">%s</div></div>' % (gid, lay, inner))
    init.append('gsap.set("#%s",{xPercent:-50,yPercent:-50,opacity:0,scale:1});' % gid)
    tw.append('tl.set("#%s",{opacity:1},%.2f);' % (gid, gin))
    for iid, t, _ in items:
        init.append('gsap.set("#%s",{scale:0.001});' % iid)
        tw.append('tl.to("#%s",{scale:1,duration:0.30,ease:"back.out(1.9)"},%.2f);' % (iid, max(gin, t - 0.10)))
    tw.append('tl.to("#%s",{scale:0.001,duration:0.24,ease:"power2.in"},%.2f);' % (gid, gout))

words = json.load(open("words_fixed.json", encoding="utf-8"))
chunks = []; cur = []
for wd in words:
    if wd["start"] >= SUB_END:
        break
    if SUB_HOLE[0] <= wd["start"] < SUB_HOLE[1]:
        if cur:
            chunks.append(cur); cur = []
        continue
    cur.append(wd)
    txt = " ".join(x["text"] for x in cur)
    if cur[-1]["text"][-1:] in ".,!?" or len(cur) >= 2 or len(txt) >= 15:
        chunks.append(cur); cur = []
if cur:
    chunks.append(cur)

caps = []
for i, ch in enumerate(chunks):
    s = ch[0]["start"]; e = ch[-1]["end"]
    nxt = chunks[i + 1][0]["start"] if i + 1 < len(chunks) else e + 0.4
    hide = min(e + 0.20, nxt - 0.06, SUB_END)        # -0.06: nunca dos subtitulos a la vez
    if s < SUB_HOLE[0] < hide:
        hide = SUB_HOLE[0]
    caps.append('<div id="cap%d" class="cap">%s</div>' % (i, html.escape(" ".join(x["text"] for x in ch))))
    init.append('gsap.set("#cap%d",{opacity:0});' % i)
    tw.append('tl.set("#cap%d",{opacity:1},%.2f);' % (i, max(0, s - 0.04)))
    tw.append('tl.set("#cap%d",{opacity:0},%.2f);' % (i, hide))

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@800;900&family=Poppins:wght@600;700;800;900&family=Anton&display=swap');
*{margin:0;padding:0;box-sizing:border-box}
#root{position:relative;width:1080px;height:1920px;overflow:hidden;background:__BG__;font-family:'Poppins',sans-serif}
#base{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;z-index:1}
.cut{position:absolute;left:0;top:0;width:1080px;height:1920px;object-fit:cover;z-index:10}
.card{position:absolute;left:50%;top:__TOP__px;z-index:24;display:flex;justify-content:center}
.card.top{top:410px}
.hook{display:flex;flex-direction:column;align-items:center;gap:2px;background:rgba(10,10,14,.93);border:5px solid __RED__;border-radius:26px;padding:14px 40px 16px;box-shadow:0 16px 42px rgba(0,0,0,.65)}
.hook .h1{font-family:'Anton';font-size:76px;color:#fff;line-height:1.05;white-space:nowrap}
.hook .h2{font-weight:800;font-size:40px;color:#e6e6ea;white-space:nowrap}
.hook .h2 b{color:#FF5A45;font-weight:900}
.money{display:flex;flex-direction:column;align-items:center;background:rgba(10,10,14,.93);border:5px solid __GREEN__;border-radius:26px;padding:12px 44px 14px;box-shadow:0 16px 42px rgba(0,0,0,.65)}
.money b{font-family:'Anton';font-size:88px;color:__GREEN__;line-height:1.02;white-space:nowrap;font-weight:400}
.money span{font-weight:800;font-size:38px;color:#fff;white-space:nowrap}
.stack{display:flex;flex-direction:column;gap:12px;align-items:center}
.li{display:flex;align-items:center;gap:16px;background:rgba(12,12,16,.93);border:2px solid rgba(255,255,255,.30);border-radius:16px;padding:12px 28px;font-weight:800;font-size:40px;color:#fff;box-shadow:0 10px 26px rgba(0,0,0,.65);white-space:nowrap;min-width:760px}
.lin{font-family:'Anton';font-size:42px;color:#06210F;background:__GOLD__;width:58px;height:58px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex:none}
.gk{display:grid;grid-template-columns:1fr 1fr;gap:12px 14px}
.pill{background:__TERRA__;color:#fff;font-weight:900;font-size:46px;padding:12px 36px;border-radius:40px;box-shadow:0 10px 26px rgba(0,0,0,.6);white-space:nowrap}
.pill.g{background:__INK__;border:3px solid __GREEN__}
.cta{display:flex;flex-direction:column;align-items:center;background:rgba(10,10,14,.95);border:6px solid __TERRA__;border-radius:30px;padding:24px 56px;box-shadow:0 18px 46px rgba(0,0,0,.65)}
.cta .c1{font-weight:700;font-size:44px;color:#fff}
.cta .c2{font-family:'Anton';font-size:96px;color:__TERRA__;letter-spacing:3px;line-height:1.05}
.cta .c3{font-weight:700;font-size:30px;color:#e8e8ea;margin-top:6px;white-space:nowrap}
.cap{position:absolute;left:50%;top:1545px;transform:translateX(-50%);z-index:26;opacity:0;font-family:'Nunito';font-weight:900;font-size:60px;color:#fff;text-align:center;white-space:nowrap;-webkit-text-stroke:3px #000;paint-order:stroke fill;text-shadow:0 3px 8px rgba(0,0,0,.95)}
"""
for k, v in (("__GOLD__", GOLD), ("__GREEN__", GREEN), ("__INK__", INK), ("__TERRA__", TERRA),
             ("__RED__", RED), ("__TOP__", str(CARD_TOP)), ("__BG__", "#000" if PREVIEW else "#FF00FF")):
    CSS = CSS.replace(k, v)

HTML = (
 '<!doctype html><html lang="es"><head><meta charset="utf-8"><style>' + CSS + '</style></head><body>\n'
 '<div data-hf-id="root" id="root" data-composition-id="main" data-start="0" data-duration="%s" data-width="%d" data-height="%d">\n' % (DUR, W, H)
 + "".join(parts) + "\n" + "".join(caps) + '\n</div>\n'
 '<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>\n'
 '<script>const tl=gsap.timeline({paused:true});window.__timelines={"main":tl};\n'
 + "\n".join(init) + "\n" + "\n".join(tw) + "\n</script></body></html>"
)
open("index.html", "w", encoding="utf-8").write(HTML)
print("OK%s | b-roll:" % (" [PREVIEW]" if PREVIEW else ""), len(CUTS), "| tarjetas:", len(CARDS),
      "| listas:", len(GROUPS), "| subtitulos:", len(chunks))
