[Setup]
AppName=PyConverter
AppVersion=0.1.0
AppPublisher=Alessandro
DefaultDirName={autopf}\PyConverter
DefaultGroupName=PyConverter
UninstallDisplayIcon={app}\pyconverter.exe
OutputDir=output
OutputBaseFilename=PyConverter_Setup
Compression=lzma2
SolidCompression=yes
SetupIconFile=pyconverter\resources\icons\app_icon.ico
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Files]
Source: "dist\pyconverter\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs

[Icons]
Name: "{group}\PyConverter"; Filename: "{app}\pyconverter.exe"
Name: "{group}\Uninstall PyConverter"; Filename: "{uninstallexe}"
Name: "{commondesktop}\PyConverter"; Filename: "{app}\pyconverter.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Create desktop shortcut"; GroupDescription: "Additional shortcuts:"

[Run]
Filename: "{app}\pyconverter.exe"; Description: "Launch PyConverter"; Flags: nowait postinstall skipifsilent
