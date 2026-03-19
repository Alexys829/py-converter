#!/bin/bash
set -e

echo "=== PyConverter - Linux Build ==="
echo ""

# Activate venv
source .venv/bin/activate

# Build with Nuitka
echo "Building with Nuitka (this may take a few minutes)..."
python -m nuitka \
    --jobs=8 \
    --standalone \
    --onefile \
    --enable-plugin=pyside6 \
    --include-package=pyconverter \
    --include-data-dir=pyconverter/resources=pyconverter/resources \
    --nofollow-import-to=pymupdf \
    --nofollow-import-to=fitz \
    --nofollow-import-to=pandas \
    --output-filename=PyConverter \
    main.py

echo ""
echo "Build complete!"

# Create AppImage structure
echo "Creating AppImage..."

APPDIR="PyConverter.AppDir"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/icons/hicolor/128x128/apps"

# Copy binary
cp PyConverter "$APPDIR/usr/bin/"

# Copy icon
cp pyconverter/resources/icons/app_icon.svg \
   "$APPDIR/usr/share/icons/hicolor/128x128/apps/pyconverter.svg"
cp pyconverter/resources/icons/app_icon.svg "$APPDIR/pyconverter.svg"

# Desktop entry
cat > "$APPDIR/pyconverter.desktop" << 'DESKTOP'
[Desktop Entry]
Name=PyConverter
Comment=Universal file converter
Exec=PyConverter
Icon=pyconverter
Terminal=false
Type=Application
Categories=Utility;FileTools;
Keywords=convert;file;image;pdf;audio;video;
DESKTOP

# AppRun
cat > "$APPDIR/AppRun" << 'APPRUN'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
exec "${HERE}/usr/bin/PyConverter" "$@"
APPRUN
chmod +x "$APPDIR/AppRun"

# Build AppImage
if command -v appimagetool &> /dev/null; then
    appimagetool "$APPDIR" "PyConverter-x86_64.AppImage"
    echo ""
    echo "Done! Output: PyConverter-x86_64.AppImage"
else
    echo ""
    echo "appimagetool not found. Install it to create AppImage:"
    echo "  wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
    echo "  chmod +x appimagetool-x86_64.AppImage"
    echo "  sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool"
    echo ""
    echo "Standalone binary is available at: ./PyConverter"
fi
