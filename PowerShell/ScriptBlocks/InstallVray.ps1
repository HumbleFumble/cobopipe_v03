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

$parameters = [pscustomobject]@{Name = "Vray"; PathToInstaller = "T:\_Software\Chaosgroup\vray_adv_52002_maya2022_x64.exe"; TaskName = "Install Vray"; Arguments = "-gui=0 -configFile=T:\_Software\Chaosgroup\config.xml -quiet=1 -auto"}

Set-UAC -Off
Install-App -PathToInstaller $parameters.PathToInstaller -Arguments $parameters.Arguments -TaskName $parameters.TaskName
Start-Sleep 3
Get-Process setup | Wait-Process

Unregister-ScheduledTask -TaskName $parameters.TaskName -Confirm:$False
Set-UAC -On

