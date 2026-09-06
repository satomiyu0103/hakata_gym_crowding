# Desktop\RPA に手動実行ショートカットを作成（パターン A: 正本はリポジトリ内 BAT）
# 使い方: powershell -NoProfile -ExecutionPolicy Bypass -File scripts\create_desktop_shortcuts.ps1

$ErrorActionPreference = "Stop"

$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$desktopRpa = Join-Path $env:USERPROFILE "Desktop\RPA"
New-Item -ItemType Directory -Force -Path $desktopRpa | Out-Null

$shortcuts = @(
    @{
        FileName = "博多体育館混雑取得.lnk"
        Target   = Join-Path $repo "scripts\run_hakata_crowding.bat"
        Desc     = "博多体育館トレーニング室 混雑取得（手動・通常実行）"
    }
    @{
        FileName = "博多体育館混雑取得_テスト.lnk"
        Target   = Join-Path $repo "scripts\run_hakata_crowding_dry_run.bat"
        Desc     = "博多体育館混雑取得 dry-run（休館判定スキップ・Sheets 書込なし）"
    }
)

$wsh = New-Object -ComObject WScript.Shell
foreach ($item in $shortcuts) {
    $lnkPath = Join-Path $desktopRpa $item.FileName
    $lnk = $wsh.CreateShortcut($lnkPath)
    $lnk.TargetPath = $item.Target
    $lnk.WorkingDirectory = $repo
    $lnk.Description = $item.Desc
    $lnk.Save()
    Write-Host "作成: $lnkPath"
}

Write-Host "完了: $desktopRpa"