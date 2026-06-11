---
name: video-ad-editing
description: >-
  Edit and enhance talking-head / AI-avatar videos with HyperFrames — both vertical 9:16
  ads (Meta/TikTok) and 16:9 YouTube intros/long-form. Use whenever the user asks to "edit
  this video", add support material / b-roll, "make it more dynamic", add zooms, captions
  (incl. karaoke word-highlight), AI support images, badges, music, sound effects, or export.
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
2. **Transcribe for content/timing**: `npx hyperframes transcribe source.mp4 --model medium --language es`.
   NEVER a `.en` model for Spanish (it translates). `small` silently TRUNCATES long clips — use `medium`.
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
- **Zoom punch-ins** on emphasis. Gentle = scale ~1.09, one yoyo, `sine.inOut`, ~0.8s. Aggressive (when asked)
  = punch to scale ~1.4–1.45, HOLD ~2s, then pull back. **Origin MUST sit on the subject's face, not 50%** —
  if they sit off-center, measure face x/y with an ffmpeg `drawgrid=w=iw/10:h=ih/10` frame and set
  `transform-origin` per beat. Keep scale ≤~1.45 (1.55 read as "muy fuerte"). Never START already zoomed-in.
- **Stat / name cards** (great for intros): big animated number / credibility cards that pop in (`back.out`)
  one at a time over the presenter — e.g. "+200.000 seguidores", "+$300.000 invertidos", a name lower-third
  (Anton font for the big number). Use the client's REAL numbers.
- **Small dynamic overlays**: chips, seals, badges, thematic symbols in corners.
- **Branded graphics**: price comparison (struck-through "fortuna" → "fracción"), cert/FDA seal, location pin,
  thematic icon (snowflake = cryo/cold), **CTA down-arrow** ("Toca el botón ↓", bouncing) to the link button.
- **Music + ducking**: royalty-free bed on its own track. Don't just lower volume — **duck it** vs the voice:
  `ffmpeg -i source.mp4 -vn voice.wav`, then `[m]volume=1.7 … sidechaincompress=threshold=0.12:ratio=3:attack=20:release=350:makeup=2`
  → `music_ducked.mp3` at `data-volume` ~0.35–0.4. (Hard ducking + low volume = "casi no se escucha".)
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
- Kie AI Nano Banana: env var `KIE_API_KEY` (see the image-generation section for models/pricing/Spanish-text rule).

## Final render
`npx hyperframes render <project> --quality high --output <project>/renders/<name>-FINAL.mp4`.
Then VERIFY: extract frames (incl. adjacent frames to catch freezes) AND confirm the audio carries the **voice**,
not just music — `ffmpeg -af volumedetect` on a speech window vs the source voice should be within a few dB.
