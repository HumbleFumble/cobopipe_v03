# Script parameters. This script can be called with parameters

param (
    [string]$AtTime
)

function Set-SecurityLevel{
    param (
        [switch]$High,
        [switch]$Low
    )
    $path = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System"
    if ($High -and $Low){
        Write-Host "Conflicting parameters. Choose either 'High' or 'Low'" -ForegroundColor Red
    }else {
        if ($Low){
            Set-ExecutionPolicy Bypass -Confirm:$False
            New-ItemProperty -Path $path -Name 'ConsentPromptBehaviorAdmin' -Value 0 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'ConsentPromptBehaviorUser' -Value 3 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'EnableInstallerDetection' -Value 1 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'EnableLUA' -Value 1 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'EnableVirtualization' -Value 0 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'PromptOnSecureDesktop' -Value 0 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'ValidateAdminCodeSignatures' -Value 0 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'FilterAdministratorToken' -Value 0 -PropertyType DWORD -Force | Out-Null
            Set-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3' -Name 1806 -Value 0
        }
        elseif ($High){
            Set-ItemProperty -Path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Internet Settings\Zones\3' -Name 1806 -Value 1
            New-ItemProperty -Path $path -Name 'ConsentPromptBehaviorAdmin' -Value 5 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'ConsentPromptBehaviorUser' -Value 3 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'EnableInstallerDetection' -Value 1 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'EnableLUA' -Value 1 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'EnableVirtualization' -Value 1 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'PromptOnSecureDesktop' -Value 1 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'ValidateAdminCodeSignatures' -Value 0 -PropertyType DWORD -Force | Out-Null
            New-ItemProperty -Path $path -Name 'FilterAdministratorToken' -Value 0 -PropertyType DWORD -Force | Out-Null
            Set-ExecutionPolicy Restricted -Confirm:$false
        }
    }
}
# END Set-SecurityLevel
#-------------------------------------------------------------------------------------------------------------------------------------------

function Install-App { 

    param (
        [Parameter()][string]$PathToInstaller,
        [Parameter()][string]$Arguments,
        [Parameter()][string]$TaskName
    
    )
    # Set up scheduled task for each set of parameters and run it
    #--------------------------------------------------------------------------------------------------------------------------------------------
    
        $Action = New-ScheduledTaskAction -Execute $PathToInstaller -Argument $Arguments
        $Trigger = New-ScheduledTaskTrigger -Once -At $AtTime
        $Settings = New-ScheduledTaskSettingsSet
        $Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings
        Register-ScheduledTask -TaskName $TaskName -InputObject $Task
        Start-ScheduledTask -TaskName $TaskName
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$False
}

# END Install-App
#-------------------------------------------------------------------------------------------------------------------------------------------

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

# Set temporarily admnistrator check (UAC) to none
Set-SecurityLevel -Low

# Set time for the installation (the code below get the current time and the installation runs immediatelly)
if (! ($AtTime)){
    $AtTime = Get-Date -Format "HH:mm"
}else{
    if (! ($AtTime -match "\d\d:\d\d")){
    Write-Output "`nPlease enter time in the following format: `"HH:mm`""
    break
    }
}
# Install
Install-App -PathToInstaller $parameters.PathToInstaller[0] -Arguments $parameters.Arguments[0] -TaskName $parameters.TaskName[0]
Start-Sleep 10
do {
    Start-Sleep 1
    Write-Output "`nWaiting for Python installation..."
    }until(Test-Path -Path "C:\Python39\scripts\pip.exe")

foreach ($p in $parameters){
    if ($p.Name -ne "Python"){
        Install-App -PathToInstaller $p.PathToInstaller -Arguments $p.Arguments -TaskName $p.TaskName
    }
}

python -m pip list
# Set admnistrator check (UAC) back to normal
Set-SecurityLevel -High