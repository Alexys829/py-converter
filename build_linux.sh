#!/bin/bash
set -e
echo "=== PyConverter - Linux Build ==="

source .venv/bin/activate
pip install pyinstaller -q

# Build with PyInstaller
echo "Building with PyInstaller..."
pyinstaller pyconverter.spec

# Create AppImage
APPDIR="PyConverter.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/icons/hicolor/128x128/apps"

cp -r dist/pyconverter/* "$APPDIR/usr/bin/"
cp pyconverter/resources/icons/app_icon.svg "$APPDIR/usr/share/icons/hicolor/128x128/apps/pyconverter.svg"
cp pyconverter/resources/icons/app_icon.svg "$APPDIR/pyconverter.svg"

cat > "$APPDIR/pyconverter.desktop" << 'EOF'
[Desktop Entry]
Name=PyConverter
Comment=Universal file converter
Exec=pyconverter
Icon=pyconverter
Terminal=false
Type=Application
Categories=Utility;FileTools;
Keywords=convert;file;image;pdf;audio;video;
StartupWMClass=pyconverter
EOF

cat > "$APPDIR/AppRun" << 'SCRIPT'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/bin:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/pyconverter" "$@"
SCRIPT
chmod +x "$APPDIR/AppRun"

if command -v appimagetool &> /dev/null; then
    ARCH=x86_64 appimagetool "$APPDIR" "PyConverter-x86_64.AppImage"
    echo ""
    echo "Done! Output: PyConverter-x86_64.AppImage"
else
    echo ""
    echo "appimagetool not found. Install it:"
    echo "  wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    echo "  chmod +x appimagetool-x86_64.AppImage"
    echo "  sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool"
    echo ""
    echo "Portable output: dist/pyconverter/"
fi
