; Inno Setup скрипт для ChatList
; Автоматически сгенерирован из version.py

#define MyAppName "ChatList"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "ChatList"
#define MyAppURL "https://github.com/chatlist"
#define MyAppExeName "ChatListApp-1.0.0.exe"
#define MyAppId "{{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}}"

[Setup]
; Примечание: значение AppId используется для идентификации приложения.
; Не используйте тот же AppId в других установщиках.
; (Чтобы создать новый идентификатор, нажмите Ctrl+G в Inno Setup)
AppId={{MyAppId}}
AppName={{MyAppName}}
AppVersion={{MyAppVersion}}
;AppVerName={{MyAppName}} {{MyAppVersion}}
AppPublisher={{MyAppPublisher}}
AppPublisherURL={{MyAppURL}}
AppSupportURL={{MyAppURL}}
AppUpdatesURL={{MyAppURL}}
DefaultDirName={{autopf}}\{{MyAppName}}
DefaultGroupName={{MyAppName}}
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=installer
OutputBaseFilename=ChatList-Setup-1.0.0
SetupIconFile=app.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{{cm:CreateQuickLaunchIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
Source: "dist\ChatListApp-1.0.0.exe"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "app.ico"; DestDir: "{{app}}"; Flags: ignoreversion
; Примечание: не используйте "Flags: ignoreversion" для любых общих системных файлов

[Icons]
Name: "{{group}}\{{MyAppName}}"; Filename: "{{app}}\{{MyAppExeName}}"; IconFilename: "{{app}}\app.ico"
Name: "{{group}}\{{cm:UninstallProgram,{{MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{autodesktop}}\{{MyAppName}}"; Filename: "{{app}}\{{MyAppExeName}}"; Tasks: desktopicon; IconFilename: "{{app}}\app.ico"
Name: "{{userappdata}}\Microsoft\Internet Explorer\Quick Launch\{{MyAppName}}"; Filename: "{{app}}\{{MyAppExeName}}"; Tasks: quicklaunchicon; IconFilename: "{{app}}\app.ico"

[Run]
Filename: "{{app}}\{{MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{{app}}\*"
Type: dirifempty; Name: "{{app}}"

[UninstallRun]
; Здесь можно добавить дополнительные команды, выполняемые при удалении
; Например, удаление файлов конфигурации пользователя, логов и т.д.
; Filename: "{{sys}}\taskkill.exe"; Parameters: "/F /IM {MyAppExeName}"; Flags: runhidden skipifdoesntexist

[Code]
; Дополнительный код для кастомных действий при установке/удалении
procedure InitializeUninstallProgressForm();
begin
  ; Можно добавить кастомные действия при удалении
end;
