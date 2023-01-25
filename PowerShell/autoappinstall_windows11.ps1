#------------------------------------------------------------------------------------------------------------------
#   Software Auto-Install PowerShell script
#------------------------------------------------------------------------------------------------------------------

# The purpose of this script is to automatically install predetermined additional software on a freshly installed Windows operating system, via PowerShell,
# with the minimum of user input, thus saving time. The script would install either specific, or the latest version of a given software.  
# For the specific version software, the script reads file paths from a folder, which is currently set to read from "C:\Users\whateveruser\Desktop\AutoInstallPack". 
# This means that the folder (currently called "AutoInstallPack") needs to be copied to the desktop of the machine, for which the install is intended, 
# before the script is ran. The script will install the package managers first (Chocolatey and WinGet). These download and install software of which the latest version 
# (or no specific version) is needed. Of course, all the software can be downloaded in advance and installed from a folder, but this increases the copy time; 
# also installing via package manager ensures the latest version is used. 	          
# The paths to the installation files are stored in a xml file, named "installConfig.xml" located in \AutoInstallPack\config. When adding new entries in the  file, 
# the easiest will be to add them at the end, since this ensures the correct enumeration. 


#-------------------------------------------------------------------------------------------------------------------
# Importing libraries. These libraries are necessary for the sendkeys to work.
#-------------------------------------------------------------------------------------------------------------------

Add-Type -AssemblyName Microsoft.VisualBasic
Add-Type -AssemblyName System.Windows.Forms

#-------------------------------------------------------------------------------------------------------------------
# $PackFolder variable is where the script would exepect to find the installation pack. 
# If different location for the instalation pack is chosen, this variable needs to be updated for the script to work
#-------------------------------------------------------------------------------------------------------------------

$PackFolder = "C:\Users\$env:USERNAME\Desktop" 

#-------------------------------------------------------------------------------------------------------------------
# Installation pack folder name. Update this variable
#-------------------------------------------------------------------------------------------------------------------

$packFolderName = "\AutoInstallPack\"
$installPackFolder = $PackFolder + $packFolderName

[xml]$applist = Get-Content ($installPackFolder + "config\installConfig.xml")
[xml]$paths = Get-Content ($installPackFolder + "config\variablePaths.xml")

#-------------------------------------------------------------------------------------------------------------------
# Decalring variables for the Check-Install function. The installLog global variable stores the reslut from the function 
# and will comprise the body for the email, if email is being sent. The function takes single parameter and looks for 
# match in the list of programs that winget recognizes as valid installed packages. This is not the most precise method,
# but is the most flexible.
# ------------------------------------------------------------------------------------------------------------------

$global:installLog = $null
$result = $null

function Check-Install {

    param (
        [string]$package
    )

    $installations = winget list

    if ($installations -match "$package*"){$result = $package + " successfully installed!"}
    else {$result = $package + " not found!"}

    $result + "`n"
    $global:installLog += $result + "`n"

}


### ---------------------- OPEN REMOTE SESSION --------------------------###

### $username = "machinename\username"
### $computername = "computername"
### $creds = Get-Credential -UserName $username
### $session = New-PSSession -ComputerName $computername -Credential $creds

###-----------------------------------------------------------------------###



#-------------------------------------------------------------------------------------------------------------------
# Start log. This command will capture console output into a file on the desktop
#-------------------------------------------------------------------------------------------------------------------

Start-Transcript -path C:\Users\$env:USERNAME\Desktop\autoInstallLog.txt -append


Write-Host 
"###-------------------------------------------------------------------------------###
###----------------- Initializing Multi-Package Installation ---------------------###
###-------------------------------------------------------------------------------###`n"

$prompt = Read-Host -Prompt "Send instalation log to email? [Y/N]"

if($prompt -eq "Y"){

    $EmailFrom = Read-Host -Prompt “Enter your email”
    $EmailTo = Read-Host -Prompt “Send email to”
    $creds = Get-Credential -UserName $EmailFrom
    $Subject = “Installation log”
    }

#------------------------------------------------------------------------------------------------------------------------
# This command sets the execution policy to "BYPASS", which allows for the script to run. The defaul policy is "Restricted",
# which doesn't allow any PowerShell scripts to be executed on the system. At the end of the script, the policy is changed 
# back to "RESTRICTED". Execution policies are in place for protecting the system from being compromised.
#------------------------------------------------------------------------------------------------------------------------

Set-ExecutionPolicy Bypass -Scope Process -Force 


#-----------------------------------------------------------------------------------------#
# NuGet # This package is necessary for Chocolatey to run
#-----------------------------------------------------------------------------------------#


Install-PackageProvider -Name NuGet -MinimumVersion 2.8.5.201 -Force

#-----------------------------------------------------------------------------------------#
# Chocolatey # This installs Chocolatey package manager
#-----------------------------------------------------------------------------------------#


[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; 
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

Start-Sleep 5

#-----------------------------------------------------------------------------------------#
# DotNet, VClibs and WinGet installs - these are necessary for WinGet to run
#-----------------------------------------------------------------------------------------#

choco install dotnet-6.0-sdk -y
Import-Module PackageManagement
Add-AppPackage -Path ($installPackFolder + "Microsoft.UI.Xaml.2.6_2.62112.3002.0_x64__8wekyb3d8bbwe.appx")
Add-AppxPackage -Path ($installPackFolder + "Microsoft.VCLibs.x64.14.00.Desktop.appx")

#-----------------------------------------------------------------------------------------#
# This installs Windows package manager (WinGet)
#-----------------------------------------------------------------------------------------#

Add-AppPackage -Path ($installPackFolder + $applist.ChildNodes.app[0].Path)
Install-Module -Name WinGet -Force
Start-Process -FilePath ($installPackFolder + $applist.AppList.App[0].Path) -ArgumentList "-SkipLicense"
Start-Sleep -Seconds 1
[System.Windows.Forms.SendKeys]::SendWait("{TAB}")
Start-Sleep -Seconds 1
[System.Windows.Forms.SendKeys]::SendWait("{ENTER}")
Get-Process -name "AppInstaller" | Wait-Process
Start-Sleep 5
    
    if (Get-Process -Name "AppInstaller") {Stop-Process -name "AppInstaller"}
Start-Sleep 1

#-----------------------------------------------------------------------------------------#
# Python #
# This section installs Python 3.9.1, upgrades pip, and installs PySide2 and FFMPEG
# The "wait" switch ensures that the instalation is completed, before the script continues
# The "NoNewWindow" switch ensures the output is diplayed in the same window. Typically,
# "Start-Process" will open a new console window. 
# The modules are installed with the full path, since there is no easy way to update the 
# system "Path" variable with the Python paths (which are necessary for the modules to be installed),
# without restarting the PowerShell console. 
#-----------------------------------------------------------------------------------------#

$pythonfilepath = $installPackFolder + $applist.ChildNodes.app[1].Path
Start-Process -FilePath $pythonfilepath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait -NoNewWindow

Start-Process -FilePath "C:\Program Files\Python39\python.exe" -ArgumentList "-m pip install --upgrade pip" -wait -NoNewWindow 
Start-Process -FilePath "C:\Program Files\Python39\Scripts\pip.exe" -ArgumentList "install pyside2" -wait -NoNewWindow
Start-Process -FilePath "C:\Program Files\Python39\Scripts\pip.exe" -ArgumentList "install python_ffmpeg" -NoNewWindow

Start-Sleep 3

if(Get-Process "winget"){Stop-Process -Name "winget"} 

#-----------------------------------------------------------------------------------------#
# WinRar #
# WinRar is used to unpack Maya archive, which was created, because there is no automate the 
# archived downloadable version. It has been unpacked and archived again, which allows for 
# automating the process (unpacking and installing)
#-----------------------------------------------------------------------------------------#

winget install RARLab.WinRAR -h --accept-source-agreements --accept-package-agreements 
Start-Sleep 3
Check-Install "WinRar"

#-----------------------------------------------------------------------------------------#
# Variables set
#-----------------------------------------------------------------------------------------#

[Environment]::SetEnvironmentVariable("Path", ($env:Path += $paths.VariablesList.Variable[0].Path), [EnvironmentVariableTarget]::Machine)
Write-Host "WinRar variable set!`n"
[Environment]::SetEnvironmentVariable("Path", ($env:Path += $paths.VariablesList.Variable[1].Path), [EnvironmentVariableTarget]::Machine)
Write-Host "PHP variable set!`n"
[Environment]::SetEnvironmentVariable("Path", ($env:Path += $paths.VariablesList.Variable[2].Path), [EnvironmentVariableTarget]::Machine)
Write-Host "Yeti variable set!`n"


#-----------------------------------------------------------------------------------------#
# Maya #
#-----------------------------------------------------------------------------------------#


$launchmaya = $installPackFolder + "Launch_maya.BAT"
Copy-Item -Path $launchmaya -Destination $PackFolder
New-Item -Path "C:\Temp" -ItemType Directory          # Creating "C:\Path" folder
Write-Host "Unzipping Maya...`n"
unrar x -y ($installPackFolder + $applist.ChildNodes.app[2].Path) "$installPackFolder" | Out-Null
Write-Host "Installing Maya...`n"
Start-Process -FilePath ($installPackFolder + $applist.ChildNodes.app[3].Path) -ArgumentList "--silent" 


# This loop checks continuously if maya.exe has been created (meaning it has been installed)
# making sure that the script only continues if Maya has been installed

do {    
 
    if (Test-Path "C:\Program Files\Autodesk\Maya2020\bin\maya.exe"){$t = $true}
  }while($t -ne $true)

 while(!(winget list "Autodesk Maya 2020")){Start-Sleep -Milliseconds 100}
 
 
#-----------------------------------------------------------------------------------------#
# V-Ray #
# V-Ray uses a xml file for unattended install. Check website for instructions on creating 
# the xml. Unfortunatelly it won't work with UNC paths (it won't install from network location)
#-----------------------------------------------------------------------------------------#

Write-Host "Installing V-Ray...`n"
Start-Process -FilePath ($installPackFolder + $applist.ChildNodes.app[4].Path) -ArgumentList "-gui=0 -configFile=C:\Users\$env:USERNAME\Desktop\AutoInstallPack\config\VRayConfig.xml -quiet=1 -auto" -Wait
Start-Sleep 3
Check-Install "Maya 2020"
Check-Install "V-Ray"


#-----------------------------------------------------------------------------------------#
# Creative Cloud #
#-----------------------------------------------------------------------------------------#

Write-Host "Installing Creative Cloud...`n"
Start-Process -FilePath ($installPackFolder + $applist.ChildNodes.App[5].Path) -ArgumentList "--silent" -Wait

Check-Install "After Effects"
Check-Install "Media Encoder"
Check-Install "Premier"
Check-Install "Photoshop"
Start-Sleep 3


#-----------------------------------------------------------------------------------------#
# Harmony #
#-----------------------------------------------------------------------------------------#

Write-Host "Installing Harmony Toon Boom...`n"

function Make-Shortcut {
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
    
Start-Process -FilePath ($installPackFolder + $applist.ChildNodes.App[6].Path) -ArgumentList '/s','/v"/qn"' -Wait

    #----------------------------------------------------------------------------------------------------------
    # Create necessary directories
    #----------------------------------------------------------------------------------------------------------

    New-Item -Path "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Harmony 21 Premium" -ItemType Directory -Name "Documentation"
    New-Item -Path "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Harmony 21 Premium" -ItemType Directory -Name "Tools"
    
    #----------------------------------------------------------------------------------------------------------
    # Create PSCustomObject with all shortcuts that need to be created and feed it as argument to the function
    #----------------------------------------------------------------------------------------------------------
    
    $startmenu = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Harmony 21 Premium"
    $installfolder = "C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 21 Premium"
    
    $shortCutArray = @(
            [pscustomobject]@{FilePath = $installfolder + "\win64\bin\wstart.exe"; shortCutFolder = "C:\Users\Public\Desktop"; shortCutName = "Harmony 21.1 Premium"; Arguments = "HarmonyPremium.exe"; IconLocation = $installfolder + "\win64\bin\HarmonyPremium.ico"}
            [pscustomobject]@{FilePath = $installfolder + "\win64\bin\wstart.exe"; shortCutFolder = $startmenu; shortCutName = "Control Center"; Arguments = "ControlCenter.exe"; IconLocation = $installfolder + "\win64\bin\ControlCenter.ico"}
            [pscustomobject]@{FilePath = $installfolder + "\win64\bin\wstart.exe"; shortCutFolder = $startmenu; shortCutName = "Harmony 21.1 Premium"; Arguments = "HarmonyPremium.exe"; IconLocation = $installfolder + "\win64\bin\HarmonyPremium.ico"}
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

Check-Install "Harmony"


#-----------------------------------------------------------------------------------------#
# PowerShell #
#-----------------------------------------------------------------------------------------#

winget install Microsoft.PowerShell -h --accept-source-agreements --accept-package-agreements 

Check-Install "Powershell 7-x64"
Start-Sleep -Seconds 2


#-----------------------------------------------------------------------------------------#
# VLC Player #
#-----------------------------------------------------------------------------------------#

winget install vlc --source winget
Check-Install "VLC"
Start-Sleep 3


#-----------------------------------------------------------------------------------------#
# Chrome #
#-----------------------------------------------------------------------------------------#

choco install GoogleChrome -y
Check-Install "Google Chrome"
Start-Sleep 3


#-----------------------------------------------------------------------------------------#
# FireFox #
#-----------------------------------------------------------------------------------------#

winget install Mozilla.Firefox
Check-Install "Mozilla"
Start-Sleep 3

#-----------------------------------------------------------------------------------------#
# QuickTime #
#-----------------------------------------------------------------------------------------#

choco install QuickTime -y
Check-Install "QuickTime"
Start-Sleep 3
#-----------------------------------------------------------------------------------------#
# Acrobat Reader #
#-----------------------------------------------------------------------------------------#

winget install "Adobe Acrobat Reader DC (64-bit)" -h --accept-source-agreements --accept-package-agreements 
Check-Install "Adobe Acrobat"
Start-Sleep 3

   
#-----------------------------------------------------------------------------------------#
# PHP #
#-----------------------------------------------------------------------------------------#

if ((Test-Path -Path "C:\php") -eq $false){
    
    Copy-Item -Path ($installPackFolder + "php") -Destination "C:\" -Recurse
    Write-Host "PHP folder copied to C:\ drive!"
}


#-----------------------------------------------------------------------------------------#
# Windows Update via Powershell #
#-----------------------------------------------------------------------------------------#

Write-Host "Instaling Windows updates...`n"
$version = (Find-Module PSWindowsUpdate).version
Install-Module -Name PSWindowsUpdate -RequiredVersion $version -Force
Get-WindowsUpdate -Install -AcceptAll -IgnoreReboot 


#-----------------------------------------------------------------------------------------#
# Send an email note #
#-----------------------------------------------------------------------------------------#

if ($EmailFrom -ne $null){

    [string]$date = Get-Date
    $Body = $date + "`n`n`n" + $global:installLog
    $SMTPServer = “smtp.office365.com”
    $SMTPClient = New-Object Net.Mail.SmtpClient($SmtpServer, 587)
    $SMTPClient.EnableSsl = $true
    $SMTPClient.Credentials = New-Object System.Net.NetworkCredential($creds.UserName, $creds.Password)
    $SMTPClient.Send($EmailFrom, $EmailTo, $Subject, $Body)
    $SMTPClient.Dispose()
}
#-----------------------------------------------------------------------------------------#

Write-Host 
"###-------------------------------------------------------------------------------###
###------------------------------- Installation Done! ----------------------------###
###-------------------------------------------------------------------------------###`n"

$installLog


Write-Host "Rebooting..."
Set-ExecutionPolicy Restricted -Force
Stop-Transcript
Start-Sleep 5
Restart-Computer -Force
