# -*- coding: utf-8 -*-
"""
video-imperio-edit · HOJA  — hoja de contacto con la hora de cada cuadro (para REVISAR un video sin reproducirlo).

    python hoja.py <video> <salida.jpg> [inicio] [fin] [paso] [columnas] [ancho_celda]
    python hoja.py renders/borrador.mp4 _work/rev1.jpg 0 15 0.25 12 166     # un cuadro cada 0.25 s, de 0 a 15 s

Úsala para: estudiar un video de referencia, y para revisar tu borrador ANTES de mostrarlo
(¿algo tapa la cara?, ¿los textos caben?, ¿cada pieza entra cuando se dice?).
"""
import sys, cv2
from PIL import Image, ImageDraw, ImageFont

def fuente(tam):
    for f in ('C:/Windows/Fonts/arialbd.ttf', '/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        try: return ImageFont.truetype(f, tam)
        except Exception: pass
    return ImageFont.load_default()

def main():
    if len(sys.argv) < 3: raise SystemExit(__doc__)
    src, out = sys.argv[1], sys.argv[2]
    cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
    t0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
    t1 = float(sys.argv[4]) if len(sys.argv) > 4 else total - 0.05
    step = float(sys.argv[5]) if len(sys.argv) > 5 else max(0.25, (t1 - t0) / 60)
    cols = int(sys.argv[6]) if len(sys.argv) > 6 else 10
    cw = int(sys.argv[7]) if len(sys.argv) > 7 else 200
    Wv = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); Hv = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)); ch = int(cw * Hv / Wv)
    font = fuente(max(14, cw // 11)); ims = []; t = t0
    while t <= min(t1, total) + 1e-6:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(t * fps))); ok, fr = cap.read()
        if not ok: break
        im = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).resize((cw, ch), Image.LANCZOS)
        d = ImageDraw.Draw(im); lab = f'{t:.2f}'; bb = d.textbbox((0, 0), lab, font=font)
        d.rectangle([0, 0, bb[2] + 10, bb[3] + 8], fill=(0, 0, 0)); d.text((5, 2), lab, font=font, fill=(255, 235, 60))
        ims.append(im); t += step
    if not ims: raise SystemExit('no pude leer cuadros de ' + src)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * cw, rows * ch), (30, 30, 30))
    for i, im in enumerate(ims): sheet.paste(im, ((i % cols) * cw, (i // cols) * ch))
    sheet.save(out, quality=88); print(out, len(ims), 'cuadros', sheet.size)


if __name__ == '__main__':
    main()
