<#
  Get-Broll.ps1 — descarga b-roll royalty-free (MP4) por palabra clave.
  Fuentes: Pexels (oficial) y Pixabay (oficial). Sin Apify.

  Requiere las keys como variables de entorno:
    $env:PEXELS_API_KEY   (header Authorization)
    $env:PIXABAY_API_KEY  (?key=)

  Ejemplos:
    .\_tools\Get-Broll.ps1 -Query "coffee region colombia aerial" -OutDir ".\proyecto\assets\broll" -Count 2
    .\_tools\Get-Broll.ps1 -Query "spa massage relax" -Source pixabay -Count 1 -OutDir ".\x\broll"
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory=$true)][string]$Query,
  [string]$OutDir = ".",
  [int]$Count = 1,
  [ValidateSet('pexels','pixabay')][string]$Source = 'pexels',
  [ValidateSet('portrait','landscape','square')][string]$Orientation = 'portrait',
  [int]$TargetHeight = 1920
)

if (-not (Test-Path $OutDir)) { New-Item -ItemType Directory -Force $OutDir | Out-Null }
$slug = ($Query -replace '[^\w]+','-').Trim('-').ToLower()
$creditsFile = Join-Path $OutDir "CREDITS-broll.txt"

function Save-Mp4($url, $path) {
  Invoke-WebRequest -Uri $url -OutFile $path -UseBasicParsing
  return (Test-Path $path)
}

if ($Source -eq 'pexels') {
  if (-not $env:PEXELS_API_KEY) { throw "Falta `$env:PEXELS_API_KEY (pega tu key de Pexels)." }
  $headers = @{ Authorization = $env:PEXELS_API_KEY }
  $u = "https://api.pexels.com/v1/videos/search?query=$([uri]::EscapeDataString($Query))&orientation=$Orientation&per_page=$([math]::Max($Count,3))"
  $resp = Invoke-RestMethod -Uri $u -Headers $headers
  if (-not $resp.videos) { "Sin resultados para '$Query'."; return }
  $i = 0
  foreach ($v in $resp.videos) {
    if ($i -ge $Count) { break }
    $mp4 = $v.video_files | Where-Object { $_.file_type -eq 'video/mp4' -and [int]$_.width -gt 0 -and [int]$_.height -ge [int]$_.width }
    if (-not $mp4) { $mp4 = $v.video_files | Where-Object { $_.file_type -eq 'video/mp4' -and [int]$_.width -gt 0 } }
    $best = $mp4 | Sort-Object { [math]::Abs([int]$_.height - $TargetHeight) } | Select-Object -First 1
    if (-not $best) { continue }
    $i++
    $name = "{0}_{1}_{2}x{3}.mp4" -f $slug, $v.id, $best.width, $best.height
    $path = Join-Path $OutDir $name
    if (Save-Mp4 $best.link $path) {
      Add-Content $creditsFile "$name  |  Pexels  |  $($v.user.name)  |  $($v.url)"
      "DL  $name  ($($best.width)x$($best.height), ${$v.duration}s)  by $($v.user.name)"
    }
  }
}
elseif ($Source -eq 'pixabay') {
  if (-not $env:PIXABAY_API_KEY) { throw "Falta `$env:PIXABAY_API_KEY (pega tu key de Pixabay)." }
  $u = "https://pixabay.com/api/videos/?key=$($env:PIXABAY_API_KEY)&q=$([uri]::EscapeDataString($Query))&per_page=$([math]::Max($Count*5,10))"
  $resp = Invoke-RestMethod -Uri $u
  if (-not $resp.hits) { "Sin resultados para '$Query'."; return }
  $i = 0
  foreach ($v in $resp.hits) {
    if ($i -ge $Count) { break }
    # Pixabay videos have NO orientation param -> pick a vertical rendition; skip landscape when portrait wanted
    $cands = @($v.videos.large, $v.videos.medium, $v.videos.small) | Where-Object { $_ -and $_.url }
    if (-not $cands) { continue }
    $vert = $cands | Where-Object { [int]$_.height -gt [int]$_.width }
    if ($Orientation -eq 'portrait') {
      if (-not $vert) { continue }
      $f = $vert | Sort-Object { [math]::Abs([int]$_.height - $TargetHeight) } | Select-Object -First 1
    } else {
      $f = $cands | Sort-Object { [math]::Abs([int]$_.height - $TargetHeight) } | Select-Object -First 1
    }
    if (-not $f.url) { continue }
    $i++
    $name = "{0}_{1}_{2}x{3}.mp4" -f $slug, $v.id, $f.width, $f.height
    $path = Join-Path $OutDir $name
    if (Save-Mp4 $f.url $path) {
      Add-Content $creditsFile "$name  |  Pixabay  |  $($v.user)  |  $($v.pageURL)"
      "DL  $name  ($($f.width)x$($f.height))  by $($v.user)"
    }
  }
}
"Listo -> $OutDir"
