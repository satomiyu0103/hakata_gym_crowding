@echo off
rem 博多体育館混雑取得 RPA — 手動実行用（正本）
rem 使い方: ダブルクリック、または引数付きで実行（例: --dry-run --force）
chcp 65001 >nul
cd /d "%~dp0.."

echo [博多体育館混雑取得] 開始...
uv run python -m hakata_gym_crowding.cli %*
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% neq 0 (
    echo.
    echo エラー終了（コード %EXIT_CODE%）。logs\run.log を確認してください。
) else (
    echo.
    echo 正常終了。
)

pause
exit /b %EXIT_CODE%
