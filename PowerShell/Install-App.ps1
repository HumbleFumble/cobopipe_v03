#-------------------------------------------------------------------------------------------------------------------------------------------
# function Install-App{
#     param ([Parameter(Mandatory=$true)][string]$ComputerName,
#            [Parameter(Mandatory=$true)][string]$PathToInstaller,
#            [Parameter][string]$Arguments,
#            [switch]$AtTime
#     )
#     if (!($AtTime)){
#         $AtTime = Get-Date -Format HH:mm
#     }
#     $Action = New-ScheduledTaskAction -Execute $PathToInstaller -Argument $Arguments
#     $Trigger = New-ScheduledTaskTrigger -Once -At $AtTime
#     $Settings = New-ScheduledTaskSettingsSet
#     $Task = New-ScheduledTask -Action $Action -Trigger $Trigger -Settings $Settings
#     Register-ScheduledTask -TaskName 'Start Maya' -InputObject $Task -User 'System'
#     Start-ScheduledTask -TaskName 'Start Maya'
#     Unregister-ScheduledTask -TaskName 'Start Maya' -Confirm:$False
# }
# # END Install-App
# #-------------------------------------------------------------------------------------------------------------------------------------------
    
# Function fails with System.Management.Automation.ParameterAttribute error. Perhaps PSObject fed function could work
# Without function, the code executes fine, Python installation example:

Invoke-Command -ComputerName vm2 -ScriptBlock {

    if (get-cimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python 3.9.1*"){
    Write-Host "`nPython $PythonVersion installation(s) found. Uninstalling..."
    Get-cimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python ..... tcl*" | Invoke-CimMethod -MethodName Uninstall
    Get-cimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python ..... pip*" | Invoke-CimMethod -MethodName Uninstall
    Get-cimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python *" | Invoke-CimMethod -MethodName Uninstall
    
    }
    $PathToInstaller = "\\rs1\shared\Python\python-3.9.1-amd64.exe"
    $Arguments = '/quiet TargetDir=C:\Python39 InstallAllUsers=1 PrependPath=1 Include_test=0'
    $AtTime = Get-Date -Format HH:mm
    $Action = New-ScheduledTaskAction -Execute $PathToInstaller -Argument $Arguments
    $Trigger = New-ScheduledTaskTrigger -Once -At $AtTime
    $Settings = New-ScheduledTaskSettingsSet
    $Task = New-ScheduledTask -Action $Action -Description $Trigger -Settings $Settings
    Register-ScheduledTask -TaskName 'Install Python' -InputObject $Task -User 'System'
    Start-ScheduledTask -TaskName 'Install Python'
    Unregister-ScheduledTask -TaskName 'Install Python' -Confirm:$false
    }
