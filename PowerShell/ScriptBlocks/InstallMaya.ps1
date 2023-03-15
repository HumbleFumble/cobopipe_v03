$parameters = [pscustomobject]@{Name = "Maya"; PathToInstaller = "\\dumpap3\tools\_Software\Maya\Maya2022-4\Maya2022extracted\Setup.exe"; TaskName = "Install Maya"; Arguments = "--silent"}
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