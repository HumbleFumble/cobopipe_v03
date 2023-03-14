# $InstallScriptBlock = .\InstallScriptBlock.ps1

# # List of computers to run scriptblock agains
# $ComputersList = "vm2", "vm3"

# Run the scriptblock on remote computer
# Invoke-Command -ComputerName $ComputersList -ScriptBlock $InstallScriptBlock

# Or use session to send the command 
# $creds = Get-Credential -UserName vmnet\admin
# $session = New-PSSession -ComputerName $computerslist -Credential $creds
# Invoke-Command -Session  $session -ScriptBlock $InstallScriptBlock

# function Install-App {
#     param (
#         [Parameter(Mandatory)][string[]]$ComputersList,
#         [Parameter(Mandatory)][scriptblock]$InstallScriptBlock,
#         [string]$AtTime
#     )
#     Invoke-Command -ComputerName $ComputersList -ScriptBlock $InstallScriptBlock
# }

# Install-App -ComputersList $ComputersList -InstallScriptBlock $InstallScriptBlock
#

# List of computers to run scriptblock agains
# $ComputersList = "vm2", "vm3"


$install_apps = Get-Content -Path "C:\Users\plp\VsCodeProjects\cobopipe_v02-001\PowerShell\install_apps.json" | ConvertFrom-Json

$applist = @(
    [pscustomobject]@{Name = "Python"; ScriptBlock = "Path to script"}
    
)

# $install_apps.$ComputerName is object that contains the apps
# $b is custom object from the install list
#
# for each computer in the list from the install_apps.json, created by the python script
# for each application in the apps list of the computer
# if the application is in the install list, do this
foreach ($ComputerName in $install_apps.psobject.Properties.GetEnumerator().Name){
    foreach ($install_app in $install_apps.$ComputerName.DisplayName) {
        foreach ($app in $applist.name){
        if ($install_app -match $app){
            # do this
            $("$app "+ " $ComputerName")}
        }
    }
}

function Install-App {
    param (
        [Parameter(Mandatory)][string[]]$ComputersList,
        [scriptblock]$InstallScriptBlock,
        [string]$FilePath,
        [string]$AtTime
    )
    if ($InstallScriptBlock){
        Invoke-Command -ComputerName $ComputersList -ScriptBlock $InstallScriptBlock
    } elseif ($FilePath) {
        Invoke-Command -FilePath $FilePath -ComputerName $ComputersList 
    }
    
}

# Install-App -ComputersList $ComputersList -FilePath 'C:\users\admin\desktop\InstallScriptBlock.ps1'

# or Install-App -ComputersList $ComputersList -InstallScriptBlock $InstallScriptBlock