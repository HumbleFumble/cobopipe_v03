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

$parameters = [pscustomobject]@{Name = "Maya"; PathToInstaller = "\\dumpap3\tools\_Software\Maya\Maya2022-4\Maya2022extracted\Setup.exe"; TaskName = "Install Maya"; Arguments = "--silent"}

# If ascheduled task with the same name has been setup already, remove it
if (Get-ScheduledTask | Where-Object {$_.TaskName -match $parameters.$TaskName[0]}){
    Unregister-ScheduledTask -TaskName $parameters.$TaskName[0] -Confirm:$False
}


Install-App -PathToInstaller $parameters.PathToInstaller -Arguments $parameters.Arguments -TaskName $parameters.TaskName
Start-Sleep 3
Get-Process setup | Wait-Process
Set-SecurityLevel -High