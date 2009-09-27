; -- inst_grid.iss --
; Demonstrates copying 3 files and creating an icon.

; SEE THE DOCUMENTATION FOR DETAILS ON CREATING .ISS SCRIPT FILES!

[Setup]
AppName=Gridzilla
AppVerName=Gridzilla Version 0.2 Beta
DefaultDirName={pf}\Gridzilla
DefaultGroupName=Gridzilla
UninstallDisplayIcon={app}\icons\gzilla_ico_dark.ico
Compression=lzma
SolidCompression=true
OutputDir=.\
WizardImageBackColor=clGreen
SetupIconFile=gzilla_ico_dark.ico

[Files]
Source: .\dist\gzilla.exe; DestDir: {app}\bin
Source: .\dist\*.pyd; DestDir: {app}\bin
Source: *.dll; DestDir: {app}\bin
Source: .\dist\*.dll; DestDir: {app}\bin
Source: .\dist\library.zip; DestDir: {app}\bin
Source: gzilla_ico_dark.ico; DestDir: {app}\icons
Source: gzilla_uninstall_ico_fin.ico; DestDir: {app}\icons
Source: crystalcomponent.csv; DestDir: {app}\Examples

[Icons]
Name: {group}\Gridzilla; Filename: {app}\bin\gzilla.exe; IconFilename: {app}\icons\gzilla_ico_dark.ico
;Name: {commonstartup}\Gridzilla; Filename: {app}\bin\gzilla.exe; IconFilename: {app}\icons\gzilla_ico_dark.ico
Name: {commonprograms}\Gridzilla; Filename: {app}\bin\gzilla.exe; IconFilename: {app}\icons\gzilla_ico_dark.ico
Name: {commondesktop}\Gridzilla; Filename: {app}\bin\gzilla.exe; IconFilename: {app}\icons\gzilla_ico_dark.ico
Name: "{group}\Uninstall Gridzilla"; Filename: "{uninstallexe}"; IconFilename: {app}\icons\gzilla_uninstall_ico_fin.ico

;[Registry]
;Root: HKCU ; Subkey: "Environment"; ValueType: string; ValueName: "GZILLADIR"; ValueData: "C:\Program Files\Gridzilla"; Flags: uninsdeletekey
