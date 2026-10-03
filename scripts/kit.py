# -*- coding: utf-8 -*-
"""
video-imperio-edit · KIT  — piezas comunes que usan las plantillas (build.py de cada proyecto).

    import sys; SKILL = open('_work/skill.txt', encoding='utf-8').read().strip()
    sys.path.insert(0, SKILL + '/scripts'); import kit as K

  K.load_words(P, fixes)          palabras del video cortado (words.json) con correcciones de nombres
  K.find(words, 'frase', after)   segundo en que empieza esa frase (K.find_end: en que termina)
  K.Face(P, crop)                 zona segura: .safe_top(t0, t1, zoom) = 'top' mínimo para NO tapar la cara
  K.mix_audio(P, DUR, ...)        voz limpia + música nivelada que baja cuando hablas + efectos -> final_audio.wav
  K.copy_fonts / K.font_faces     fuentes de recursos/fonts al proyecto (@font-face)
  K.logo_svg('claude', color)     logo SVG de recursos/logos, coloreado
  K.CROP_WM / K.CROP_CSS          mini zoom fijo que saca de cuadro una marca de agua de esquina (p. ej. BIGVU)
  K.zoom_alterno(cutmap, z)       acercamiento alterno en cada corte (esconde los saltos)
"""
import json, os, re, subprocess, statistics, shutil

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SFX = os.path.join(SKILL, 'recursos', 'sfx')
MUSIC = os.path.join(SKILL, 'recursos', 'musica')
FONTS = os.path.join(SKILL, 'recursos', 'fonts')
LOGOS = os.path.join(SKILL, 'recursos', 'logos')

# ---------------- palabras ----------------
def norm(s): return re.sub(r'[^\wáéíóúñü]', '', s.lower())

def load_words(proj, fixes=None, splitY=True):
    W = json.load(open(os.path.join(proj, 'words.json'), encoding='utf-8'))
    out = []
    for w in W:
        t = w['text']
        # whisper a veces pega la "Y" a la palabra siguiente ("Yyo") -> separar
        if splitY and re.match(r'^Y[a-záéíóúñ]', t) and t.lower() not in ('ya', 'yo', 'yoga'):
            mid = w['start'] + 0.08
            out.append({'text': 'Y', 'start': w['start'], 'end': mid}); out.append({**w, 'text': t[1:], 'start': mid}); continue
        out.append(dict(w))
    for w in out:
        for a, b in (fixes or {}).items():                  # {'cloud': 'Claude'} -> corrige respetando la puntuación
            if norm(w['text']) == norm(a):
                core = re.sub(r'[^\wáéíóúñü$]', '', w['text'])
                w['text'] = w['text'].replace(core, b) if core else b
    return out

def find(words, phrase, after=0.0):
    """segundo en que EMPIEZA la primera aparición de `phrase` después de `after`"""
    ws = [norm(x) for x in phrase.split()]
    for i in range(len(words)):
        if words[i]['start'] < after: continue
        if [norm(x['text']) for x in words[i:i + len(ws)]] == ws:
            return words[i]['start']
    raise SystemExit(f'NO ENCONTRADO en words.json: "{phrase}" (después de {after:.1f}s). Revisa cómo quedó escrita en el guion.')

def find_end(words, phrase, after=0.0):
    ws = [norm(x) for x in phrase.split()]
    for i in range(len(words)):
        if words[i]['start'] < after: continue
        if [norm(x['text']) for x in words[i:i + len(ws)]] == ws:
            return words[i + len(ws) - 1]['end']
    raise SystemExit(f'NO ENCONTRADO en words.json: "{phrase}" (después de {after:.1f}s).')

# ---------------- cara ----------------
class Face:
    """Zona segura bajo la barbilla (face.json de preparar.py). crop = mini zoom fijo anclado arriba (ver CROP_WM)."""
    def __init__(self, proj, crop=1.0):
        F = json.load(open(os.path.join(proj, 'face.json')))
        W = F.get('W', 1080)
        self.tr = [dict(f) for f in F['track'] if f.get('ok') and 0.12 * W <= f['w'] <= 0.5 * W]
        if not self.tr: self.tr = [dict(f) for f in F['track'] if f.get('ok')]
        for f in self.tr:
            f['x'] = 540 + (f['x'] - 540) * crop; f['y'] *= crop; f['w'] *= crop; f['h'] *= crop; f['chin'] *= crop
        self.cx = statistics.median([f['x'] + f['w'] / 2 for f in self.tr])
        self.cy = statistics.median([f['y'] + f['h'] / 2 for f in self.tr])
        self.chin_med = statistics.median([f['chin'] for f in self.tr])

    def chin(self, t0, t1):
        s = sorted(f['chin'] for f in self.tr if t0 - 0.3 <= f['t'] <= t1 + 0.3)
        if not s: return self.chin_med
        return s[int(len(s) * 0.9)] if len(s) > 4 else s[-1]            # percentil 90 (ignora un cuadro raro)

    def safe_top(self, t0, t1, zoom=1.0, margin=40, lo=1000, hi=1230):
        """'top' mínimo (px) para que un elemento visible entre t0 y t1 quede DEBAJO de la barbilla."""
        c = self.cy + (self.chin(t0, t1) - self.cy) * zoom                # con zoom la barbilla baja
        return int(min(hi, max(lo, c + margin)))

# ---------------- cámara ----------------
def zoom_alterno(cutmap, z=1.10, sel='#cam'):
    """lista de tweens GSAP: alterna 1.0 / z en cada corte del video (como en los reels de referencia)."""
    tw = [f'gsap.set("{sel}",{{scale:1}});']; acc = 0.0; cur = 1.0
    for s0, s1 in cutmap['keep'][:-1]:
        acc += s1 - s0; cur = z if cur == 1.0 else 1.0
        tw.append(f'tl.set("{sel}",{{scale:{cur}}},{acc:.3f});')
    return tw

# marca de agua en una esquina de abajo (p. ej. "RECORDED ON BIGVU", y≈1805-1899 en 1080x1920):
# NUNCA taparla con una caja (se ve feo). Mini zoom fijo anclado arriba-centro que la saca del cuadro.
CROP_WM = 1.075
CROP_CSS = f'#crop{{position:absolute;inset:0;transform:scale({CROP_WM});transform-origin:540px 0px}}'

# ---------------- audio ----------------
def _run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode: raise SystemExit(r.stderr[-1500:])
    return r

def elegir_musica(music):
    """'auto' = la primera pista de recursos/musica; None/'' = sin música; o una ruta."""
    if not music: return None
    if music == 'auto':
        if not os.path.isdir(MUSIC): return None
        pistas = sorted(f for f in os.listdir(MUSIC) if f.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg', '.flac')))
        return os.path.join(MUSIC, pistas[0]) if pistas else None
    if os.path.isfile(music): return music
    cand = os.path.join(MUSIC, music)
    return cand if os.path.isfile(cand) else None

def mix_audio(proj, dur, music='auto', music_start=0.0, music_gain=0.28, sfx=None, out='final_audio.wav'):
    """voz limpia (-16 LUFS) + música nivelada (-14 LUFS x music_gain) que se aparta cuando hablas + efectos
       sfx = [(segundo, 'pop.wav', ganancia), ...] (archivos de recursos/sfx). Resultado ≈ -14 LUFS, pico -1.5 dB."""
    wk = os.path.join(proj, '_work'); voice = os.path.join(proj, 'voice.wav')
    _run(['ffmpeg', '-y', '-v', 'error', '-i', os.path.join(wk, 'voice_raw.wav'), '-af',
          'highpass=f=85,equalizer=f=3000:width_type=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3:attack=10:release=200:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=11',
          '-ar', '48000', '-ac', '1', voice])
    pista = elegir_musica(music)
    ins = ['-i', voice]; fc = []; mixes = []
    if pista:
        mus = os.path.join(wk, 'music_lvl.wav')
        _run(['ffmpeg', '-y', '-v', 'error', '-ss', str(music_start), '-stream_loop', '-1', '-i', pista, '-t', f'{dur:.3f}',
              '-af', f'loudnorm=I=-14:TP=-1.5:LRA=7,afade=t=in:d=0.4,afade=t=out:st={max(0, dur - 1.4):.3f}:d=1.3',
              '-ar', '48000', '-ac', '2', mus])
        ins += ['-i', mus]
        fc += [f'[1:a]volume={music_gain}[m]', '[0:a]asplit=2[v1][vsc]',
               '[m][vsc]sidechaincompress=threshold=0.10:ratio=3:attack=15:release=320:makeup=1[duck]']
        mixes = ['[v1]', '[duck]']
    else:
        print('  (aviso) sin música: deja una pista en recursos/musica/ o pásala con music="ruta.mp3"')
        fc.append('[0:a]anull[v1]'); mixes = ['[v1]']
    base = len(ins) // 2
    for k, (t, f, g) in enumerate(sfx or []):
        ins += ['-i', os.path.join(SFX, f)]; ms = max(0, int(round(t * 1000)))
        fc.append(f'[{base + k}:a]volume={g},adelay={ms}|{ms}[s{k}]'); mixes.append(f'[s{k}]')
    fc.append(f'{"".join(mixes)}amix=inputs={len(mixes)}:duration=first:normalize=0,atrim=0:{dur:.3f}[mx]')
    fc.append('[mx]loudnorm=I=-14:TP=-1.5:LRA=11[out]')
    _run(['ffmpeg', '-y', '-v', 'error', *ins, '-filter_complex', ';'.join(fc), '-map', '[out]', '-ar', '48000', '-ac', '2', os.path.join(proj, out)])
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', os.path.join(proj, out), '-af', 'volumedetect', '-f', 'null', '-'], capture_output=True, text=True).stderr
    mv = re.search(r'mean_volume: (\S+)', r).group(1); mx = re.search(r'max_volume: (\S+)', r).group(1)
    print(f'audio OK -> {out} | media {mv} dB, pico {mx} dB | música: {os.path.basename(pista) if pista else "ninguna"} | efectos {len(sfx or [])}')

# ---------------- fuentes y logos ----------------
def copy_fonts(proj, files):
    os.makedirs(os.path.join(proj, 'fonts'), exist_ok=True)
    for f in files: shutil.copy(os.path.join(FONTS, f + '.woff2'), os.path.join(proj, 'fonts', f + '.woff2'))

def font_faces(names):
    return ''.join(f'@font-face{{font-family:"{fam}";font-weight:{w};font-display:block;src:url("fonts/{f}.woff2") format("woff2");}}\n' for fam, w, f in names)

def logo_svg(name, color):
    p = os.path.join(LOGOS, name + '.svg')
    if not os.path.exists(p):
        raise SystemExit(f'No está el logo "{name}". Descárgalo de https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/{name}.svg a {p}')
    return open(p, encoding='utf-8').read().replace('<svg ', f'<svg fill="{color}" ', 1)
