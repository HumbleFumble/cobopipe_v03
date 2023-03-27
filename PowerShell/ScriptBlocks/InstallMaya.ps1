# Script parameters. This script can be called with parameters

param (
    [string]$AtTime
)


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
Install-App -PathToInstaller $parameters.PathToInstaller -Arguments $parameters.Arguments -TaskName $parameters.TaskName
Start-Sleep 3
Get-Process setup | Wait-Process
Set-UAC -On