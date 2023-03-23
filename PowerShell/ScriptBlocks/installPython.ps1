# Set temporarily admnistrator check (UAC) to none
Set-SecurityLevel -Low

# Script parameters. $AtTime can be used to install Python at given time. Use as script parameter to set scheduled time
param (
    [string]$AtTime
)

# Set time for the installation (the code below gets the current time and runs the installation immediatelly)
if (! ($AtTime)){
    $AtTime = Get-Date -Format "HH:mm"
}else{
    if (! ($AtTime -match "\d\d:\d\d")){
    Write-Output "`nPlease enter time in the following format: `"HH:mm`""
    break
    }
}

# Uninstall any previously installed Python version
$python =  Get-CimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python *"
if ($python){
    Write-Output "`nPython installation found, uninstalling"
    $python | Where-Object -Property Name -Match "python ..... tcl*" | Invoke-CimMethod -MethodName Uninstall
    $python | Where-Object -Property Name -Match "python ..... pip*" | Invoke-CimMethod -MethodName Uninstall
    $python | Where-Object -Property Name -Match "python *" | Invoke-CimMethod -MethodName Uninstall -ErrorAction SilentlyContinue
}else {
    Write-Output "`nNo Python installation found, continuing..."
}

# Set parameters for the installation
$parameters = @(
    [pscustomobject]@{Name = "Python"; Index = 1; PathToInstaller = "\\dumpap3\tools\_Software\Python\python-3.9.1-amd64.exe"; TaskName = "Install Python"; Arguments = "/quiet TargetDir=C:\Python39 InstallAllUsers=1 PrependPath=1 Include_test=0"},
    [pscustomobject]@{Name = "Pip Upgrade"; Index = 3; PathToInstaller = "C:\Python39\python.exe"; TaskName = "Upgrade Pip"; Arguments = "-m pip install --upgrade pip"},
    [pscustomobject]@{Name = "PySide2"; Index = 4; PathToInstaller = "C:\Python39\Scripts\pip.exe"; TaskName = "Install PySide2"; Arguments = "install pyside2"},
    [pscustomobject]@{Name = "FFMpeg"; Index = 5; PathToInstaller = "C:\Python39\Scripts\pip.exe"; TaskName = "Install FFMpeg"; Arguments = "install ffmpeg-python"}
)

# If ascheduled task with the same name has been setup already, remove it
if (Get-ScheduledTask | Where-Object {$_.TaskName -match $parameters.$TaskName[0]}){
    Unregister-ScheduledTask -TaskName $parameters.$TaskName[0] -Confirm:$False
}

# Install Python
Install-App -PathToInstaller $parameters.PathToInstaller[0] -Arguments $parameters.Arguments[0] -TaskName $parameters.TaskName[0]
Start-Sleep 10
do {
    Start-Sleep 1
    Write-Output "`nWaiting for Python installation..."
    }until(Test-Path -Path "C:\Python39\scripts\pip.exe")

# Install Python packages
foreach ($p in $parameters){
    if ($p.Name -ne "Python"){
        Install-App -PathToInstaller $p.PathToInstaller -Arguments $p.Arguments -TaskName $p.TaskName
    }
}

# Set UAC back to normal
Set-SecurityLevel -High

# Print list of Python packages 
python -m pip list
