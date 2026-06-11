<#
  Get-NanoBanana.ps1 — genera imágenes con KIE AI (Nano Banana) y las descarga.
  Requiere $env:KIE_API_KEY. Modelo por defecto: google/nano-banana (básico, ~4 créditos/img).

  -PromptsJson : ruta a un .json con [{ "name": "slug", "prompt": "..." }, ...]
  -OutDir      : carpeta de salida (cada imagen -> <name>.png)
  -Model       : google/nano-banana (def) | google/nano-banana-2 | google/nano-banana-pro
  -Size        : "16:9" (def) | "9:16" | "1:1"
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$PromptsJson,
  [Parameter(Mandatory=$true)][string]$OutDir,
  [string]$Model = "google/nano-banana",
  [string]$Size = "16:9"
)
$key = $env:KIE_API_KEY
if (-not $key) { throw "Falta `$env:KIE_API_KEY" }
$h = @{ Authorization = "Bearer $key" }
New-Item -ItemType Directory -Force $OutDir | Out-Null
$prompts = Get-Content $PromptsJson -Raw -Encoding UTF8 | ConvertFrom-Json

foreach ($p in $prompts) {
  $body = @{ model = $Model; input = @{ prompt = $p.prompt; output_format = "png"; image_size = $Size } } | ConvertTo-Json -Depth 6 -Compress
  try {
    $ct = Invoke-RestMethod -Uri "https://api.kie.ai/api/v1/jobs/createTask" -Method Post -Headers $h -ContentType "application/json" -Body $body
  } catch { "CREATE-ERR $($p.name): $($_.Exception.Message)"; continue }
  $taskId = $ct.data.taskId
  if (-not $taskId) { "NO-TASKID $($p.name)"; continue }
  $url = $null
  for ($i = 0; $i -lt 45; $i++) {
    Start-Sleep -Seconds 4
    try { $ri = Invoke-RestMethod -Uri "https://api.kie.ai/api/v1/jobs/recordInfo?taskId=$taskId" -Headers $h } catch { continue }
    $st = $ri.data.state
    if ($st -eq "success") {
      $raw = $ri.data.resultJson
      if ($raw) {
        try { $rj = $raw | ConvertFrom-Json; $url = $rj.resultUrls[0]; if (-not $url) { $url = $rj.resultUrl } } catch {}
        if (-not $url) { $m = [regex]::Match($raw, 'https?://[^"\\]+\.(png|jpg|jpeg|webp)'); if ($m.Success) { $url = $m.Value } }
      }
      break
    }
    if ($st -eq "fail") { "FAIL $($p.name): $($ri.data.failMsg)"; break }
  }
  if ($url) {
    $out = Join-Path $OutDir ($p.name + ".png")
    try { Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing; "OK   $($p.name)  ($([math]::Round((Get-Item $out).Length/1KB))KB)" }
    catch { "DL-ERR $($p.name): $($_.Exception.Message)" }
  } else { "NO-URL $($p.name)" }
}
"Listo -> $OutDir"
