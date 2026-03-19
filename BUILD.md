# Build Instructions

## Prerequisites (all platforms)

- Python 3.10+
- pip

## Windows

### Option A: Nuitka (recommended, produces native .exe)

```powershell
# Install dependencies
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
pip install nuitka ordered-set

# Build (uses build_windows.bat)
.\build_windows.bat
```

Output: `PyConverter.exe` (single file, ~80-120 MB)

Nuitka will automatically download MinGW64 compiler on first run.
Alternatively, install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

### Option B: PyInstaller

```powershell
pip install pyinstaller
pyinstaller pyconverter.spec
```

Output: `dist/pyconverter/pyconverter.exe` (folder with exe + DLLs)

To create a single-file exe, add `--onefile` flag or modify the spec.

---

## Linux

### Run from source

```bash
git clone https://github.com/YOUR_USERNAME/pyconverter.git
cd pyconverter
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Desktop entry (menu integration)

```bash
# Edit pyconverter.desktop to fix paths, then:
cp pyconverter.desktop ~/.local/share/applications/
```

### AppImage

1. Install [appimagetool](https://github.com/AppImage/appimagetool/releases):

```bash
wget https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage
sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool
```

2. Create AppDir structure:

```bash
# Install PyInstaller and build first
pip install pyinstaller
pyinstaller pyconverter.spec

# Create AppDir
mkdir -p PyConverter.AppDir/usr/bin
mkdir -p PyConverter.AppDir/usr/share/icons/hicolor/128x128/apps
mkdir -p PyConverter.AppDir/usr/share/applications

# Copy built files
cp -r dist/pyconverter/* PyConverter.AppDir/usr/bin/

# Copy icon
cp pyconverter/resources/icons/app_icon.svg \
   PyConverter.AppDir/usr/share/icons/hicolor/128x128/apps/pyconverter.svg

# Create .desktop inside AppDir
cat > PyConverter.AppDir/pyconverter.desktop << 'EOF'
[Desktop Entry]
Name=PyConverter
Comment=Universal file converter
Exec=pyconverter
Icon=pyconverter
Terminal=false
Type=Application
Categories=Utility;FileTools;
EOF

# Create AppRun
cat > PyConverter.AppDir/AppRun << 'SCRIPT'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/bin:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/pyconverter" "$@"
SCRIPT
chmod +x PyConverter.AppDir/AppRun

# Build AppImage
appimagetool PyConverter.AppDir PyConverter-x86_64.AppImage
```

Output: `PyConverter-x86_64.AppImage` (single file, ~100-150 MB)

### DEB Package

1. Build with PyInstaller first (see above)

2. Create deb structure:

```bash
# Create directory structure
mkdir -p pyconverter-deb/DEBIAN
mkdir -p pyconverter-deb/usr/bin
mkdir -p pyconverter-deb/usr/share/applications
mkdir -p pyconverter-deb/usr/share/icons/hicolor/128x128/apps
mkdir -p pyconverter-deb/opt/pyconverter

# Copy built files
cp -r dist/pyconverter/* pyconverter-deb/opt/pyconverter/

# Create launcher script
cat > pyconverter-deb/usr/bin/pyconverter << 'EOF'
#!/bin/bash
exec /opt/pyconverter/pyconverter "$@"
EOF
chmod +x pyconverter-deb/usr/bin/pyconverter

# Copy icon
cp pyconverter/resources/icons/app_icon.svg \
   pyconverter-deb/usr/share/icons/hicolor/128x128/apps/pyconverter.svg

# Create .desktop
cat > pyconverter-deb/usr/share/applications/pyconverter.desktop << 'EOF'
[Desktop Entry]
Name=PyConverter
Comment=Universal file converter
Exec=pyconverter
Icon=pyconverter
Terminal=false
Type=Application
Categories=Utility;FileTools;
Keywords=convert;file;image;pdf;audio;video;
EOF

# Create control file
cat > pyconverter-deb/DEBIAN/control << EOF
Package: pyconverter
Version: 0.1.0
Section: utils
Priority: optional
Architecture: amd64
Maintainer: Alessandro
Description: PyConverter - Universal file converter
 Cross-platform file converter supporting images, documents,
 data files, audio, video, and PDF tools.
 Features drag & drop, batch conversion, Material Design UI.
EOF

# Build .deb
dpkg-deb --build pyconverter-deb pyconverter_0.1.0_amd64.deb
```

Output: `pyconverter_0.1.0_amd64.deb`

Install with: `sudo dpkg -i pyconverter_0.1.0_amd64.deb`

### Nuitka (Linux)

```bash
pip install nuitka ordered-set
python -m nuitka \
    --standalone \
    --onefile \
    --enable-plugin=pyside6 \
    --include-package=pyconverter \
    --include-data-dir=pyconverter/resources=pyconverter/resources \
    --output-filename=PyConverter \
    main.py
```

Output: `PyConverter` (single binary, ~80-120 MB)

---

## Notes

- **ffmpeg is bundled** via `imageio-ffmpeg` - no system install needed
- Windows builds require building **on** Windows (no cross-compilation)
- Linux builds require building **on** Linux
- Nuitka produces faster, smaller executables than PyInstaller
- For smallest size, use `--onefile` (Nuitka) or modify the spec (PyInstaller)
