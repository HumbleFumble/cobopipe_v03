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

Start-Process $pythonfilepath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0" -Wait
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

Remove-PSDrive -Name "T" -Force
Set-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3' -Name 1806 -Value 1
Set-ExecutionPolicy Restricted