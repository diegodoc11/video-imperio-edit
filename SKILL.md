---
name: video-imperio-edit
description: >-
  Edita videos VERTICALES (9:16) de una persona hablando a cámara y los deja listos para Reels, TikTok o anuncios:
  corta silencios y equivocaciones con precisión, subtítulos (una palabra, karaoke resaltado o pequeños), gancho en
  pantalla desde el segundo 0, tarjetas, listas, logos, pruebas reales y CTA "Comenta X" que aparecen JUSTO cuando se
  dice cada palabra y NUNCA tapan la cara, zoom en los cortes, música que baja sola cuando se habla y efectos
  (HyperFrames + GSAP). Tres estilos probados: "tablero", "fucsia" y "stickers". Úsala cuando pidan "edita este
  video", "edítame este reel", "ponle subtítulos y apoyo visual", "hazlo más dinámico", "edítalo como este otro
  reel", o invoquen /video-imperio-edit. NO es para recortar al presentador dentro de un diseño animado (eso es
  reel-motion) NI para videos sin presentador hechos desde un guion (eso es anuncios-animados).
---

# video-imperio-edit — edición de reels con IA (el video real, a pantalla completa)

**Qué entrega:** un MP4 vertical 1080×1920 a 60 cuadros con el video original a pantalla completa, sin pausas ni
equivocaciones, y encima: gancho, subtítulos, tarjetas/listas/logos/pruebas sincronizadas palabra por palabra,
CTA, zooms, música y efectos. Hecha por Diego Osorio (@soydiegoosorio) con lo que funcionó en sus propios reels.

| Skill | El presentador | Úsala cuando |
|---|---|---|
| **video-imperio-edit** (esta) | Grabado, **a pantalla completa** con su fondo real | "edítame este video": cortes, subtítulos, apoyo visual, CTA |
| reel-motion | Grabado y **recortado** dentro de un diseño animado | "anímalo", "motion graphics", "recortado sobre color" |
| anuncios-animados | **No hay** presentador | parten de un guion: voz IA + ilustraciones |

**Entrada:** un video vertical (9:16) de UNA persona hablando a cámara (celular sirve; iPhone en HDR también).
Si es horizontal o no hay cara, esta skill no aplica: dilo y propón otra.

Rutas: `SKILL` = la carpeta de esta skill. `PY` = el Python de la skill. `P` = la carpeta del proyecto del video.

---

## 0. Instalación (una vez por computador)

```bash
python "SKILL/scripts/instalar.py"          # --verificar = solo revisa
```

Crea `SKILL/.venv`, instala numpy/pillow/opencv, revisa `ffmpeg`, `npx` (Node 20+), `whisper-cli` y `whisper-server`
(whisper.cpp), deja listo HyperFrames con su navegador y descarga el modelo de transcripción (~3 GB). Si dice
`[FALTA]`, instálalo con el comando que imprime y vuelve a correrlo hasta "Listo para usar".
Windows sin Scoop: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned; irm get.scoop.sh | iex` y luego
`scoop install git python nodejs-lts ffmpeg whisper-cpp`. Mac: `brew install git python node ffmpeg whisper-cpp`.

Desde ahí usa SIEMPRE: Windows `PY = "SKILL/.venv/Scripts/python.exe" -X utf8` · Mac/Linux `PY = "SKILL/.venv/bin/python"`.
Rutas con espacios SIEMPRE entre comillas.

## 1. Qué preguntar (UNA sola ronda, solo lo que falte)

1. **El video** (ruta). Varios videos = un proyecto por video.
2. **El CTA**: casi siempre el video ya lo dice ("comenta CLASE"); pregunta solo si no hay.
3. **El estilo** (`tablero`, `fucsia` o `stickers`; ver §4). Si el usuario no sabe, propón uno según el tema y sigue.
   Si pasa un reel de referencia "para que lo edites así": estúdialo (§6) y elige el estilo más parecido.
4. **Música**: la skill NO trae música (derechos). Usa la que indique o la primera de `SKILL/recursos/musica/`.
5. **Material real** solo si el guion lo menciona ("mis resultados", "mi web"): fotos, capturas o videos suyos.
6. ¿El video trae **marca de agua** en una esquina de abajo (BIGVU, etc.)? Míralo tú en un cuadro; no preguntes si se ve.

No preguntes nada técnico: tiempos, posiciones, tamaños y fuentes los decides tú.

## 2. Flujo

### 2.1 Preparar (2-5 min por minuto de video; córrelo en segundo plano)
```bash
PY "SKILL/scripts/preparar.py" "<video>" "<P>"
```
Copia el crudo (`source.mp4`), transcribe con tiempos por palabra (whisper DTW), quita silencios largos, corta a
cuadro exacto (`cut.mp4` 1080×1920 30 fps, SDR; si viene HDR o rotado lo corrige), transcribe OTRA VEZ el video ya
cortado (`words.json`, tiempos exactos), sigue la cara (`face.json`) e imprime el GUION con segundos. Léelo entero.

### 2.2 Equivocaciones (OBLIGATORIO — el usuario lo nota siempre)
Cuando alguien se equivoca y repite ("Y ciertos… ¿Y su…? Y si esto te suena básico"), whisper transcribe la frase
UNA vez y el guion se ve limpio aunque el video tenga el error.
```bash
PY "SKILL/scripts/frases.py" "<P>"
```
Transcribe CADA tramo entre silencios por separado: ahí aparecen los arranques en falso y las frases repetidas.
Escribe los tramos MALOS (segundos del CRUDO; cortar en silencio, dejando ~0.2 s de pausa) en
`<P>/_work/cortes.json` → `[[31.24, 34.74], [55.80, 59.08]]` y vuelve a correr `preparar.py`. Para afinar un borde
mira la energía: `PY -c "import wave,numpy as n;..."` o pide el perfil cada 0.04 s alrededor del corte.
Después de cortar, relee el GUION nuevo: se tiene que leer de corrido y no puede faltar ninguna palabra.

### 2.3 Armar el build
```bash
cp "SKILL/plantilla/build.py" "<P>/build.py"
```
Edita SOLO la parte "TU VIDEO" de `<P>/build.py`:
- `ESTILO`, `COLOR`, `QUITAR_MARCA`, `MUSICA`, `CORRECCIONES` (nombres que whisper escribe mal: cloud→Claude…).
- `GANCHO`: la promesa del video en 2-3 renglones cortos; sale desde el segundo 0. `GANCHO_HASTA`: frase/segundo.
- `ESCENAS`: una por idea, en orden (tipos en §5). Las frases se escriben como quedaron en `words.json`.
- `ZOOMS` (opcional) y `CTA`.
Para efectos avanzados (destello + zoom de testimonios, ramas y círculos dibujados, diagramas con flechas, maqueta de
celular, máquina de escribir…) copia la pieza de `SKILL/plantilla/recetas/` (son los build.py reales de 3 reels).

### 2.4 Construir y REVISAR antes de mostrar
```bash
cd "<P>"; PY build.py            # index.html + final_audio.wav   (--sin-audio = más rápido mientras ajustas)
npx hyperframes lint .           # 0 errores
npx hyperframes snapshot . --at 1,5,10,15,20 --no-end --timeout 40000 -o snaps     # y MIRA la hoja
```
Revisa en los cuadros: nada tapa la cara (ni con zoom), los textos caben, cada pieza entra cuando se dice, el
gancho se ve en el segundo 0, el CTA al final. Si un `K.find` dice "NO ENCONTRADO", la frase quedó escrita distinto
en `words.json`: búscala ahí y cópiala igual.

### 2.5 Vista previa (iterar aquí, NO con renders)
```bash
cd "<P>"; npx hyperframes preview --background      # imprime la URL de Studio (http://localhost:3xxx/...)
```
Dale la URL al usuario. Cada cambio: editar `build.py` → `PY build.py` → Studio se recarga solo.
(Studio a veces no reproduce la voz en vivo; el export sí la lleva.) Cuando termine: `npx hyperframes preview --stop`.

### 2.6 Exportar SOLO con el OK del usuario
```bash
cd "<P>"; npx hyperframes render . --fps 60 --quality high --crf 16 --sdr --output renders/final.mp4
```
(~8-12 min por minuto de video.) Verifica ANTES de decir "listo": `ffprobe` (1080×1920, 60 fps, duración), 6-10
cuadros sueltos del final (`PY "SKILL/scripts/hoja.py" renders/final.mp4 _work/rev.jpg`) y que el audio tenga voz
(`ffmpeg -i renders/final.mp4 -af volumedetect -f null -` → media ≈ -18 dB, pico ≤ -1.5 dB).
Para redes, una copia liviana: `ffmpeg -i renders/final.mp4 -c:v libx264 -b:v 5500k -c:a aac -b:a 192k renders/final-redes.mp4`.

## 3. Reglas de oro (aprendidas a la fuerza)

1. **NADA sobre la cara.** Todo `top` sale de `FACE.safe_top()` (barbilla + margen, contando el zoom). Solo material
   REAL a pantalla completa (un video o foto que reemplaza la toma) puede cubrirla.
2. **El gancho se ve en el segundo 0.** Si el gancho entra en el segundo 2, ya se fue la gente.
3. **Cada pieza entra cuando se dice su palabra**, y las listas se encienden UNA POR UNA (nunca todo de golpe).
4. **Cero equivocaciones**: §2.2 siempre, y verifica cada empalme.
5. **Marca de agua**: nunca taparla con una caja (se ve horrible): `QUITAR_MARCA = True` (mini zoom 1.075 anclado arriba).
6. **Apoyo visual de principio a fin**, también en la segunda mitad. Material real (sus resultados, su web, sus
   clips) primero; si no hay, tarjetas y listas.
7. **Texto grande y legible**; subtítulos abajo (y≈1600) y tarjetas entre la barbilla y los subtítulos.
8. **Música audible pero debajo de la voz** (el ducking la baja sola). Sin pista: voz + efectos, y avisa.
9. **Exporta solo con OK** y **verifica el export** (cuadros + audio). "Compila" no es "funciona".

## 4. Los 3 estilos

| Estilo | Gancho | Subtítulos | Apoyo | Ideal para |
|---|---|---|---|---|
| `tablero` | sticker blanco tipo Instagram | UNA palabra, MAYÚSCULAS | pizarra blanca con letra de marcador que "se escribe" | explicar un método, pasos, cifras |
| `fucsia` | escrito a mano, mayúsculas | 3-4 palabras, la que se dice resaltada en `COLOR` | tarjeta de logo + ficha "Acerca de" estilo GitHub | listas de herramientas, recomendaciones |
| `stickers` | palabra a mano + etiquetas de papel rasgado | 2-3 palabras, pequeños | etiquetas de marcador, X rojas, chat, terminal | historias, demostraciones, antes/después |

## 5. Tipos de escena (`ESCENAS` en build.py)

Todas llevan `'desde'` y `'hasta'` (frase o segundos). Campos extra:

| tipo | campos | qué hace |
|---|---|---|
| `lista` | `titulo`, `items: [(frase, texto), …]` | título + cada ítem aparece al decir su frase |
| `tarjeta` | `titulo`, `grande`, `sub` | cifra o palabra grande ("$500 – $2.000", "x2") |
| `logos` | `titulo`, `logos: [(frase, svg, nombre, color), …]` | fichas de apps (svg de `recursos/logos/`) |
| `logo` | `nombre`, `svg` o None, `oscuro`, `acerca`, `url`, `acerca_desde` | tarjeta de marca y luego su ficha "Acerca de" |
| `imagen` | `src`, `completa` (bool) | foto/captura enmarcada bajo la barbilla, o a pantalla completa |
| `video` | `src`, `etiqueta` | clip real a pantalla completa (pruebas, su web, b-roll) |
| `tachado` | `items: [(frase, texto), …]` | cajas que se tachan con X roja al decir la frase |
| `chat` | `texto`, `app` | burbuja de chat que se escribe sola |
| `terminal` | `comando`, `resultado`, `en` | comando que se teclea + resultado |

Logos: `recursos/logos/*.svg` (simple-icons). Si falta uno: `https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/<nombre>.svg`.
Fotos y clips del usuario: cópialos a `<P>/assets/` (clips de iPhone: pásalos a SDR 1080×1920 con ffmpeg antes).

## 6. "Edítalo como este reel" (modelar una referencia)

Estudia la referencia antes de editar: `PY "SKILL/scripts/hoja.py" ref.mp4 _work/ref.jpg` (un cuadro cada 0.25-1 s),
anota cómo es el gancho, cómo son los subtítulos (tamaño, palabras por línea, resaltado), dónde y cuándo entra cada
tarjeta, cortes/zooms, música y CTA. Elige el estilo más cercano y ajusta `COLOR`/textos; copia de las recetas lo
que falte. Mantén SIEMPRE las reglas de §3 aunque la referencia no las cumpla (p. ej. si tapa la cara).

## 7. Problemas comunes

- **iPhone (HDR) o video rotado**: `preparar.py` ya lo pasa a SDR y lo endereza.
- **Video horizontal**: no aplica (es para verticales).
- **"NO ENCONTRADO" en K.find**: la frase está escrita distinto en `words.json` (números, tildes, una "Y" pegada).
- **Lint "gsap_non_transform_motion"**: no animes `top`/`left`; usa `y`, `x`, `scale`, `opacity`.
- **El export no trae las tarjetas**: un error en el script del HTML; revisa la consola de la vista previa.
- **whisper escribe mal un nombre**: agrégalo a `CORRECCIONES`.
- **Muy lento**: transcribir y renderizar corren en el computador; con tarjeta gráfica va mucho más rápido.
