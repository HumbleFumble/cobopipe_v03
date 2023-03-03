# Install VRay
# ! From elevated prompt ! ("start pwsh -Credential "")
# It seems with open session from elevated propt installations go as anticipated

$creds = Get-Credential -UserName "cphbom\administrator"
$session = New-PSSession -ComputerName vm1 -Credential $creds


Invoke-Command -Session $session -ScriptBlock {

    New-PSDrive -Name "W" -Root "\\WSX3\shared" -PSProvider "FileSystem" -Credential $using:creds -Persist
    Set-ExecutionPolicy Bypass
    Start-Process -FilePath "\\WSX3\shared\VRay\installVray.cmd" -Wait
    Remove-PSDrive -Name "W"
    Set-ExecutionPolicy Restricted
} 



# Installing application. It appears that the application must have option for silent install to be installed remotely.
$creds = Get-Credential -UserName "network\admin"
$driveRoot = "\\driveroot\folder"
$driveName = "drive letter"
$computerName = 'computer name'
# Perhaps a loop here that iterates over a list of desired apps and sets the variables below

$appRelativePath = '\' + $apps['firefox']['path']
$installApp = $driveRoot + $appRelativePath
$appArgs = $apps['firefox']['args']

Invoke-Command -ComputerName $computerName -ScriptBlock {
    # Map the network share within PowerShell
    New-PSDrive -Name $using:driveName -Root $using:driveRoot -PSProvider "FileSystem" -Credential $using:creds -Persist
    Set-ExecutionPolicy Bypass
    # The arguments for launching the application are app-specific 
    Start-Process -FilePath $using:installApp -ArgumentList $using:appArgs -Wait
    # Remove the share
    Remove-PSDrive $using:driveName -Force
    Set-ExecutionPolicy Restricted
}

# Install V-Ray and Maya

$creds = Get-Credential -UserName "cphbom\administrator"
$session = New-PSSession -ComputerName vm1 -Credential $creds


Invoke-Command -Session $session -ScriptBlock {

    New-PSDrive -Name "W" -Root "\\WSX3\shared" -PSProvider "FileSystem" -Credential $using:creds -Persist
    Set-ExecutionPolicy Bypass
    Start-Process -FilePath "\\WSX3\shared\Maya2022extracted\Setup.exe" -ArgumentList "--silent" -Wait
    Start-Sleep 3
    Start-Process -FilePath "\\WSX3\shared\VRay\installVray.cmd" -ArgumentList "" -Wait
    Remove-PSDrive -Name "W"
} 

# Open session to remote computer and install applications from custom object

$computerName = 'vm1'
$driveRoot = "\\wsx3\shared"
$driveName = "W"

$creds = Get-Credential -UserName "cphbom\administrator"
# $session = New-PSSession -ComputerName $computerName -Credential $creds
do { # Try to open
    Start-Sleep -Milliseconds 300
    Write-Host "Connecting..."
# Remote session with appropriate name (computername/session/session number)
    $session = New-PSSession -ComputerName $computerName -Credential $creds
}until (
# Keep trying until it's been opened
    Get-PSSession
)
Write-Host "`nSuccessfully connected"

Invoke-Command -Session $session -ScriptBlock {

    New-PSDrive -Name $using:driveName -Root $using:driveRoot -PSProvider "FileSystem" -Credential $using:creds -Persist
    Set-ExecutionPolicy Bypass
    # Installing applications from custom object
    # This function installs a program with the parameters in a pscustomobject
    function Install-App {
        [CmdletBinding()]
        param ([PSCustomObject]$parameters)
    
        if (!($parameters.arguments)){
            Start-Process $parameters.path -Wait
        }
        else {
            Start-Process $parameters.path -ArgumentList $parameters.arguments -Wait
        }    
    }

    # Array of custom objects containing the application name, path to it and the arguments it should be run with, if any
    $apps = @(
        [pscustomobject]@{Name = "Maya 2022"; Path = "\\wsx3\shared\Maya2022extracted\Setup.exe"; Arguments = "--silent"}
        [pscustomobject]@{Name = "V-Ray"; Path = "\\wsx3\shared\VRay\installVray.cmd"; Arguments = ""}
    )

    # Loop over the array of custom objects
    foreach ($i in $apps){
        Install-App $i
        Start-Sleep 3
    }

    Remove-PSDrive -Name $using:driveName
    Set-ExecutionPolicy Restricted
} 

# Test connection to host
$list = "wsx2", "wsx11", "wsx19", "wsx24"
foreach ($i in $list){
    Write-Host "$($i) $((Test-Connection $i -Count 1).status)"
}





$creds = Get-Credential -UserName "cphbom\administrator"
$session1 = New-PSSession -ComputerName wsx22 -Credential $creds

Invoke-CommandAs -Session $session1 -ScriptBlock {
    $creds = Get-Credential -UserName "cphbom\administrator"
    New-PSDrive -Name "T" -Root "\\dumpap3\tools" -PSProvider "FileSystem" -Credential $creds -Persist
    if (Test-Path -Path "\\dumpap3\tools"){
    
    Set-ExecutionPolicy Bypass
    Set-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3' -Name 1806 -Value 0

    $pythoninstallpath = "\\dumpap3\tools\_Software\Python\python-3.9.1-amd64.exe"
    Start-Process $pythoninstallpath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -wait

    
    pwsh -command{
    $pythonpath = $null
    $envmachine = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine) -split ";"
    foreach($i in $envmachine){
        if ($i.Contains("Python") -and !($i.Contains("Scripts"))){
            $pythonpath = $i}
        }

    
    Start-Process $($pythonpath + '\python.exe') -ArgumentList "-m pip install --upgrade pip" -wait -NoNewWindow
    Start-Process $($pythonpath + '\Scripts\pip.exe') -ArgumentList "install pyside2" -wait -NoNewWindow
    Start-Process $($pythonpath + '\Scripts\pip.exe') -ArgumentList "install python_ffmpeg" -wait -NoNewWindow
    }

    Start-Process -FilePath "\\dumpap3\tools\_Software\Maya\Maya2022-4\Maya2022extracted\Setup.exe" -ArgumentList "--silent" -Wait
    Start-Sleep 3
    Start-Process -FilePath "\\dumpap3\tools\_Software\Chaosgroup\installVray.cmd" -Wait
    Remove-PSDrive -Name "T"
    Set-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3' -Name 1806 -Value 1
    Set-ExecutionPolicy Restricted}
    else {"Path is not valid"}
    
    Write-Host "Installation done"
    Start-Sleep 1
   
} -AsSystem


$CurrentTime = (get-date -format "hh:mm")
$Action = New-ScheduledTaskAction -Execute 'notepad.exe' -Argument '-NonInteractive -NoLogo -NoProfile'
$Trigger = New-ScheduledTaskTrigger -Once -At $CurrentTime
$Settings = New-ScheduledTaskSettingsSet
$Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings
Register-ScheduledTask -TaskName 'Run Notepad' -InputObject $Task -User "System"
Start-ScheduledTask -TaskName "Run Notepad"
Unregister-ScheduledTask -TaskName "Run Notepad" -Confirm:$false


# Local install 
#-------------------------------------------------------------------------------------------------------------------------

Set-ExecutionPolicy Bypass -Confirm:$False
$creds = Get-Credential -UserName cphbom\administrator
Set-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3' -Name 1806 -Value 0
if (Get-PSDrive -Name "T"){
    Write-Host "`nDrive found!"
}
else{
    New-PSDrive -Name "T" -PSProvider FileSystem -Root "\\dumpap3\tools" -Persist -Credential $creds
}
$pythonfilepath = "\\dumpap3\tools\_Software\Python\python-3.9.1-amd64.exe"
if (test-path $pythonfilepath){
    Write-Host "`nPython installation file found: $pythonfilepath"
    Write-Host "`nInstalling Python..."

Start-Process $pythonfilepath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait -ErrorAction SilentlyContinue
powershell -command {
    $pythonpath = $null
    $envmachine = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine) -split ";"
    foreach($i in $envmachine){
        if ($i.Contains("Python") -and !($i.Contains("Scripts"))){
            $pythonpath = $i
        }
    }

    Start-Process $($pythonpath + '\python.exe') -ArgumentList "-m pip install --upgrade pip" -wait -NoNewWindow
    Start-Process $($pythonpath + '\Scripts\pip.exe') -ArgumentList "install pyside2" -wait -NoNewWindow
    Start-Process $($pythonpath + '\Scripts\pip.exe') -ArgumentList "install python_ffmpeg" -wait -NoNewWindow
}

} else {
    Write-Host "Python installation file not found!"
}
Write-Host "`nInstalling Maya..."
Start-Process -FilePath "\\dumpap3\tools\_Software\Maya\Maya2022-4\Maya2022extracted\Setup.exe" -ArgumentList "--silent" -Wait
Start-Sleep 2

Write-Host "`nInstalling V-Ray..."
Start-Process -FilePath "\\dumpap3\tools\_Software\Chaosgroup\installVray.cmd" -Wait

Write-Host "Installing Harmony Toon Boom...`n"

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
    
Start-Process -FilePath "\\dumpap3\tools\_Software\Toonboom\HAR22-PRM-win-19025.exe" -ArgumentList '/s','/v"/qn"' -Wait

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

    foreach ($i in $shortCutArray){
        $parameters = $i
        Install-Shortcut $parameters
        }

Remove-PSDrive -Name "T" -Force
Set-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3' -Name 1806 -Value 1
Set-ExecutionPolicy Restricted







# Local install Python, Maya, V-Ray, Harmony
#-------------------------------------------------------------------------------------------------------------------------

Set-ExecutionPolicy Bypass -Confirm:$False

$path = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
New-ItemProperty -Path $path -Name 'ConsentPromptBehaviorAdmin' -Value 0 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'ConsentPromptBehaviorUser' -Value 3 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'EnableInstallerDetection' -Value 1 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'EnableLUA' -Value 1 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'EnableVirtualization' -Value 0 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'PromptOnSecureDesktop' -Value 0 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'ValidateAdminCodeSignatures' -Value 0 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'FilterAdministratorToken' -Value 0 -PropertyType DWORD -Force | Out-Null

$creds = Get-Credential -UserName cphbom\administrator

Set-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3' -Name 1806 -Value 0


if (Get-PSDrive -Name "T"){
    Write-Host "`nDrive found!"
}
else{
    New-PSDrive -Name "T" -PSProvider FileSystem -Root "\\dumpap3\tools" -Persist -Credential $creds
}
$pythonfilepath = "\\dumpap3\tools\_Software\Python\python-3.9.1-amd64.exe"
if (test-path $pythonfilepath){
    Write-Host "`nPython installation file found: $pythonfilepath"
    Write-Host "`nInstalling Python..."

Start-Process $pythonfilepath -ArgumentList "/quiet TargetDir=C:\Python39 InstallAllUsers=1 PrependPath=1 Include_test=0 " -Wait -ErrorAction SilentlyContinue
Start-Sleep 3
powershell -command {
	
    $pythonpath = $null
    $envmachine = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine) -split ";"
    foreach($i in $envmachine){
        if ($i.Contains("Python") -and !($i.Contains("Scripts"))){
            $pythonpath = $i
        }
    }

    Start-Process $($pythonpath + '\python.exe') -ArgumentList "-m pip install --upgrade pip" -wait -NoNewWindow
    Start-Process $($pythonpath + '\Scripts\pip.exe') -ArgumentList "install pyside2" -wait -NoNewWindow
    Start-Process $($pythonpath + '\Scripts\pip.exe') -ArgumentList "install ffmpeg-python" -wait -NoNewWindow
}

} else {
    Write-Host "Python installation file not found!"
}


Write-Host "`nInstalling Maya..."
Start-Process -FilePath "\\dumpap3\tools\_Software\Maya\Maya2022-4\Maya2022extracted\Setup.exe" -ArgumentList "--silent" -Wait
Start-Sleep 2

Write-Host "`nInstalling V-Ray..."
Start-Process -FilePath "\\dumpap3\tools\_Software\Chaosgroup\installVray.cmd" -Wait

Write-Host "`nInstalling Harmony Toon Boom...`n"

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
    
Start-Process -FilePath "\\dumpap3\tools\_Software\Toonboom\HAR22-PRM-win-19025.exe" -ArgumentList '/s','/v"/qn"' -Wait

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

    foreach ($i in $shortCutArray){
        $parameters = $i
        Make-Shortcut $parameters
        }

Remove-PSDrive -Name "T" -Force
Set-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3' -Name 1806 -Value 1

$path = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
New-ItemProperty -Path $path -Name 'ConsentPromptBehaviorAdmin' -Value 5 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'ConsentPromptBehaviorUser' -Value 3 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'EnableInstallerDetection' -Value 1 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'EnableLUA' -Value 1 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'EnableVirtualization' -Value 1 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'PromptOnSecureDesktop' -Value 1 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'ValidateAdminCodeSignatures' -Value 0 -PropertyType DWORD -Force | Out-Null
New-ItemProperty -Path $path -Name 'FilterAdministratorToken' -Value 0 -PropertyType DWORD -Force | Out-Null
Set-ExecutionPolicy Restricted

# check for other python 3 versions and remove them
# check and remove python_ffmpeg module

# install Pyside2 and ffmpeg-python on python 3.9

# change the env path from Harmony -> 21.1 to 22
# run update_harmony_hotbar.bat 
# copy launcher for harmony to the desktop
# copy preference folder from 21.1 and rename to 22 (%appdata%/Toonboom...)


# Uninstall Python 3.9.1
#------------------------------------------------------------------------------------------------------------------
$envmachine = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine) -split ";"
foreach($i in $envmachine){
    if ($i.Contains("Python")){
        $pythonpath = $i
    }

Remove-Item $i -Recurse
}

Get-CimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python ..... tcl*" | Invoke-CimMethod -MethodName Uninstall
Get-CimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python ..... pip*" | Invoke-CimMethod -MethodName Uninstall
Get-CimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python*" | Invoke-CimMethod -MethodName Uninstall

#------------------------------------------------------------------------------------------------------------------

# Scriptblock that runs on remote computer
$InstallScriptBlock = {
    
    # Web install PowerShell silent
    iex "& { $(irm https://aka.ms/install-powershell.ps1) } -UseMSI -quiet"
    
    # If $AtTime is not set above, it will be set with the current time 
    if (!$AtTime){
        $AtTime = $(Get-Date -Format HH:mm)
    }
    # List os custom objects, containing the parameters for each installer
    $parameters = @(
        [pscustomobject]@{PathToInstaller = "\\rs1\shared\Python\python-3.9.1-amd64.exe";TaskName = "Install Python";Arguments = "/quiet TargetDir=C:\Python39 InstallAllUsers=1 PrependPath=1 Include_test=0"},
        [pscustomobject]@{PathToInstaller = "\\rs1\shared\Firefox\firefox.exe";TaskName = "Install Firefox";Arguments = "/S"},
        [pscustomobject]@{PathToInstaller = "C:\Python39\python.exe";TaskName = "Upgrade Pip";Arguments = "-m pip install --upgrade pip"},
        [pscustomobject]@{PathToInstaller = "C:\Python39\Scripts\pip.exe";TaskName = "Install PySide2";Arguments = "install pyside2"},
        [pscustomobject]@{PathToInstaller = "C:\Python39\Scripts\pip.exe";TaskName = "Install FFMPEG";Arguments = "install ffmpeg-python"}
    )
    
    # Uninstall any previously installed Python version
    $python =  get-cimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python *"
    $python | Where-Object -Property name -Match "tcl*" | Invoke-CimMethod -MethodName Uninstall
    $python | Where-Object -Property name -Match "pip*" | Invoke-CimMethod -MethodName Uninstall
    $python | Where-Object -Property name -Match "python*" | Invoke-CimMethod -MethodName Uninstall -ErrorAction SilentlyContinue

    # Set up scheduled task for each set of parameters and run it
    #--------------------------------------------------------------------------------------------------------------------------------------------
    foreach ($p in $parameters){
        $Action = New-ScheduledTaskAction -Execute $p.PathToInstaller -Argument $p.Arguments 
        $Trigger = New-ScheduledTaskTrigger -Once -At $AtTime
        $Settings = New-ScheduledTaskSettingsSet
        $Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings
        Register-ScheduledTask -TaskName $p.TaskName -InputObject $Task -User 'System'
        Start-ScheduledTask -TaskName $p.TaskName
        Unregister-ScheduledTask -TaskName $p.TaskName -Confirm:$False
    }
    #--------------------------------------------------------------------------------------------------------------------------------------------

    # Run additional code
}

# List of computers to run scriptblock agains
$computerslist = "vm2", "vm3"

# Set time for the scheduled task to run. If no time is set, it will be executed immediatelly
$AtTime = $null

# Run the scriptblock on remote computer
Invoke-Command -ComputerName $computerslist -ScriptBlock $InstallScriptBlock

# Or use session to send the command 
# $creds = Get-Credential -UserName vmnet\admin
# $session = New-PSSession -ComputerName $computerslist -Credential $creds
# Invoke-Command -Session  $session -ScriptBlock $InstallScriptBlock



$exceplist = "wsx16", "wsx30", "wsx3", "wsx15", "wsx12", "wsx33"

$ComputersList = New-Object System.Collections.ArrayList
1..33 | ForEach-Object {$ComputersList += "wsx" + $_}
$newlist = foreach ($i in $ComputersList){Get-HostInfo -ComputerName $i -IPAddress -CurrentUser -WinRMStatus }

foreach ($item in $exceplist){
    foreach($pso in $newlist){
        if ($pso.name -eq $item){
            $newlist.Remove($pso)
        }
    }
}
$newlist


