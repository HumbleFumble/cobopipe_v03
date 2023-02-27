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
$ComputersList = "vm2", "vm3"

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

Install-App -ComputersList $ComputersList -FilePath 'C:\users\admin\desktop\InstallScriptBlock.ps1'

# or Install-App -ComputersList $ComputersList -InstallScriptBlock $InstallScriptBlock