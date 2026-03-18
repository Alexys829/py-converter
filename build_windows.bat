@echo off
echo === PyConverter - Nuitka Build ===
echo.

REM Generate icon if missing
if not exist "pyconverter\resources\icons\app_icon.ico" (
    echo Generating icon...
    python scripts\generate_ico.py
)

echo Building with Nuitka...
python -m nuitka ^
    --standalone ^
    --onefile ^
    --windows-console-mode=disable ^
    --windows-icon-from-ico=pyconverter\resources\icons\app_icon.ico ^
    --enable-plugin=pyside6 ^
    --include-package=pyconverter ^
    --include-data-dir=pyconverter\resources=pyconverter\resources ^
    --output-filename=PyConverter.exe ^
    --company-name="PyConverter" ^
    --product-name="PyConverter" ^
    --product-version=0.1.0 ^
    --file-description="Universal File Converter" ^
    main.py

echo.
echo Done! Output: PyConverter.exe
pause
