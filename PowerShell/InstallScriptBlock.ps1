
# Set execution policy to run scripts
Set-ExecutionPolicy Bypass

# Powershell silent web install
if (! (Test-Path -Path "C:\Program Files\PowerShell\7\pwsh.exe")){
    iex "& { $(irm https://aka.ms/install-powershell.ps1) } -UseMSI -quiet"
}else {
    Write-Host "`nPowerShell 7 already installed on this system"
}

# If $AtTime is not set above, it will be set with the current time
$AtTime = $using:AtTime
if (!$AtTime){
    $AtTime = $(Get-Date -Format HH:mm)
}
# List os custom objects, containing the parameters for each installer
$parameters = @(
    [pscustomobject]@{Name = "Python"; Index = 1; PathToInstaller = "\\rs1\shared\Python\python-3.9.1-amd64.exe"; TaskName = "Install Python"; Arguments = "/quiet TargetDir=C:\Python39 InstallAllUsers=1 PrependPath=1 Include_test=0"},
    [pscustomobject]@{Name = "Firefox"; Index = 2; PathToInstaller = "\\rs1\shared\Firefox\firefox.exe"; TaskName = "Install Firefox"; Arguments = "/S"},
    [pscustomobject]@{Name = "Pip Upgrade"; Index = 3; PathToInstaller = "C:\Python39\python.exe"; TaskName = "Upgrade Pip"; Arguments = "-m pip install --upgrade pip"},
    [pscustomobject]@{Name = "PySide2"; Index = 4; PathToInstaller = "C:\Python39\Scripts\pip.exe"; TaskName = "Install PySide2"; Arguments = "install pyside2"},
    [pscustomobject]@{Name = "FFMpeg"; Index = 5; PathToInstaller = "C:\Python39\Scripts\pip.exe"; TaskName = "Install FFMpeg"; Arguments = "install ffmpeg-python"}
)

# Uninstall any previously installed Python version
$python =  Get-CimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python *"
$python | Where-Object -Property Name -Match "python ..... tcl*" | Invoke-CimMethod -MethodName Uninstall
$python | Where-Object -Property Name -Match "python ..... pip*" | Invoke-CimMethod -MethodName Uninstall
$python | Where-Object -Property Name -Match "python *" | Invoke-CimMethod -MethodName Uninstall -ErrorAction SilentlyContinue

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

$piplist = python -m pip list
Write-Host $piplist

Set-ExecutionPolicy Restricted

