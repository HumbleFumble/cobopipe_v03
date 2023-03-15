# Uninstall any previously installed Python version
$python =  Get-CimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python *"
$python | Where-Object -Property Name -Match "python ..... tcl*" | Invoke-CimMethod -MethodName Uninstall
$python | Where-Object -Property Name -Match "python ..... pip*" | Invoke-CimMethod -MethodName Uninstall
$python | Where-Object -Property Name -Match "python *" | Invoke-CimMethod -MethodName Uninstall -ErrorAction SilentlyContinue

# Update!
# $PathToInstaller = "\\dumpap3\tools\_Pipeline\cobopipe_v02-001\PowerShell\ScriptBlocks\installPython
$parameters = [pscustomobject]@{Name = "Python"; PathToInstaller = "\\dumpap3\tools\_Software\Python\python-3.9.1-amd64.exe"; TaskName = "Install Python"; Arguments = "/quiet TargetDir=C:\Python39 InstallAllUsers=1 PrependPath=1 Include_test=0"}
$AtTime = Get-Date -Format "HH:mm"
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
    Register-ScheduledTask -TaskName $TaskName -InputObject $Task -User 'System'
    Start-ScheduledTask -TaskName $TaskName
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$False
}

Install-App -PathToInstaller $parameters.PathToInstaller -Arguments $parameters.Arguments -TaskName $parameters.TaskName