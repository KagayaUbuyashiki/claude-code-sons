# Tocador unico da fila de sons (queue\*.json). Um mutex garante que so um audio toca por vez;
# instancias extras esperam a vez e drenam o que sobrar na fila.
$ErrorActionPreference = 'SilentlyContinue'
Add-Type -AssemblyName PresentationCore

function Show-Toast([string]$title, [string]$body) {
  try {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
    [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
    $esc = { param($s) [System.Security.SecurityElement]::Escape($s) }
    $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
    $xml.LoadXml("<toast><visual><binding template='ToastGeneric'><text>$(& $esc $title)</text><text>$(& $esc $body)</text></binding></visual><audio silent='true'/></toast>")
    $appId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show([Windows.UI.Notifications.ToastNotification]::new($xml))
  } catch {}
}

$mutex = New-Object System.Threading.Mutex($false, 'Global\ClaudeCodeSfxPlayer')
try { [void]$mutex.WaitOne(900000) } catch [System.Threading.AbandonedMutexException] {}
try {
  $queue = Join-Path $PSScriptRoot 'queue'
  while ($true) {
    $item = Get-ChildItem $queue -Filter '*.json' | Sort-Object Name | Select-Object -First 1
    if (-not $item) { break }
    $j = Get-Content $item.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
    Remove-Item $item.FullName -Force
    if (-not $j) { continue }
    $age = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds() - [double]$j.ts
    if ($age -gt 90) { continue }
    if ($j.toast) { Show-Toast $j.toast[0] $j.toast[1] }

    $p = New-Object System.Windows.Media.MediaPlayer
    $p.Volume = 1.0
    $p.Open([Uri]$j.file)
    $t = 0
    while (-not $p.NaturalDuration.HasTimeSpan -and $t -lt 60) { Start-Sleep -Milliseconds 50; $t++ }
    $p.Play()
    $ms = if ($p.NaturalDuration.HasTimeSpan) { $p.NaturalDuration.TimeSpan.TotalMilliseconds } else { 15000 }
    Start-Sleep -Milliseconds ([int][Math]::Min($ms + 250, 60000))
    $p.Stop(); $p.Close()
  }
} finally { $mutex.ReleaseMutex() }
