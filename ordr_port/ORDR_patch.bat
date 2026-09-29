@echo off
chcp 65001 >nul
cd /d "%~dp0"
if "%~1"=="" (
  echo 새 버전 맵 w3x 파일을 이 파일 위로 끌어다 놓으세요.
  pause
  exit /b
)
where python >nul 2>nul
if %errorlevel%==0 (
  python ordr_patch.py "%~1"
) else (
  py ordr_patch.py "%~1"
)
pause
