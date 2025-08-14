@echo off
REM venv 경로 지정 (예시: 프로젝트 폴더 내 venv)
set VENV_PATH=c:\Users\ayj604516\OneDrive\연애\FlotoYTMusic\venv

REM venv 활성화
call "%VENV_PATH%\Scripts\activate.bat"

REM 작업 폴더 이동
cd /d "c:\Users\ayj604516\OneDrive\연애\FlotoYTMusic"

REM 파이썬 스크립트 실행
python create_yt_playlist.py >> log.txt 2>&1

REM venv 비활성화 (선택)
deactivate