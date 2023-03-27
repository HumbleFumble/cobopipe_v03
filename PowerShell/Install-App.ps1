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
        Register-ScheduledTask -TaskName $TaskName -InputObject $Task
        Start-ScheduledTask -TaskName $TaskName
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$False
    }
    
    if (! ($AtTime)){
        $AtTime = Get-Date -Format "HH:mm"
    }else{
        if (! ($AtTime -match "\d\d:\d\d")){
        Write-Output "`nPlease enter time in the following format: `"HH:mm`""
        break
        }
    }