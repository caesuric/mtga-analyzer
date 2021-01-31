pyinstaller --onefile show-progress.py
ren dist\show-progress.exe overlay-backend.exe
copy dist\overlay-backend.exe overlay-frontend\dist\overlay-backend.exe
cd overlay-frontend
electron-builder -w
