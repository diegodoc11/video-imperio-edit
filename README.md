# 🎬 video-imperio-edit — Skill de edición de video con IA (HyperFrames)

Skill para **Claude Code** que edita videos talking-head — **anuncios verticales 9:16** (Meta/TikTok) e **intros/videos de YouTube 16:9** — usando HyperFrames: **subtítulos karaoke**, **imágenes de IA (Nano Banana)**, **b-roll de Pexels/Pixabay**, zooms, tarjetas de stats, **música con ducking**, efectos de transición (whoosh/flash) y render final verificado.

Creado por **Diego Osorio** · Método Escala / comunidad **Imperio**.

---

## ✅ Requisitos
- **Node.js 20+** (trae `npx`).
- **FFmpeg** y **Google Chrome** (HyperFrames renderiza con Chrome).
- **whisper.cpp** para transcripción → `scoop install whisper-cpp` (Windows).
- **PowerShell** (los scripts de `tools/` son `.ps1`).
- HyperFrames se usa vía `npx hyperframes …` (sin instalación global).

## 📦 Instalar la skill
```bash
npx skills add diegodoc11/video-imperio-edit
```
(Manual: copia `SKILL.md` y la carpeta `templates/` a `~/.claude/skills/video-ad-editing/`)

## 🔑 API keys (variables de entorno)
Todas tienen plan gratuito. En Windows déjalas fijas con `setx` y reinicia la terminal:
| Servicio | Para qué | Conseguir | Variable |
|---|---|---|---|
| **Pexels** | b-roll en video | https://www.pexels.com/api/ | `setx PEXELS_API_KEY "tu_key"` |
| **Pixabay** | b-roll (variedad) | https://pixabay.com/api/docs/ | `setx PIXABAY_API_KEY "tu_key"` |
| **KIE AI** | imágenes Nano Banana | https://kie.ai | `setx KIE_API_KEY "tu_key"` |

## 🛠️ Scripts incluidos (`tools/`)
**Descargar b-roll** (Pexels primario, Pixabay de respaldo):
```powershell
.\tools\Get-Broll.ps1 -Query "money cash" -OutDir .\assets\broll -Count 2 -Orientation landscape
```
**Generar imágenes IA** (Nano Banana):
```powershell
.\tools\Get-NanoBanana.ps1 -PromptsJson .\prompts.example.json -OutDir .\assets\img -Model google/nano-banana -Size 16:9
```
> 💲 **Precios KIE (aprox.)**: `nano-banana` ~$0.02/img · `nano-banana-2` ~$0.04 · `nano-banana-pro` ~$0.12. **WAN es video**, no imágenes.
> ⚠️ Pide el texto de las imágenes **EN ESPAÑOL** (o sin texto) — los prompts en inglés escriben texto en inglés. Ver `prompts.example.json`.

## 🚀 Flujo de trabajo
1. **Analiza** la fuente: `ffprobe` + contact sheet (mapear dónde habla vs b-roll).
2. **Transcribe**: `npx hyperframes transcribe source.mp4 --model large-v3 --language es`.
3. **Arma** la composición e **itera en el preview en vivo** (no renders): `npx hyperframes preview <proj> --port 3010`.
4. `npx hyperframes lint` + `inspect` (arregla errores).
5. **Render final** + verifica frames y audio (voz + música).

## 🎞️ Reels grabados con iPhone (HDR) — nuevo
El iPhone graba en HDR, y si le cambias el color al video original se ve "dañado" al lado del crudo. La solución que ya se probó en 8 reels:
- HyperFrames produce **solo los gráficos** (tarjetas, listas, subtítulos, b-roll) sobre fondo **magenta**, y ffmpeg los pega encima del video original **sin tocarle el color**.
- Plantilla lista: **[`templates/build_overlay.py`](templates/build_overlay.py)**. Llenas 3 listas (b-roll, tarjetas y listas que se encienden palabra por palabra) y genera la composición.
- **Vista previa primero**: `python build_overlay.py preview` te deja revisar todo en vivo antes de exportar, que tarda varios minutos.
- Audio listo para reels: limpieza de voz y música baja que se aparta sola cuando hablas.
- Estilo que funciona en Instagram: tarjetas **entre el mentón y los subtítulos** (Instagram recorta arriba y abajo en la vista previa del feed), mucho b-roll desde el segundo 2 y CTA "Comenta PALABRA" al final.

Los comandos exactos (composición HDR, mezcla de audio, verificación) están en `SKILL.md` → sección *iPhone HDR reels*.

📖 Todo el detalle (técnicas, gotchas, motor de karaoke, etc.) está en **[`SKILL.md`](SKILL.md)**.

---
*Hecho con HyperFrames + Claude Code.*
