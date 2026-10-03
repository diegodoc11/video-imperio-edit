# -*- coding: utf-8 -*-
"""
video-imperio-edit · FRASES  — detector de equivocaciones y repeticiones.

    python frases.py <carpeta_proyecto>

Cuando alguien se equivoca y repite la frase, whisper la transcribe UNA sola vez (junta las repeticiones), así que la
transcripción normal se ve limpia aunque el video tenga el error. Este script parte el audio CRUDO por los silencios
reales y transcribe CADA frase por separado: ahí sí aparecen los arranques en falso ("Y ciertos… ¿Y su…? Y si esto…").

Qué hacer con el resultado: si ves una frase repetida o a medias, escribe el tramo MALO (inicio y fin en segundos del
crudo, cortando en el silencio y dejando ~0.2 s de pausa) en  <proyecto>/_work/cortes.json  ->  [[12.84, 15.31], ...]
y vuelve a correr preparar.py.
"""
import sys, os, json, wave, io, time, shutil, subprocess, urllib.request, uuid
try: sys.stdout.reconfigure(encoding='utf-8', errors='replace'); sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception: pass
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from preparar import buscar_modelo, arg

PUERTO = 8178

def servidor_arriba():
    try:
        urllib.request.urlopen(f'http://127.0.0.1:{PUERTO}/', timeout=2); return True
    except Exception:
        return False

def main():
    if len(sys.argv) < 2: raise SystemExit(__doc__)
    P = os.path.abspath(sys.argv[1]); WK = os.path.join(P, '_work')
    idioma = arg('--idioma', 'es'); modelo = arg('--modelo', 'large-v3')
    a16 = os.path.join(WK, 'a16.wav')
    if not os.path.exists(a16): raise SystemExit('Primero corre preparar.py (falta _work/a16.wav).')
    proc = None
    if not servidor_arriba():
        if not shutil.which('whisper-server'): raise SystemExit('Falta whisper-server (viene con whisper.cpp). Windows: scoop install whisper-cpp · Mac: brew install whisper-cpp')
        proc = subprocess.Popen(['whisper-server', '-m', buscar_modelo(modelo), '-l', idioma, '--port', str(PUERTO), '-nfa'],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(90):
            if servidor_arriba(): break
            time.sleep(1)
        else:
            proc.kill(); raise SystemExit('whisper-server no arrancó.')
    try:
        wf = wave.open(a16, 'rb'); sr = wf.getframerate()
        a = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
        x = a.astype(np.float32) / 32768.0; hop = int(sr * 0.01)
        db = 20 * np.log10(np.array([np.sqrt(np.mean(x[i:i + hop] ** 2) + 1e-12) for i in range(0, len(x) - hop, hop)]))
        voiced = db > (np.percentile(db, 90) - 24)
        segs = []; i = 0; n = len(voiced)                      # frases = tramos con voz separados por silencios >= 0.16 s
        while i < n:
            if voiced[i]:
                j = i
                while j < n:
                    if voiced[j]: j += 1; continue
                    k = j
                    while k < n and not voiced[k]: k += 1
                    if k - j >= 16 or k >= n: break
                    j = k
                segs.append((i * 0.01, j * 0.01)); i = j
            else: i += 1
        segs = [(s, e) for s, e in segs if e - s >= 0.08]
        print(f'{len(segs)} tramos entre silencios; transcribiendo uno por uno (~1 min por cada 30 s de video)…', flush=True)
        if len(segs) <= 3:
            print('  (aviso) este orador casi no hace pausas: dentro de un tramo largo NO se pueden ver repeticiones. '
                  'Lee el guion de preparar.py con calma buscando frases repetidas.', flush=True)

        def transcribir(s, e):
            pad = 0.12; i0 = max(0, int((s - pad) * sr)); i1 = min(len(a), int((e + pad) * sr))
            buf = io.BytesIO(); w = wave.open(buf, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(a[i0:i1].tobytes()); w.close()
            bnd = uuid.uuid4().hex
            body = (f'--{bnd}\r\nContent-Disposition: form-data; name="file"; filename="c.wav"\r\nContent-Type: audio/wav\r\n\r\n').encode() + buf.getvalue() + \
                   (f'\r\n--{bnd}\r\nContent-Disposition: form-data; name="response_format"\r\n\r\njson\r\n'
                    f'--{bnd}\r\nContent-Disposition: form-data; name="temperature"\r\n\r\n0\r\n--{bnd}--\r\n').encode()
            req = urllib.request.Request(f'http://127.0.0.1:{PUERTO}/inference', data=body, headers={'Content-Type': f'multipart/form-data; boundary={bnd}'})
            return ' '.join(json.loads(urllib.request.urlopen(req, timeout=180).read().decode('utf-8')).get('text', '').split())

        out = []
        print(' #   inicio-  fin   frase (cada renglón = lo que se dijo entre dos silencios)')
        for k, (s, e) in enumerate(segs):
            t = transcribir(s, e); out.append({'i': k, 's': round(s, 2), 'e': round(e, 2), 'text': t})
            print(f'{k:3d}  {s:6.2f}-{e:6.2f}  {t}', flush=True)
        json.dump(out, open(os.path.join(WK, 'frases.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print('\nBusca: la MISMA frase dicha dos veces o frases a medias. Si todo se lee de corrido, no hay nada que cortar.')
        print('Ojo: un tramo muy corto (<1 s) o un nombre en otro idioma puede salir mal transcrito al aislarlo; eso no es una equivocación.')
        print('Compara con el guion completo de preparar.py antes de cortar, y relee el guion después de cortar: no debe faltar ninguna palabra.')
    finally:
        if proc: proc.kill()


if __name__ == '__main__':
    main()
