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
        Register-ScheduledTask -TaskName $TaskName -InputObject $Task #-User 'System'
        Start-ScheduledTask -TaskName $TaskName

    }