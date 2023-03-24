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

$parameters = [pscustomobject]@{Name = "AdobeCC"; PathToInstaller = "T:\_Software\Adobe\AdobeInstaller_AE-Prem-PhotoSh\Build\setup.exe"; TaskName = "Install AdobeCC"; Arguments = "--silent"}

# If ascheduled task with the same name has been setup already, remove it
if (Get-ScheduledTask | Where-Object {$_.TaskName -match $parameters.$TaskName}){
    Unregister-ScheduledTask -TaskName $parameters.$TaskName -Confirm:$False
}


Install-App -PathToInstaller $parameters.PathToInstaller -Arguments $parameters.Arguments -TaskName $parameters.TaskName
Start-Sleep 10
Get-Process setup | Wait-Process
Set-SecurityLevel -High

