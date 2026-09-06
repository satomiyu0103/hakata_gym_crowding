@echo off
rem 取得のみ（Sheets へ書き込まない）。休館判定も無視するテスト用。
call "%~dp0run_hakata_crowding.bat" --dry-run --force
