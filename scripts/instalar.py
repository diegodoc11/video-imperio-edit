# -*- coding: utf-8 -*-
"""
video-imperio-edit · INSTALAR  (se corre UNA sola vez; se puede repetir sin problema)

    python instalar.py [--modelo-whisper large-v3 | medium] [--sin-whisper] [--verificar]

  --verificar : solo revisa (no crea nada ni descarga nada) e imprime qué hay y qué falta.

  1. crea un entorno de Python propio dentro de la skill (.venv) con lo necesario (numpy, pillow, opencv)
  2. revisa que estén: ffmpeg, Node.js (npx), whisper.cpp (whisper-cli / whisper-server), deja listo HyperFrames
     y descarga el modelo de whisper si falta (3 GB)
Al final imprime la ruta del Python que debes usar para los demás scripts.
"""
import sys, os, shutil, subprocess, urllib.request, platform

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIN = platform.system() == 'Windows'; MAC = platform.system() == 'Darwin'
VENV = os.path.join(SKILL, '.venv')
PY = os.path.join(VENV, 'Scripts', 'python.exe') if WIN else os.path.join(VENV, 'bin', 'python')
WH_URL = 'https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-{m}.bin'
como = lambda win, mac, lin: win if WIN else (mac if MAC else lin)
ok, falta = [], []

def bajar(url, destino, nombre):
    os.makedirs(os.path.dirname(destino), exist_ok=True); tmp = destino + '.parte'
    print(f'  descargando {nombre}…', flush=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'video-imperio-edit'})) as r, open(tmp, 'wb') as f:
        total = int(r.headers.get('Content-Length') or 0); leido = 0; marca = 0
        while True:
            b = r.read(1 << 20)
            if not b: break
            f.write(b); leido += len(b)
            if total and leido * 10 // total > marca: marca = leido * 10 // total; print(f'    {marca * 10}%', flush=True)
    os.replace(tmp, destino)

def main():
    VERIF = '--verificar' in sys.argv
    print('video-imperio-edit · ' + ('verificación' if VERIF else 'instalación') + ' en', SKILL)
    if sys.version_info < (3, 10): raise SystemExit('Necesitas Python 3.10 o más nuevo.')

    # 1) entorno de Python
    if VERIF:
        if os.path.exists(PY):
            r = subprocess.run([PY, '-c', 'import numpy, cv2, PIL'], capture_output=True)
            (ok if r.returncode == 0 else falta).append('librerías de Python' + ('' if r.returncode == 0 else ' (faltan: corre instalar.py sin --verificar)'))
        else: falta.append('entorno .venv (corre instalar.py sin --verificar)')
    else:
        if not os.path.exists(PY):
            print('creando entorno de Python (.venv)…', flush=True)
            subprocess.run([sys.executable, '-m', 'venv', VENV], check=True)
        print('instalando librerías (puede tardar unos minutos la primera vez)…', flush=True)
        r = subprocess.run([PY, '-m', 'pip', 'install', '--quiet', '--disable-pip-version-check', '-r', os.path.join(SKILL, 'requirements.txt')])
        (ok if r.returncode == 0 else falta).append('librerías de Python' + ('' if r.returncode == 0 else ' (pip falló: revisa tu conexión y vuelve a correr)'))

    # 3) programas
    for exe, nombre, ayuda in (('ffmpeg', 'ffmpeg', como('scoop install ffmpeg', 'brew install ffmpeg', 'sudo apt install ffmpeg')),
                               ('npx', 'Node.js 20+ (npx)', como('scoop install nodejs-lts', 'brew install node', 'https://nodejs.org')),
                               ('whisper-cli', 'whisper.cpp (whisper-cli)', como('scoop install whisper-cpp', 'brew install whisper-cpp', 'https://github.com/ggml-org/whisper.cpp')),
                               ('whisper-server', 'whisper.cpp (whisper-server)', como('scoop install whisper-cpp', 'brew install whisper-cpp', 'https://github.com/ggml-org/whisper.cpp'))):
        if shutil.which(exe) or (WIN and shutil.which(exe + '.cmd')): ok.append(nombre)
        else: falta.append(f'{nombre}  ->  instálalo con:  {ayuda}')

    # 3b) HyperFrames (el que renderiza): se baja solo con npx la primera vez, junto con su navegador
    if shutil.which('npx') or (WIN and shutil.which('npx.cmd')):
        print('preparando HyperFrames (la primera vez descarga el paquete y su navegador)…', flush=True)
        try:
            v = subprocess.run('npx --yes hyperframes --version', shell=True, capture_output=True, text=True, timeout=600)
            nav = v if VERIF else subprocess.run('npx --yes hyperframes browser ensure', shell=True, capture_output=True, text=True, timeout=900)
            if v.returncode == 0 and nav.returncode == 0: ok.append('HyperFrames ' + (v.stdout.strip().splitlines() or ['?'])[-1])
            else: falta.append('HyperFrames no quedó listo. Corre a mano:  npx --yes hyperframes browser ensure')
        except Exception as e:
            falta.append(f'HyperFrames ({e}). Corre a mano:  npx --yes hyperframes browser ensure')

    # 4) modelo de whisper
    if '--sin-whisper' not in sys.argv:
        m = sys.argv[sys.argv.index('--modelo-whisper') + 1] if '--modelo-whisper' in sys.argv else 'large-v3'
        cands = [os.path.join(SKILL, 'modelos', f'ggml-{m}.bin'), os.path.expanduser(f'~/.cache/hyperframes/whisper/models/ggml-{m}.bin'),
                 os.path.expanduser(f'~/.claude/skills/reel-motion/modelos/ggml-{m}.bin'), os.path.expanduser(f'~/.cache/whisper/ggml-{m}.bin')]
        if not any(os.path.exists(c) for c in cands) and not VERIF:
            try: bajar(WH_URL.format(m=m), cands[0], f'modelo de whisper {m} (~{"3 GB" if "large" in m else "1.5 GB"})')
            except Exception as e: falta.append(f'modelo de whisper ({e}). Descárgalo de {WH_URL.format(m=m)} a {cands[0]}')
        hay = [c for c in cands if os.path.exists(c)]
        if hay: ok.append(f'modelo de whisper {m}  ' + hay[0])
        elif VERIF: falta.append(f'modelo de whisper {m} (corre instalar.py sin --verificar para descargarlo)')

    print('\n=========== RESULTADO ===========')
    for x in ok: print('  [ok]    ', x)
    for x in falta: print('  [FALTA] ', x)
    if falta and WIN:
        print('\nWindows: si no tienes Scoop, instálalo una vez en PowerShell:\n  Set-ExecutionPolicy -Scope CurrentUser RemoteSigned\n  irm get.scoop.sh | iex\n'
              'y luego:  scoop install git python nodejs-lts ffmpeg whisper-cpp   (cierra y abre la terminal al terminar)')
    print('\nPython para los scripts de la skill:\n  ' + PY)
    print('\nListo para usar.' if not falta else '\nArregla lo que dice FALTA y vuelve a correr este instalador.')
    sys.exit(1 if falta else 0)


if __name__ == '__main__':
    main()
