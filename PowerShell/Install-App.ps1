#-------------------------------------------------------------------------------------------------------------------------------------------
function Install-App{
    param ([Parameter(Mandatory=$true)][string]$ComputerName,
           [Parameter(Mandatory=$true)][string]$PathToInstaller,
           [Parameter][string]$Arguments,
           [switch]$AtTime
    )
    if (!($AtTime)){
        $AtTime = Get-Date -Format HH:mm
    }
    $Action = New-ScheduledTaskAction -Execute $PathToInstaller -Argument $Arguments
    $Trigger = New-ScheduledTaskTrigger -Once -At $AtTime
    $Settings = New-ScheduledTaskSettingsSet
    $Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings
    Register-ScheduledTask -TaskName 'Start Maya' -InputObject $Task -User 'System'
    Start-ScheduledTask -TaskName 'Start Maya'
    Unregister-ScheduledTask -TaskName 'Start Maya' -Confirm:$False
}
# END Install-App
#-------------------------------------------------------------------------------------------------------------------------------------------
    