@echo off
echo Select Pyinstaller option
echo [1] onedir
echo [2] onefile
set /p input=" "

if "%input%"=="1" (
	python -m PyInstaller --clean --onedir --noconfirm --noconsole -n "CommandRunner" -i assets\icon.ico src\main.py
) else if "%input%"=="2" (
	python -m PyInstaller --clean --onefile --noconfirm --noconsole -n "CommandRunner" -i assets\icon.ico src\main.py
) else exit /b

xcopy assets "dist\CommandRunner" /E /I /Y
pause
