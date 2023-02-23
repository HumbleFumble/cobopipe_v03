#-------------------------------------------------------------------------------------------------------------------------------------------
function Install-App{
    param ([Parameter(Mandatory=$true)][string]$ComputerName,
           [Parameter(Mandatory=$true)][string]$PathToInstaller,
           [Parameter(Mandatory=$true)][string]$TaskName,
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
    Register-ScheduledTask -TaskName $TaskName -InputObject $Task -User 'System'
    Start-ScheduledTask -TaskName $TaskName
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$False
    
    if(Get-ScheduledTask -TaskName $TaskName){
        Write-Host "`"$TaskName`" scheduled task successfully registered"
    }else{
        Write-Host "`"$TaskName`" scheduled task could not beregistered"
    }
}
# END Install-App
#-------------------------------------------------------------------------------------------------------------------------------------------
    