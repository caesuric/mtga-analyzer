@echo off
pyinstaller --onefile show-progress.py
copy dist\show-progress.exe dist\overlay-backend.exe
copy dist\overlay-backend.exe overlay-frontend\dist\overlay-backend.exe
cd overlay-frontend
electron-builder -w
