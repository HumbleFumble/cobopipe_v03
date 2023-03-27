# Set temporarily admnistrator check (UAC) to none
Set-UAC -Off

# Script parameters. $AtTime can be used to install Python at given time. Use as script parameter to set scheduled time
param (
    [string]$AtTime,
    [string]$user = (whoami.exe)
)

if (! ($AtTime)){
    $AtTime = Get-Date -Format "HH:mm"
}else{
    if (! ($AtTime -match "\d\d:\d\d")){
    Write-Output "`nPlease enter time in the following format: `"HH:mm`""
    break
    }
}


function Install-Shortcut {
    [CmdletBinding()]
    param (
        [PSCustomObject]$parameters
    )

$fileName = $parameters.FilePath.Substring($parameters.FilePath.LastIndexOf("\") + 1)
$shortcutPath = $parameters.ShortcutFolder + "\" + $parameters.ShortcutName + '.lnk'

if ($shortcutPath | Out-String -Stream | Select-String -Pattern 'Desktop'){$workdir = "C:\Users\Public\Desktop"}
else {$workdir = $parameters.FilePath -replace '$fileName' -replace ""}

# This section of the function creates the shorcut and is fed by the parameter
$WScriptObj = New-Object -ComObject ("WScript.Shell")
$shortcut = $WscriptObj.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $parameters.FilePath
$shortcut.Arguments = $parameters.Arguments
$shortcut.WorkingDirectory = $workdir
$shortcut.IconLocation = $parameters.IconLocation
$shortcut.Save()
}


Install-App -PathToInstaller "\\dumpap3\tools\_Software\Toonboom\HAR22-PRM-win-19025.exe" -Arguments '/S /v"/qn"' -TaskName "Harmony" 

#----------------------------------------------------------------------------------------------------------
# Create necessary directories
#----------------------------------------------------------------------------------------------------------

New-Item -Path "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Harmony 22 Premium" -ItemType Directory -Name "Documentation"
New-Item -Path "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Harmony 22 Premium" -ItemType Directory -Name "Tools"

#----------------------------------------------------------------------------------------------------------
# Create PSCustomObject with all shortcuts that need to be created and feed it as argument to the function
#----------------------------------------------------------------------------------------------------------

$startmenu = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Harmony 22 Premium"
$installfolder = "C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium"

$shortCutArray = @(
        [pscustomobject]@{FilePath = $installfolder + "\win64\bin\wstart.exe"; shortCutFolder = "C:\Users\Public\Desktop"; shortCutName = "Harmony 22 Premium"; Arguments = "HarmonyPremium.exe"; IconLocation = $installfolder + "\win64\bin\HarmonyPremium.ico"}
        [pscustomobject]@{FilePath = $installfolder + "\win64\bin\wstart.exe"; shortCutFolder = $startmenu; shortCutName = "Control Center"; Arguments = "ControlCenter.exe"; IconLocation = $installfolder + "\win64\bin\ControlCenter.ico"}
        [pscustomobject]@{FilePath = $installfolder + "\win64\bin\wstart.exe"; shortCutFolder = $startmenu; shortCutName = "Harmony 22 Premium"; Arguments = "HarmonyPremium.exe"; IconLocation = $installfolder + "\win64\bin\HarmonyPremium.ico"}
        [pscustomobject]@{FilePath = $installfolder + "\win64\bin\wstart.exe"; shortCutFolder = $startmenu; shortCutName = "Paint"; Arguments = "HarmonyPremium.exe -paint"; IconLocation = $installfolder + "\win64\bin\HarmonyPremiumPaint.ico"}
        [pscustomobject]@{FilePath = $installfolder + "\win64\bin\wstart.exe"; shortCutFolder = $startmenu; shortCutName = "Play"; Arguments = "Play.exe"; IconLocation = $installfolder + "\win64\bin\HarmonyPlay.ico"}
        [pscustomobject]@{FilePath = $installfolder + "\win64\bin\wstart.exe"; shortCutFolder = $startmenu; shortCutName = "Scan"; Arguments = "Scan.exe -indirect"; IconLocation = $installfolder + "\win64\bin\Scan.ico"}
        [pscustomobject]@{FilePath = $installfolder + "\win64\bin\ConfigEditor.exe"; shortCutFolder = $startmenu + "\Tools"; shortCutName = "Configuration Editor"; Arguments = ""; IconLocation = $installfolder + "\win64\bin\ConfigEditor.ico"}
        [pscustomobject]@{FilePath = $installfolder + "\win32\bin\ConfigWizard.exe"; shortCutFolder = $startmenu + "\Tools"; shortCutName = "Configuration Wizard"; Arguments = ""; IconLocation = $installfolder + "\win32\bin\ConfigWizard.ico"}
        [pscustomobject]@{FilePath = $installfolder + "\win32\bin\Toon Boom Harmony Control Panel.exe"; ShortCutFolder = $startmenu + "\Tools"; shortCutName = "Control Panel"; Arguments = ""; IconLocation = $installfolder + "\win32\bin\ControlPanel.ico"}
        [pscustomobject]@{FilePath = $installfolder + "\win64\bin\ServiceLauncher.exe"; shortCutFolder = $startmenu + "\Tools"; shortCutName = "Service Launcher"; Arguments = ""; IconLocation = $installfolder + "\win64\bin\tbservicelauncher.ico"}
        [pscustomobject]@{FilePath = $installfolder + "\help\en\Toon_Boom_Harmony_Getting_Started_Guide.pdf"; shortCutFolder = $startmenu + "\Documentation"; shortCutName = "Harmony Getting Started Guide"; Arguments = ""; IconLocation = ""}
    )

#----------------------------------------------------------------------------------------------------------
# Loop through the PSCustomObject to create each shorcut
#----------------------------------------------------------------------------------------------------------

foreach ($i in $ShortCutArray){
    $parameters = $i
    Install-Shortcut $parameters
    }

# Set UAC back to normal
Set-UAC -On