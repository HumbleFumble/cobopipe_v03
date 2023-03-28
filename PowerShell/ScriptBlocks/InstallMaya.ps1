
# This script can be called with parameters

param (
    [string]$AtTime
)

# Set temporarily admnistrator check (UAC) to none
Set-UAC -Off

Import-Module "C:\Program Files\PowerShell\7\Modules\Custom-Functions"

if (! ($AtTime)){
    $AtTime = Get-Date -Format "HH:mm"
}else{
    if (! ($AtTime -match "\d\d:\d\d")){
    Write-Output "`nPlease enter time in the following format: `"HH:mm`""
    break
    }
}

$parameters = [pscustomobject]@{Name = "Maya"; PathToInstaller = "\\dumpap3\tools\_Software\Maya\Maya2022-4\Maya2022extracted\Setup.exe"; TaskName = "Install Maya"; Arguments = "--silent"}

Set-UAC -Off

if (Get-ScheduledTask | Where-Object {$_.TaskName -match $parameters.TaskName} -ErrorAction SilentlyContinue){
    Unregister-ScheduledTask -TaskName $parameters.TaskName -Confirm:$False
    }

Install-App -PathToInstaller $parameters.PathToInstaller -Arguments $parameters.Arguments -TaskName $parameters.TaskName
Start-Sleep 3
Get-Process setup | Wait-Process

Unregister-ScheduledTask -TaskName $parameters.TaskName -Confirm:$False
Set-UAC -On
