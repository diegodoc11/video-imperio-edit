# -*- coding: utf-8 -*-
"""
video-imperio-edit · PREPARAR  — del video crudo al proyecto listo para editar.

    python preparar.py <video> <carpeta_proyecto> [--idioma es] [--modelo large-v3] [--sin-silencios]

Hace, en orden:
  1. copia el crudo como source.mp4 y saca el audio
  2. transcribe con whisper (tiempos por palabra, modo DTW)                 -> _work/wdtw.json
  3. quita los silencios largos (y los tramos de _work/cortes.json, si existe) -> cut.mp4 (1080x1920, 30 fps, SDR) + _work/voice_raw.wav
  4. transcribe de nuevo el audio YA cortado (tiempos exactos del video final) -> words.json
  5. sigue la cara cuadro a cuadro (para no tapar nunca la cara)             -> face.json
  6. deja en el proyecto la ruta de la skill (_work/skill.txt), que usan las plantillas

Para quitar equivocaciones / repeticiones: corre frases.py, escribe los tramos malos en _work/cortes.json
( [[inicio, fin], ...] en segundos del CRUDO ) y vuelve a correr preparar.py.
"""
import sys, os, json, re, shutil, subprocess, wave
import numpy as np

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30
MIN_SIL = 0.40   # pausas más largas que esto se acortan
KEEP = 0.12      # aire que se deja a cada lado de una pausa acortada
PRE, POST = 0.06, 0.45
DTW = {'large-v3': 'large.v3', 'large-v3-turbo': 'large.v3.turbo', 'medium': 'medium', 'small': 'small', 'base': 'base'}


def arg(name, default=None):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode: raise SystemExit('ERROR al correr: ' + ' '.join(map(str, cmd[:6])) + ' …\n' + (r.stderr or r.stdout)[-1500:])
    return r

def buscar_modelo(nombre):
    """Ruta del modelo de whisper. Si no está el pedido, usa el mejor que haya instalado y avisa."""
    env = os.environ.get('VIDEO_IMPERIO_WHISPER', '') or os.environ.get('REEL_MOTION_WHISPER', '')
    if env and os.path.isfile(env): return env
    dirs = [os.path.join(SKILL, 'modelos'), os.path.expanduser('~/.cache/hyperframes/whisper/models'), os.path.expanduser('~/.cache/whisper'),
            os.path.expanduser('~/.claude/skills/reel-motion/modelos')]
    for n in [nombre] + [m for m in ('large-v3', 'large-v3-turbo', 'medium', 'small', 'base') if m != nombre]:
        for d in dirs:
            c = os.path.join(d, f'ggml-{n}.bin')
            if os.path.isfile(c):
                if n != nombre: print(f'  (aviso) no está el modelo de whisper "{nombre}"; uso "{n}".', flush=True)
                return c
    raise SystemExit(f'No encuentro ningún modelo de whisper (ggml-{nombre}.bin). Corre:  python scripts/instalar.py   (lo descarga).')

def whisper_palabras(wav, salida_sin_ext, modelo, idioma):
    """whisper.cpp con tiempos por palabra (DTW). Devuelve [{'text','start','to'}]."""
    if not shutil.which('whisper-cli'): raise SystemExit('Falta whisper-cli (whisper.cpp). Windows: scoop install whisper-cpp · Mac: brew install whisper-cpp')
    js = salida_sin_ext + '.json'
    if not (os.path.exists(js) and os.path.getmtime(js) >= os.path.getmtime(wav)):
        # -nfa es OBLIGATORIO: con flash-attention el DTW se apaga sin avisar y los tiempos quedan corridos
        ruta = buscar_modelo(modelo); usado = os.path.basename(ruta)[5:-4]          # ggml-<nombre>.bin -> el DTW debe corresponder al modelo real
        r = subprocess.run(['whisper-cli', '-m', ruta, '-l', idioma, '-mc', '0', '-nfa', '-dtw', DTW.get(usado, DTW.get(modelo, modelo)),
                            '-sow', '-ml', '1', '-ojf', '-f', wav, '-of', salida_sin_ext], capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode or not os.path.exists(js): raise SystemExit('whisper falló:\n' + (r.stderr or '')[-1200:])
    d = json.load(open(js, encoding='utf-8')); Wd = []
    for s in d['transcription']:
        txt = s['text'].strip()
        if not txt or txt.startswith('[') or txt.startswith('('): continue
        toks = [t for t in s.get('tokens', []) if not t['text'].startswith('[_') and t.get('t_dtw', -1) >= 0]
        st = (toks[0]['t_dtw'] / 100.0) if toks else s['offsets']['from'] / 1000.0
        Wd.append({'text': txt, 'start': st, 'to': s['offsets']['to'] / 1000.0})
    for i, w in enumerate(Wd):
        nxt = Wd[i + 1]['start'] if i + 1 < len(Wd) else w['to']
        w['end'] = round(max(w['start'] + 0.06, min(nxt - 0.01, w['start'] + 0.9)), 3); w['start'] = round(w['start'], 3)
    return Wd

def energia(wav):
    wf = wave.open(wav, 'rb'); sr = wf.getframerate()
    a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
    hop = int(sr * 0.01)
    rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2) + 1e-12) for i in range(0, len(a) - hop, hop)])
    return 20 * np.log10(rms), len(a) / sr

def seguir_cara(video, out, step=0.25):
    """cara del presentador cada `step` s -> {'track': [{'t','x','y','w','h','chin','ok'}]} en píxeles del video."""
    import cv2
    cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS) or 30
    n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); Wv = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); Hv = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    base = getattr(getattr(cv2, 'data', None), 'haarcascades', '') or ''
    xml = os.path.join(base, 'haarcascade_frontalface_default.xml')
    if not os.path.exists(xml): raise SystemExit('Tu OpenCV no trae los detectores de cara. Corre scripts/instalar.py (instala opencv-contrib 4.x).')
    front = cv2.CascadeClassifier(xml); prof = cv2.CascadeClassifier(os.path.join(base, 'haarcascade_profileface.xml'))
    SC = 0.5; res = []; t = 0.0; ms = (int(90 * SC), int(90 * SC))
    while t < n / fps:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(round(t * fps))); ok, fr = cap.read()
        if not ok: break
        g = cv2.equalizeHist(cv2.cvtColor(cv2.resize(fr, None, fx=SC, fy=SC), cv2.COLOR_BGR2GRAY))
        faces = list(front.detectMultiScale(g, 1.1, 5, minSize=ms))
        if not faces:
            faces = list(prof.detectMultiScale(g, 1.1, 4, minSize=ms))
            faces += [(g.shape[1] - x - w, y, w, h) for x, y, w, h in prof.detectMultiScale(cv2.flip(g, 1), 1.1, 4, minSize=ms)]
        if faces:
            faces.sort(key=lambda q: -q[2] * q[3])                       # la cara más grande = el presentador
            x, y, w, h = [int(v / SC) for v in faces[0]]
            res.append({'t': round(t, 2), 'x': x, 'y': y, 'w': w, 'h': h, 'chin': int(y + h * 1.18), 'ok': 1})
        else:
            res.append({'t': round(t, 2), 'ok': 0})
        t += step
    okk = [r for r in res if r['ok']]
    if not okk: raise SystemExit('No detecté ninguna cara en el video. Esta skill necesita a una persona hablando a cámara.')
    for r in res:
        if not r['ok']:
            near = min(okk, key=lambda o: abs(o['t'] - r['t'])); r.update({k: near[k] for k in ('x', 'y', 'w', 'h', 'chin')})
    json.dump({'W': Wv, 'H': Hv, 'step': step, 'track': res}, open(out, 'w'), indent=0)
    ch = sorted(r['chin'] for r in okk)
    return len(res), len(okk), ch[len(ch) // 2], ch[int(len(ch) * 0.9)]


def main():
    if len(sys.argv) < 3 or sys.argv[1].startswith('-'):
        raise SystemExit(__doc__)
    video, P = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    idioma = arg('--idioma', 'es'); modelo = arg('--modelo', 'large-v3')
    WK = os.path.join(P, '_work')
    for d in (WK, os.path.join(P, 'assets'), os.path.join(P, 'renders')): os.makedirs(d, exist_ok=True)
    for tool in ('ffmpeg', 'ffprobe'):
        if not shutil.which(tool): raise SystemExit(f'Falta {tool}. Instálalo (Windows: scoop install ffmpeg · Mac: brew install ffmpeg) y vuelve a correr.')
    SRC = os.path.join(P, 'source.mp4')
    if os.path.abspath(video) != SRC and not (os.path.exists(SRC) and os.path.getsize(SRC) == os.path.getsize(video)):
        shutil.copy(video, SRC)
    open(os.path.join(WK, 'skill.txt'), 'w', encoding='utf-8').write(SKILL.replace('\\', '/'))

    # ---------- 0) cómo viene el video ----------
    pr = json.loads(run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                         'stream=width,height,r_frame_rate,color_transfer:stream_side_data=rotation', '-of', 'json', SRC]).stdout)['streams'][0]
    w0, h0 = pr['width'], pr['height']
    rot = abs(int(next((sd.get('rotation', 0) for sd in pr.get('side_data_list', []) if 'rotation' in sd), 0)))
    if rot in (90, 270): w0, h0 = h0, w0
    hdr = pr.get('color_transfer') in ('arib-std-b67', 'smpte2084')
    if w0 > h0: raise SystemExit(f'El video es horizontal ({w0}x{h0}). Esta skill edita videos VERTICALES (9:16) de una persona hablando a cámara.')
    vf = []
    if hdr:   # los iPhone graban en HDR: Chrome no lo puede componer -> se pasa a SDR conservando el color (mobius)
        vf.append('zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=mobius:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p')
    if (w0, h0) != (1080, 1920): vf.append('scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920')
    print(f'video: {w0}x{h0}{" · HDR -> SDR" if hdr else ""}{" · se ajusta a 1080x1920" if (w0, h0) != (1080, 1920) else ""}')

    # ---------- 1) audio + palabras del crudo ----------
    a16 = os.path.join(WK, 'a16.wav')
    if not (os.path.exists(a16) and os.path.getmtime(a16) >= os.path.getmtime(SRC)):
        run(['ffmpeg', '-y', '-v', 'error', '-i', SRC, '-vn', '-ac', '1', '-ar', '16000', a16])
    print('transcribiendo el crudo (1/2)…', flush=True)
    Wd = whisper_palabras(a16, os.path.join(WK, 'wdtw'), modelo, idioma)
    if len(Wd) < 5: raise SystemExit('Casi no hay voz en el video: no hay nada que animar.')

    # ---------- 2) plan de cortes ----------
    db, DUR = energia(a16)
    lvl = np.percentile(db, 90); TH = lvl - 26; sil = db < TH
    runs = []; i = 0
    while i < len(sil):
        if sil[i]:
            j = i
            while j < len(sil) and sil[j]: j += 1
            runs.append((i * 0.01, j * 0.01)); i = j
        else: i += 1
    voiced = [k for k in range(len(sil)) if not sil[k]]
    first_voice, last_voice = voiced[0] * 0.01, (voiced[-1] + 1) * 0.01
    remove = []
    if first_voice - PRE > 0.05: remove.append((0.0, max(0.0, first_voice - PRE)))
    if '--sin-silencios' not in sys.argv:
        for s0, s1 in runs:
            if s0 <= first_voice or s1 >= last_voice: continue
            if s1 - s0 >= MIN_SIL:
                a0, a1 = s0 + KEEP, s1 - KEEP
                if any(a0 + 0.03 < w['start'] < a1 - 0.03 for w in Wd): continue    # whisper ve una palabra ahí: no cortar
                remove.append((a0, a1))
    if DUR - (last_voice + POST) > 0.05: remove.append((last_voice + POST, DUR))
    extra = os.path.join(WK, 'cortes.json')
    if os.path.exists(extra): remove += [tuple(x) for x in json.load(open(extra))]
    remove.sort(); merged = []
    for r in remove:
        if merged and r[0] <= merged[-1][1]: merged[-1] = (merged[-1][0], max(merged[-1][1], r[1]))
        else: merged.append(r)
    snap = lambda t: round(t * FPS) / FPS
    keep = []; cur = 0.0
    for r0, r1 in merged:
        if r0 > cur: keep.append((snap(cur), snap(r0)))
        cur = r1
    if cur < DUR: keep.append((snap(cur), snap(DUR)))
    keep = [(x, y) for x, y in keep if y - x >= 2 / FPS]
    newdur = sum(y - x for x, y in keep)
    print(f'duración {DUR:.2f}s -> {newdur:.2f}s | {len(keep)} tramos | {len(merged)} cortes' + (' (incluye _work/cortes.json)' if os.path.exists(extra) else ''))

    # ---------- 3) cortar a cuadro exacto ----------
    fc = []; ins = ''; pre = (','.join(vf) + ',') if vf else ''
    for k, (s, t) in enumerate(keep):
        d_ = t - s
        fc.append(f'[0:v]trim=start={s:.4f}:end={t:.4f},setpts=PTS-STARTPTS[v{k}]')
        fc.append(f'[0:a]atrim=start={s:.4f}:end={t:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,afade=t=out:st={max(0, d_ - 0.03):.4f}:d=0.03[a{k}]')
        ins += f'[v{k}][a{k}]'
    fc.append(f'{ins}concat=n={len(keep)}:v=1:a=1[vc][ao]')
    fc.append(f'[vc]{pre}fps={FPS},format=yuv420p[vo]')
    script = os.path.join(WK, 'fc_cut.txt'); open(script, 'w').write(';\n'.join(fc))
    print('cortando…', flush=True)
    mov = os.path.join(WK, 'cut.mov')
    fin = ['-map', '[vo]', '-map', '[ao]', '-c:v', 'libx264', '-crf', '15', '-preset', 'medium', '-pix_fmt', 'yuv420p',
           '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-c:a', 'pcm_s16le', mov]
    r = subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', SRC, '-/filter_complex', script, *fin], capture_output=True, text=True)
    if r.returncode: run(['ffmpeg', '-y', '-v', 'error', '-i', SRC, '-filter_complex_script', script, *fin])        # ffmpeg anterior a la 7
    run(['ffmpeg', '-y', '-v', 'error', '-i', mov, '-an', '-c:v', 'copy', '-movflags', '+faststart', os.path.join(P, 'cut.mp4')])
    run(['ffmpeg', '-y', '-v', 'error', '-i', mov, '-vn', '-ac', '1', '-ar', '48000', os.path.join(WK, 'voice_raw.wav')])
    c16 = os.path.join(WK, 'cut16.wav'); run(['ffmpeg', '-y', '-v', 'error', '-i', mov, '-vn', '-ac', '1', '-ar', '16000', c16])
    os.remove(mov)
    cm = os.path.join(P, 'cutmap.json'); viejo = None
    if os.path.exists(cm):
        try: viejo = [[round(v, 3) for v in k] for k in json.load(open(cm))['keep']]
        except Exception: viejo = None
    json.dump({'keep': keep, 'dur': round(newdur, 3)}, open(cm, 'w'), indent=0)

    # ---------- 4) palabras del video YA cortado (tiempos exactos) ----------
    print('transcribiendo el video cortado (2/2)…', flush=True)
    for old in (os.path.join(WK, 'wcut.json'),):
        if os.path.exists(old): os.remove(old)
    Wc = whisper_palabras(c16, os.path.join(WK, 'wcut'), modelo, idioma)
    NW = [{'text': w['text'], 'start': w['start'], 'end': w['end']} for w in Wc]
    json.dump(NW, open(os.path.join(P, 'words.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)

    # ---------- 5) cara ----------
    print('siguiendo la cara…', flush=True)
    n, okn, chin_med, chin_p90 = seguir_cara(os.path.join(P, 'cut.mp4'), os.path.join(P, 'face.json'))

    # ---------- resumen ----------
    pausas = run(['ffmpeg', '-hide_banner', '-nostats', '-i', c16, '-af', 'silencedetect=noise=-40dB:d=0.55', '-f', 'null', '-']).stderr.count('silence_end')
    print(f'\nLISTO  {P}')
    print(f'  cut.mp4 {newdur:.2f}s · words.json {len(NW)} palabras · cara detectada en {okn}/{n} muestras · barbilla y≈{chin_med} (p90 {chin_p90})')
    print(f'  pausas largas que quedaron: {pausas}')
    if chin_p90 > 1180: print('  (aviso) la cara ocupa mucho cuadro (barbilla muy abajo): queda poco espacio entre la barbilla y los subtítulos para las tarjetas.')
    print('\nGUION con tiempos (segundo · palabras):')
    for i in range(0, len(NW), 9):
        print(f"  {NW[i]['start']:6.2f}  " + ' '.join(x['text'] for x in NW[i:i + 9]))
    print('\nSiguiente: scripts/frases.py (¿equivocaciones?) -> elegir estilo y copiar su plantilla como <proyecto>/build.py')


if __name__ == '__main__':
    main()
