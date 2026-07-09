python -m PyInstaller --clean --onedir --noconfirm --noconsole -n "CommandRunner" -i assets\icon.ico src\main.py
xcopy assets "dist\CommandRunner" /E /I /Y
pause