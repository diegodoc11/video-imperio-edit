---
name: video-ad-editing
description: >-
  Edit and enhance talking-head / AI-avatar videos with HyperFrames — both vertical 9:16
  ads (Meta/TikTok) and 16:9 YouTube intros/long-form. Use whenever the user asks to "edit
  this video", add support material / b-roll, "make it more dynamic", add zooms, captions
  (incl. karaoke word-highlight), AI support images, badges, music, sound effects, or export.
  Includes the iPhone HDR reel pipeline (magenta overlay keyed over the untouched HLG master).
  Encodes a preview-first workflow, the enhancement playbook, AI image generation (Kie Nano
  Banana) + royalty-free b-roll (Pexels/Pixabay), a client resource library, and the technical
  gotchas learned shipping these.
---

# Video Ad & YouTube Editing (HyperFrames)

Companion to the `hyperframes` / `hyperframes-cli` / `hyperframes-media` skills. Captures HOW to edit
these videos. Always still follow the core HyperFrames rules (paused GSAP timeline on
`window.__timelines`, `data-*` clip attributes, determinism — no `Date.now`/`Math.random`/network).

## Formats
- **Vertical 9:16 reels/ads** (Meta/TikTok) — `hyperframes init … --resolution portrait`. These usually
  arrive WITH baked captions + baked b-roll → keep them, add overlays around them.
- **16:9 YouTube** (intros / long-form) — `--resolution landscape`. Usually a clean talking head with NO
  baked subtitles → add your own **karaoke captions** (below).

## Workflow (always)
1. **Analyze the source first**: `ffprobe` (duration/res/fps/audio) + a **contact sheet**
   (`ffmpeg -vf "fps=1/3,scale=170:302,tile=5x4"`) to map presenter-vs-b-roll segments. Don't guess.
2. **Transcribe for content/timing**: `npx hyperframes transcribe source.mp4 --model large-v3 --language es`
   (`medium` also works; `large-v3` gets names/brands right more often).
   NEVER a `.en` model for Spanish (it translates). `small` silently TRUNCATES long clips.
   Set the composition `data-duration` from the SOURCE (ffprobe), NOT the transcript end.
   **Fix Whisper mishears** before building (names, brand terms — e.g. "Osorio"→"Soria", "Claude"→"cloud").
3. **Iterate in the LIVE PREVIEW, not renders** (saves time + tokens): run
   `npx hyperframes preview <project> --port <NNNN>` in the background; give the user `http://localhost:<port>`.
   Edit HTML → Studio hot-reloads. Only `render` the FINAL once approved. (Preview may NOT play the voice
   track live — that's a Studio autoplay limitation; the render muxes it. Verify audio after render.)
4. `lint` + `inspect` after every change; fix errors, review warnings.

## Project organization
Under `Editor Videos/`, mirror the brand hierarchy:
- Ads: `<Brand>/Anuncios/<Procedimiento>/<Audiencia>/anuncio-NN/` (e.g. `Francia-Estetica/Anuncios/Criolipolisis/extranjeros/anuncio-01`).
- YouTube: `<Brand>/YouTube/<video-slug>/` (e.g. `Metodo-Escala/YouTube/redactor-vsl-intro`).
Launcher: `Abrir-Editor.bat` (Desktop shortcut "Editor de Videos") lists projects and opens the Studio.
`hyperframes init "<nested/path>" --video <src> --resolution portrait|landscape --skip-transcribe --non-interactive --skip-skills`
scaffolds the full project AND transcodes **HEVC→H.264** (Chrome can't render HEVC). It keeps the original
filename → rename the copied video to `source.mp4`.

## Enhancement playbook
Keep any **baked captions + existing b-roll**. Put overlays OUTSIDE the caption band. Add:
- **Full-screen cutaways** — Nano Banana images AND/OR royalty-free **video b-roll** at conceptual moments
  tied to the transcript. Pattern: inner `<img|video class="clip" id="…" data-start data-duration
  [data-media-start] data-track-index="3">` inside a `.broll-wrap` (mark `data-layout-allow-overflow`).
  Wrapper does the motion: "zoom-blur" punch-in `scale 1.18→1.0` (`power3.out`) → slow ken-burns to ~1.07
  → fade out. Place cutaways in talk GAPS, never over a zoom. `data-media-start` must be INSIDE the clip
  duration (past the end freezes the last frame). **Every `<video>` needs an `id`** or the renderer freezes it.
- **Cutout HERO scene — subject over a replaced background ("recortes estilo máscara", Diego LOVES this for YT intros).**
  `npx hyperframes remove-background source.mp4 -o assets/cutout.webm` → composite the cutout OVER a dynamic backdrop
  (money/AI b-roll + a darkened version, `filter:brightness(0.42)`) on its own track, subject on top. Time-sync the
  cutout with `data-media-start = scene start` so the lips still match the audio. Keep the original `source.mp4` as the
  base for the rest; show the cutout scene only on hero beats (the hook). **VERIFY cutout quality first** by compositing
  one frame over magenta: `ffmpeg -f lavfi -i color=c=magenta:s=WxH -c:v libvpx-vp9 -ss N -i cutout.webm -filter_complex "[1:v]format=yuva420p[fg];[0:v][fg]overlay" -frames:v 1 chk.png`. u2net is clean on a seated talking head (hair/glasses/mic edges held up well).
- **Masked insets — match the frame aspect to the asset's TRUE orientation ("analiza las fotos").** ffprobe EVERY asset's
  real `width,height` AND **rotation** before sizing its frame. A vertical clip in a 16:9 frame (object-fit cover) crops
  it ugly — Diego: "no quedan bien, hazlos más verticales, 4:5". So: vertical clips/portrait photos → **4:5** rounded
  frame; landscape clips, IG/testimonial screenshots → **16:9** frame; cover for photos/video, contain when on-image text
  must stay readable. Frame = gold border + radius + shadow; pop in (`back.out`) + slow ken-burns, fade out.
- **⚠️ NEVER PUT ANYTHING ON THE FACE — hard rule (Diego repeated this 3+ times).** ANY added element —
  text card, chip, badge, inset image, AI background, diagram, explanation — must go in a FACE-FREE zone, NEVER
  over the presenter's face. Diego: "me los estás colocando encima de la cara… no me los vuelvas a poner encima de la cara",
  "utiliza el espacio entre el mentón y la parte de abajo de los subtítulos". The zones, in priority order:
  1. **The "chin band"** — the space BETWEEN the chin and the top of the subtitles (her chest/torso; a dark top is an
     ideal backdrop). This is Diego's #1 preferred spot for text cards/chips/CTA. Measure where the chin sits per video.
  2. **Top band** — only the area clearly ABOVE the head (not the forehead). Many seated/standing shots leave little room
     here, so the chin band usually wins.
  3. **Over a full-screen visual** — when a before/after or b-roll cutaway covers the whole frame (no presenter face),
     text reveals (brand, product, value) can sit on top. Time the text to the visual's window so it never lingers onto her face.
  Before placing ANY element, locate the face bounding box (grab a frame) and confirm the element sits OUTSIDE it.
  If the closing/hero "needs" the center, either put it in the chin band, show it over a full-screen visual, or — last
  resort — dim the whole frame with a scrim AND keep the text below the face. Keep insets on the SIDES / bottom corners,
  max ~2 on screen at once, STAGGERED. When unsure whether something covers the face: assume it does, and move it down.
  - **MANDATORY procedure (do this BEFORE writing any overlay, every video — Diego has rejected face-coverage 4+ times):**
    1. Grab a clean frame with `drawgrid=w=iw/10:h=ih/10` and read the **chin Y** and the face bounding box (in px).
    2. For a vertical 1080×1920 talking-head, the chin sits ~y760–820. Set the **graphics/box/screenshot container `top` to ≥ chinY+40** (≈ `top:840px`) and keep its bottom above the caption band. Captions live at `bottom:140–150px`. So the **only safe band is roughly y840–1450 (over the torso)** — put EVERY card/chip/diagram/screenshot/AI-image/green-screen-label there. The hook/title goes there too (Diego: "de entrada ya me tapas la cara"). NEVER `top:` in the 150–800 range on a vertical talking head — that is the face.
    3. **Strong-zoom caveat + the WINNING layout (Diego, anuncio-06/07):** when the camera punches in (scale ~1.4–1.5 on every ~4s of an alternating zoom), the face ENLARGES and the chin DROPS — so a LOW chin-band box (top:1080+) gets covered by the zoomed chin/mouth. The low band only works WITHOUT a strong zoom. With a strong alternating zoom, **anchor EVERY top element by its BOTTOM at the hairline instead**: `top:auto; bottom:1440px;` (lower edge ≈ where the forehead ends, "rozando el nacimiento del pelo"). This one rule survives both zoom states (zoom-in drops the head BELOW the box; zoom-out keeps the box just above the hairline) AND keeps boxes out of the **Meta-Ads top-crop zone** (elements pegged to `top:80–150` get cut off in feed/placement crops — Diego: "muy arriba, va a quedar cortada"). Apply the SAME `bottom:1440` to cards, chips, badges, `.fslab` labels on b-roll, AND `.ba-tag` on before/afters — all top labels, not just the text cards (Diego flagged the b-roll labels separately). Then the closing hero (no zoom) can sit low (top:1080) over the chest. Full-frame overlays (green screen) still need z-index ≥ ~40 over the transformed `#cam-wrap`.
    4. **Verify in the render, not just the preview:** extract a frame inside EACH overlay's time window and confirm the face is fully clear. If any element touches the face, move it down and re-check. Treat "looks fine in the editor" as not verified.
- **Zoom punch-ins** on emphasis. Gentle = scale ~1.09, one yoyo, `sine.inOut`, ~0.8s. Aggressive (when asked)
  = punch to scale ~1.4–1.45, HOLD ~2s, then pull back. **Origin MUST sit on the subject's face, not 50%** —
  if they sit off-center, measure face x/y with an ffmpeg `drawgrid=w=iw/10:h=ih/10` frame and set
  `transform-origin` per beat. Keep scale ≤~1.45 (1.55 read as "muy fuerte"). Never START already zoomed-in.
- **Stat / name cards** (great for intros): big animated number / credibility cards that pop in (`back.out`)
  one at a time over the presenter — e.g. "+200.000 seguidores", "+$300.000 invertidos", a name lower-third
  (Anton font for the big number). Use the client's REAL numbers.
- **Visual diagram explainer** (loved by Simon/Diego): to explain connections/concepts (APIs, workflows), put the central element as a "brain" (big logo) center-screen on a dark panel and DRAW animated SVG arrows (animate stroke-dashoffset to 0) out to each node as it's mentioned, each with a label (e.g. "API"). Great for tutorials/explainers.
- **Small dynamic overlays**: chips, seals, badges, thematic symbols in corners.
- **Branded graphics**: price comparison (struck-through "fortuna" → "fracción"), cert/FDA seal, location pin,
  thematic icon (snowflake = cryo/cold), **CTA down-arrow** ("Toca el botón ↓", bouncing) to the link button.
- **Music + ducking**: royalty-free bed on its own track. Don't just lower volume — **duck it** vs the voice:
  `ffmpeg -i source.mp4 -vn voice.wav`, then `[m]volume=1.7 … sidechaincompress=threshold=0.12:ratio=3:attack=20:release=350:makeup=2`
  → `music_ducked.mp3` at `data-volume` ~0.35–0.4. (Hard ducking + low volume = "casi no se escucha".)
  - **When to DROP music entirely**: in interviews/2-mic shoots where one speaker (often the off-camera interviewer)
    is recorded much quieter, even ducked music buries their lines. If the quiet voice fights the bed → **remove the
    music, leave voices only**. Diego asked exactly this on the IMG_5323 reel ("mi voz no se escucha → déjalo sin música").
  - **Track choice + level for talking heads**: a track that "builds" hard reads as harsh under a calm voice — Diego
    rejected `cinematic-inspirador` ("está un poquito dura") for a YT intro. For clarity-priority talking heads pick a
    soft, EVEN track (e.g. `chill-luxury`) and keep it VERY low (`data-volume` ~0.10). The voice always wins.
- **Audio leveling (uneven speakers)** — when one voice is much softer than the other (quiet interviewer vs loud
  interviewee), level BEFORE rendering. Compressor (tames the loud peaks + makeup brings the soft voice up) → loudnorm
  (sets overall level). Re-mux onto the source keeping the video untouched (fast, no re-encode):
  `ffmpeg -i source.mp4 -c:v copy -af "acompressor=threshold=-24dB:ratio=4:attack=10:release=200:makeup=4,loudnorm=I=-15:TP=-1.5:LRA=9" -c:a aac -b:a 192k source_leveled.mp4`.
  On IMG_5323 this lifted the mean from **−26 → −18 dB** with peaks safe at −1.1. Verify with `ffmpeg -af volumedetect`
  (mean should rise, max stay < −1). The `<audio id="bg-audio">` keeps pointing at the source file (now leveled);
  `<audio id="bg-video">` still uses the SDR video track.
- **Audio clarity (single speaker — muddy or clipped entrance)** — when the client says "no se entiende mi entrada"
  and `volumedetect` shows `max_volume: 0.0 dB` (clipping), clean it BEFORE rendering: high-pass the rumble, add a
  presence boost for intelligibility, gently compress, and loudnorm with `TP=-1.5` to pull the peaks off the ceiling.
  `ffmpeg -i source.mp4 -c:v copy -af "highpass=f=85,equalizer=f=3000:width_type=q:w=1.2:g=3,acompressor=threshold=-18dB:ratio=3:attack=10:release=200:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=11" -c:a aac -b:a 192k source.mp4`
  (on the "1000 dólares" YT intro this took peaks 0.0 → −1.5 dB and added clarity). Point `<audio id="bg-audio">` at it.
- **Transitions (whoosh + flash)** — subtle. Synth `whoosh.mp3` (pink-noise burst + bandpass + fades), build
  ONE `sfx_bed.mp3` with whooshes at the cut/zoom times via `adelay`+`amix` (one file avoids
  `duplicate_media_discovery_risk`), `data-volume` ~0.4. Pair each with a 1-frame white `#flash`
  (GSAP `opacity 0→0.4→0` keyframes, `overwrite:"auto"`) at the SAME times. Explain "whoosh/flash" in plain words.

## Karaoke captions (footage WITHOUT baked subs — e.g. YouTube)
1. Transcribe (above) → `transcript.json` ([{text,start,end}]).
2. Make `captions.js` next to index.html: `window.__WORDS = <transcript array>;` and include `<script src="captions.js"></script>`.
3. In the main script, build from `window.__WORDS`:
   - Chunk into lines (break on `.?!` once ≥3 words, else every ~6).
   - One absolute `.capline` div per line (stacked same spot, opacity 0); a `<span class="cw">` per word.
   - Show a line `tl.set(div,{opacity:1}, lineStart-0.05)`, hide at `nextLineStart-0.03` (one line at a time).
   - Per word: `tl.set(span,{color:GOLD}, w.start)` then `tl.set(span,{color:WHITE}, max(w.start+0.04,w.end))`;
     base CSS color = dim white → the spoken word lights up, then settles white.
   - Big bold (~58px @1080p) + strong `text-shadow` so it reads over bright b-roll.
   (lint flags these runtime-built spans as `__unresolved__` overlapping-tween warnings — harmless.)

## iPhone HDR reels — magenta-overlay pipeline (validated on 8 reels, 2026-08/09)
For vertical talking-head reels shot on iPhone (HEVC Main10, HLG). The HDR master is NEVER re-graded: HyperFrames
renders ONLY the graphics layer on a magenta background, and ffmpeg keys it over the untouched master.
Generator template: `templates/build_overlay.py`.
1. **Prep**
   - `ffmpeg -i raw.MP4 -map 0:v:0 -map 0:a:0 -c copy source.mp4` (drops the extra iPhone metadata tracks).
   - Map the shots before planning: a per-second contact sheet `-vf "fps=1,<TM>,scale=180:320,tile=13x6" -frames:v 1`
     (tile n = second n, row-major) + exact cut times on an SDR proxy:
     `ffmpeg -i proxy.mp4 -vf "scale=270:480,select='gt(scene,0.25)',metadata=print:file=-" -an -f null -`.
     `<TM>` = the hable tonemap chain from the gotchas — for LOOKING only, never for the deliverable.
     (ffmpeg `drawtext` segfaults without fontconfig on Windows — skip frame labels.)
   - Measure the chin with `drawgrid=w=iw:h=ih/20` on a tonemapped frame at the START **and** at the END: the
     presenter moves (chin went y≈1000 → 1080 within one reel). Cards must clear the lowest chin.
2. **Transcribe** (`large-v3`) → `words_fixed.json`. Whisper glues the conjunction "Y" to the next word
   ("Yyo", "Yaquí", "Yahora", "Ysi") → split it into two words; fix names/brands ("Claudia"→"Claude",
   "la guía"→"la IA", "MetaAds"→"Meta Ads").
3. **Audio** — clean voice, then a LOW music bed that ducks under it:
   - voice → `voice.wav`: `highpass=f=85,equalizer=f=3000:width_type=q:w=1.2:g=3,acompressor=threshold=-20dB:ratio=3:attack=10:release=200:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=11`
     (also rescues raws clipped at 0.0 dB).
   - mix → `final_audio.wav` (music input with `-stream_loop -1`):
     `[1:a]atrim=0:DUR,asetpts=N/SR/TB,volume=0.20,afade=t=in:st=0:d=0.5,afade=t=out:st=<DUR-1.3>:d=1.2[mus];[0:a]asplit=2[v1][vsc];[mus][vsc]sidechaincompress=threshold=0.04:ratio=9:attack=8:release=280:makeup=1[duck];[v1][duck]amix=inputs=2:duration=first:normalize=0[mix];[mix]loudnorm=I=-14:TP=-1.5:LRA=11`
4. **Support material**
   - B-roll: `Get-Broll.ps1 -Orientation portrait -Count 2` per idea → look at a contact sheet of the candidates → pick
     (reject off-brand ones, e.g. face tattoos, toy robots) → conform each to its exact slot:
     `ffmpeg -ss S -i clip.mp4 -t D -an -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=60,format=yuv420p" -c:v libx264 -crf 17 p_name.mp4`.
   - AI images: upscale to 1080×1920 (`scale=...:flags=lanczos,crop=1080:1920`) before use. **Never repeat an AI image
     in consecutive reels** — `md5sum` the library against the other projects' assets; if used, generate new ones (~$0.02 each).
   - Frames from `.mov` files: put `-ss` AFTER `-i` — fast seek on .mov returned the wrong frames.
5. **`build_overlay.py`** — data lists → one `index.html` on `#FF00FF`:
   - `CUTS`: full-screen b-roll as opaque `class="cut clip"` video/img INSIDE the overlay (they cover the magenta, so they
     show over the master), slow zoom 1.10→1.0.
   - `CARDS`: one card each. `GROUPS`: lists whose items light up ONE BY ONE at each word's timestamp (`t-0.10`).
   - Scale-only animation, GSAP `xPercent/yPercent` centering (see gotchas).
   - Captions: white Nunito 900 chunks (≤2 words / ≤15 chars) at `top:1545px`. `SUB_HOLE` hides them while an embedded
     clip plays its own voice + baked text (e.g. a demo ad inside the reel); `SUB_END` stops them when the CTA appears.
   - Spanish accents in cards via HTML entities (`&aacute;`, `&Eacute;`, `&ntilde;`).
6. **Preview → export**
   - `python build_overlay.py preview` + `npx hyperframes preview . --port NNNN`; iterate there (see gotcha).
   - On OK: `python build_overlay.py` → `npx hyperframes render . --fps 60 --quality high --crf 14 --output renders/overlay-magenta.mp4` → composite:
     `ffmpeg -y -i source.mp4 -i renders/overlay-magenta.mp4 -i final_audio.wav -filter_complex "[1:v]zscale=tin=bt709:min=bt709:pin=bt709:rin=tv:t=linear:p=bt709,format=gbrpf32le,exposure=exposure=2.0,zscale=pin=bt709:p=bt2020:t=arib-std-b67:m=bt2020nc:r=tv,format=yuv444p10le,format=yuva444p10le,chromakey=0xFF00FF:0.30:0.02[ovl];[0:v][ovl]overlay=0:0:format=yuv420p10:shortest=1[v]" -map "[v]" -map 2:a -c:v libx265 -preset fast -crf 18 -pix_fmt yuv420p10le -tag:v hvc1 -color_primaries bt2020 -color_trc arib-std-b67 -colorspace bt2020nc -color_range tv -c:a aac -b:a 192k renders/FINAL.mp4`
   - Timing: a 77 s reel ≈ 5 min overlay render + ~4 min composite. Even a one-cutaway change means a full re-export —
     say so up front ("¿por qué tanta demora si era una cosita?"), and show small changes in the preview first.
   - `hyperframes snapshot` with many videos: add `--timeout 40000` and keep heavy intermediates OUT of `assets/`.
7. **Verify before saying "listo"**: ffprobe (`hevc Main 10`, `arib-std-b67`, `60/1`, full duration); a tonemapped grid of
   ~18 frames covering every card window (face clear, cards whole, no purple wash, b-roll opaque); `volumedetect` on speech
   windows (final within ~2–3 dB of `voice.wav`) and `max_volume ≤ -1.5 dB`.

**Diego's reel style (approved / corrected):**
- **Everything in the chin band** (between chin and captions; card center ≈ y1240–1260). Instagram's feed/grid preview
  crops a 9:16 reel to ~4:5, so anything above y≈285 or below y≈1635 gets cut off.
- **Lots of b-roll from the start**: face + hook card for the first ~2 s, then a cutaway every few seconds tied to the
  words ("pusiste muy poquito material de apoyo en los primeros segundos"). Covering ~50–60% of the talking-head time is fine.
- **Lists light up one per spoken word**, never all at once. End on a **CTA box** ("Comenta PALABRA · y te envío el video 👇").
- Rock bed (`action-promo-rock`) low + ducked.
- "Quita / mueve el b-roll X": change only that `CUTS` entry, keep the rest as approved.

## Nano Banana image generation (Kie AI)
Reusable generator: `Editor Videos/_tools/Get-NanoBanana.ps1 -PromptsJson <prompts.json> -OutDir <proj>/assets/img [-Model google/nano-banana] [-Size 16:9|9:16]`.
- API: POST `api.kie.ai/api/v1/jobs/createTask` (`Authorization: Bearer $env:KIE_API_KEY`,
  body `{model, input:{prompt, output_format:"png", image_size}}`) → `taskId`; poll
  `…/recordInfo?taskId=…` until `data.state=="success"`; image URL is inside `data.resultJson`.
- **Models & price (KIE)**: `google/nano-banana` (básico) ≈ **$0.02/img (4 credits)** ·
  `google/nano-banana-2` (to 4K) ≈ **$0.04** · `google/nano-banana-pro` (perfect in-image text) ≈ **$0.12**.
  **WAN = VIDEO, not images** (Wan 2.5 ≈ $0.06/s 720p, $0.10/s 1080p) — only for bespoke AI video b-roll.
- **Text in images = SPANISH**: English prompts bake English text (e.g. "SALES VIDEO PROJECT"). Prefer
  textless/visual prompts; if text is needed, give the exact Spanish words. Match `image_size` to the project.

## Royalty-free b-roll video (Pexels / Pixabay)
Reusable downloader: `Editor Videos/_tools/Get-Broll.ps1 -Query "…" -OutDir <proj>/assets/broll -Count N [-Source pexels|pixabay] [-Orientation portrait|landscape]`.
- **Pexels = primary** (only one with an orientation filter for vertical): `v1/videos/search?orientation=portrait|landscape`,
  header `Authorization: $env:PEXELS_API_KEY`, pick the `video_files` link closest to the target height. Free, commercial-OK.
- **Pixabay = variety/fallback**: `api/videos/?key=$env:PIXABAY_API_KEY`; video API has **NO orientation filter**
  (mostly landscape) → downloader keeps only vertical renditions for 9:16; cache 24h, no mass downloads.
- Keys = env vars (`PEXELS_API_KEY`, `PIXABAY_API_KEY`, set via `setx`). Do NOT use the Apify `Pixabay-Image-Scraper` (images only).

## Client resource library — auto-place the client's own assets
For recurring clients, keep a `Recursos/{fotos,videos}/` folder of THEIR real photos/clips. Before editing each
video: scan it, read/understand every asset, and AUTO-place the matching one as "by the way" support when the VO
hits that topic (e.g. his face/IG screenshot on "+200 mil seguidores"; a lifestyle/car shot on the aspirational
close). Keep a running catalog in memory. Real client assets (proof, lifestyle) beat generic stock for trust.
Include **testimonial screenshots** in the library — drop them as bottom-corner insets on authority/proof beats
("he generado millones para mis clientes" → Martín/Sergio/Alejandra testimonials). They're usually 16:9 → 16:9 frames.

## Openings — keep each ad in a series DIFFERENT (A/B)
Every ad in a series must open differently. Used so far on Criolipólisis: **01** baseline · **03** text-hook card
(teal gradient) · **04** scenery cold-open (Colombia/Eje b-roll + lower banner) · **05** travel cold-open
(airplane b-roll + 2-line kinetic hook). Pick a fresh angle for the next.

## Style preferences
- **Font = Poppins** (woff2 + `@font-face`; **Anton** for big stat numbers). NOT monospace.
- **Text BIG** — overlays large/legible (chips ~50px, labels ~38px+, pins ~44px). When unsure, bigger.
- **Brand example — Francia Salazar Estética**: teal `#14534A`/`#0E3B36`, cream `#EFE7D9`, gold `#C9A24B`.
- **Compliance**: don't fabricate exact prices/medical claims — qualitative ("miles de USD → una fracción");
  the client supplies real figures.

## Technical gotchas
- Transcription needs whisper.cpp: `scoop install whisper-cpp` (binary `whisper-cli`).
- Display fonts (Poppins, Anton) NOT auto-embedded — download `.woff2` + `@font-face`. IBM Plex Mono auto-resolves.
- Ken Burns/scale on media trips inspect's `container_overflow` → mark the wrapper `data-layout-allow-overflow`.
- Reusing one media file in two clips → `duplicate_media_discovery_risk` → unique filenames (or one pre-built bed).
- Every timeline-visible media element needs an `id` (renderer discovery) and `class="clip"` + `data-*` timing.
- **VP9 alpha (cutout) in ffmpeg**: Chrome honors WebM alpha natively at render; ffmpeg IGNORES it unless you
  decode with `-c:v libvpx-vp9` AND add `[fg]format=yuva420p` before `overlay`.
- **Cutout / green-screen / replace background**: built in — `npx hyperframes remove-background <in> -o out.webm`
  (model u2net_human_seg, ~2 fps CPU ≈ 10 min/75s; transparent WebM/.mov/.png). Good on a seated talking head.
  More precise (GPU/cloud): Robust Video Matting, BiRefNet, SAM2, Runway/Unscreen.
- **⚠️ SUBTITLES GO LAST — hard rule.** Background removal also strips **baked-in subtitles** (they sit on the bg)
  → re-adding looks broken. You CANNOT cleanly cut out a clip that already has burned subs. For any video where
  cutout/bg-replacement might be wanted, deliver footage WITHOUT baked subtitles and add captions as the TOP layer last.
- **"Two talking faces" (avatar artifact)**: when a bg poster also lip-syncs, AI bg-removal KEEPS it (it's a human).
  Reframe/crop it out, cover with a small medallion, or drop the take.
- **iPhone/HDR footage → convert to SDR BEFORE rendering.** iPhone records HDR (HLG, bt2020, 10-bit). The HyperFrames HDR render path is slow/unstable and times out ("HDR frame extraction failed for bg-video"). Tonemap to SDR first: `ffmpeg -i in.mp4 -vf "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p" -color_primaries bt709 -color_trc bt709 -colorspace bt709 -c:a copy out.mp4`. Verify ffprobe color_transfer = bt709 (not arib-std-b67/smpte2084).
- **⚠️ BUT if the client compares against the raw iPhone clip and rejects the SDR look ("se dañó el color"), DO NOT tonemap the master — keep the deliverable HDR and lift the SDR pieces instead.** ANY tonemap changes the footage's look; Diego rejects every variant (mobius washed, hable "dañado") when viewed next to the original on his phone. Validated recipe (2026-08, "pongamos a prueba"): master stays untouched HLG 10-bit; every SDR insert (montages, HyperFrames overlay renders, b-roll) gets brightness-lifted ~4x into HLG:
  `zscale=tin=bt709:min=bt709:pin=bt709:rin=tv:t=linear:p=bt709,format=gbrpf32le,exposure=exposure=2.0,zscale=pin=bt709:p=bt2020:t=arib-std-b67:m=bt2020nc:r=tv,format=yuv420p10le` + `-color_primaries bt2020 -color_trc arib-std-b67 -colorspace bt2020nc -color_range tv`, then concat/overlay everything as yuv420p10le.
  Traps that cost a full afternoon: (1) `zscale`'s `npl` does NOTHING for bt709 input — it is not a brightness knob, use `exposure` (stops: 2.0 = 4x) in linear float; (2) SDR placed at the "standard" level always looks dark next to iPhone HDR (~230 vs ~450-650 YAVG); (3) don't judge by full-frame YAVG when the insert has a dark design background — crop-measure the content panel and match it to the source footage (~450-650); (4) the PC monitor lies about HDR — Diego verifies on his phone, send the file there; (5) **the HDR deliverable MUST be HEVC Main10 (`-c:v libx265 -crf 18 -pix_fmt yuv420p10le -tag:v hvc1` + the bt2020/arib-std-b67 tags)** — H.264 High10 (`libx264` + yuv420p10le) won't play in Windows/most players ("no lo reproduce el reproductor"); iPhone masters are HEVC Main10, match them. Intermediates can stay H.264 10-bit; convert at the last step.
- **Green/magenta-screen overlay layer: keep `chromakey` blend LOW (0.02), and pick the key color your DESIGN doesn't use.** Compositing a HyperFrames overlay render onto footage: `chromakey=0x<COLOR>:0.15:0.02`. Two traps hit in production: (1) a **green** key eats brand greens in the design (borders, numbers vanished) — use **magenta `#FF00FF`** when the design uses green; (2) a high **blend** (0.08) makes *skin tones* semi-transparent, so full-screen b-roll with faces ghosts the underlying presenter through it ("los cutaways salen semitransparentes"). **Calibrated values when the overlay is color-converted to HLG before keying: `chromakey=0xFF00FF:0.30:0.02`.** The conversion SHIFTS the key color, so a tight similarity no longer matches it — 0.15-0.22 leaves a purple wash over the whole frame, 0.40 erases the cards themselves, 0.30 is the sweet spot (background gone, skin opaque, cards intact). The **blend** is what causes skin bleed — keep it at 0.02, never 0.08. Symptom check: a suspiciously SMALL output file (flat magenta compresses to nothing) means the key failed — verify frames, not just the file. Animate overlay elements with **scale only, never opacity fades** (a half-faded element blends with the key color and the key can't remove it).
- **Previewing the HDR/magenta pipeline live (Diego hates waiting a full render for small changes):** give `build_overlay.py` a `preview` mode that puts a tonemapped SDR H.264 proxy of the source (`preview_base.mp4`, with the mixed audio, `data-has-audio="true"`, track 0, root bg black) UNDER the overlay; iterate in `hyperframes preview`, and only on his OK rebuild without the flag (magenta) → render → chroma composite. Tell him the preview colors differ slightly; the export keeps his HDR.
- **Cards shifted left in the render:** CSS `transform:translate(-50%,-50%)` + GSAP `scale` makes GSAP bake the translate into PIXELS measured before the web fonts load (Anton/Poppins) → wide cards end up off-center. Center with GSAP instead: CSS only `left:50%`, and `gsap.set(el,{xPercent:-50,yPercent:-50,scale:0.001})`.
- **Two subtitles overlapping for a frame:** if a chunk shows at `start-0.04`, hide the previous one at `next-0.06` (not `next-0.02`).
- **iPhone clips arrive ROTATED — bake the rotation before using.** Phone "vertical" clips are often stored as
  `1920x1080` with a `rotation:-90` display-matrix side-data (ffprobe `-show_entries stream_side_data=rotation`). The
  renderer may ignore the flag and show them sideways. Re-encode to bake it (autorotate is ON by default when you
  re-encode): `ffmpeg -i in.mp4 -c:v libx264 -preset fast -crf 20 -an out.mp4` → a true upright `1080x1920`. A tonemap
  pass also bakes it. THEN size the inset frame to the now-correct orientation (vertical → 4:5; see masked-insets above).
- **Export has native clips but NO GSAP overlays (captions/cards/diagram)?** The inline script threw before `window.__timelines["main"] = tl`, so the timeline never registered → only `class="clip"` media renders. Fix: (1) register the timeline IMMEDIATELY after `gsap.timeline()`, (2) avoid `getTotalLength()` on SVG when building (throws in headless render though the Studio preview works) — use a fixed `stroke-dasharray` for draw-on arrows. Verify the EXPORT by extracting frames, not just the preview.
- Kie AI Nano Banana: env var `KIE_API_KEY` (see the image-generation section for models/pricing/Spanish-text rule).

## Final render
`npx hyperframes render <project> --quality high --output <project>/renders/<name>-FINAL.mp4`.
Then VERIFY: extract frames (incl. adjacent frames to catch freezes) AND confirm the audio carries the **voice**,
not just music — `ffmpeg -af volumedetect` on a speech window vs the source voice should be within a few dB.

## Delivery (caption + send to the client)
After the FINAL is approved, the client often wants the post-ready copy AND the file on their phone.
- **Instagram copy** (when asked): write it in **Spanish**, in the client's voice. Proven structure for Diego's reels:
  **hook** (a shocking stat or question — e.g. "+$1.000.000 USD/año") → **problem** (the slow manual way) →
  **solution** (the tools/diagram from the video, e.g. Claude + APIs to ElevenLabs/Kie AI/Pexels) → **CTA with a
  comment keyword** ("Comenta AUTOMATIZAR y te paso el tutorial") → a block of niche **hashtags**. Save it next to
  the project as `caption-ig.txt` so it's reusable.
- **Auto-publishing (Zernio)**: a "success" log does NOT mean Instagram accepted the video — poll the post status and
  retry Instagram alone if it failed. TikTok direct posting is often "at capacity" → send it as a draft to the Creator
  Inbox (`tiktokSettings.draft: true`) and tell the user to publish it from the TikTok app.
- **Send to client's Telegram**: a Telegram bot is configured in the `Carruseles IG Premium` / `carruseles-ig`
  projects — creds load from env vars `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` or those projects' `config.json`
  (`telegram_bot_token` / `telegram_chat_id`). **NEVER hard-code or publish the token** — read it at runtime.
  Send the video via the Bot API `sendVideo` (multipart) + the caption as a separate `sendMessage` so he can copy-paste it.
  - **⚠️ 50 MB bot limit**: the FINAL high-quality render (often ~180 MB) is too big for a bot. Make a **compressed
    copy < 50 MB** first: `ffmpeg -i FINAL.mp4 -c:v libx264 -b:v 3500k -maxrate 3900k -bufsize 7000k -preset medium -pix_fmt yuv420p -c:a aac -b:a 128k -movflags +faststart <name>-TG.mp4`
    (a 92s 1080×1920 reel lands ~38 MB). No real quality loss for IG — **Instagram re-compresses uploads anyway** —
    but keep the full-quality master in `renders/` for archive/other uses.
