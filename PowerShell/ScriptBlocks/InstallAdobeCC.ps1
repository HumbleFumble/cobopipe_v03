# This script can be called with parameters

param (
    [string]$AtTime
)

Set-UAC -Off

if (! ($AtTime)){
    $AtTime = Get-Date -Format "HH:mm"
}else{
    if (! ($AtTime -match "\d\d:\d\d")){
    Write-Output "`nPlease enter time in the following format: `"HH:mm`""
    break
    }
}

$parameters = [pscustomobject]@{Name = "AdobeCC"; PathToInstaller = "\\dumpap3\tools\_Software\Adobe\AdobeInstaller_AE-Prem-PhotoSh\Build\setup.exe"; TaskName = "Install AdobeCC"; Arguments = "--silent"}


Install-App -PathToInstaller $parameters.PathToInstaller -Arguments $parameters.Arguments -TaskName $parameters.TaskName
Start-Sleep 3
Get-Process setup | Wait-Process
Set-UAC -On