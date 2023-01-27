

# Get / Set connection profile on the target machine. 
# Once a computer joins a domain, the network profile changes automatically to "Domain"
# ----------------------------------------------------------------------------------------------------------------------
# Get network profile
(Get-NetConnectionProfile).NetworkCategory
# Set network profile
Set-NetConnectionProfile -NetworkCategory "Domain"

# Enabling / disabling "File And Printer Sharing" and "Network Discovery"
# ----------------------------------------------------------------------------------------------------------------------
# Enabling "File And Printer Sharing" is necessary for communication between 2 computers on a network
# For connection to be established between two Windows machines, both machines must have "File And Printer Sharing" enabled
# If the machines are on domain, "File And Printer Sharing" must be enabled for the "Domain" network profile
# For rest of the profiles "File And Printer Sharing" can remain turned off as it is not necessary to be 
# on for remote operations in a domain
# "Network Discovery" only makes the computer visible on the network, but not accessible

Set-NetFirewallRule -DisplayGroup "File And Printer Sharing" -Profile "Domain" -Enabled True
Set-NetFirewallRule -DisplayGroup "Network Discovery" -Profile "Domain" -Enabled True

# Check if "File and printer sharing" is enabled for the "Domain" profile and enable it if it's not
if ((Get-NetFirewallRule -DisplayGroup "File and printer sharing").Disabled){
    Set-NetFirewallRule -DisplayGroup "File And Printer Sharing" -Profile "Domain" -Enabled True
}

# Hashtable containing applications intended for instalation and the respective command
$apps = @(
    [pscustomobject]@{Name = "Maya 2022"; Path = "\\wsx3\shared\Maya2022extracted\Setup.exe"; Arguments = "--silent"}
    [pscustomobject]@{Name = "V-Ray"; Path = "\\WSX3\shared\VRay\installVray.cmd"; Arguments = ""}

)

# Installing application. It appears that the application must have option for silent install to be installed remotely.
$creds = Get-Credential -UserName "network\admin"
$driveRoot = "\\driveroot\folder"
$driveName = "drive letter"
$computerName = 'computer name'
$appRelativePath = '\' + $apps['firefox']['path']
$installApp = $driveRoot + $appRelativePath
$appArgs = $apps['firefox']['args']

Invoke-Command -ComputerName $computerName -ScriptBlock {
    # Map the network share within PowerShell
    New-PSDrive -Name $using:driveName -Root $using:driveRoot -PSProvider "FileSystem" -Credential $using:creds -Persist
    # The arguments for launching the application are app-specific 
    Start-Process -FilePath $using:installApp -ArgumentList $using:appArgs -Wait
    # Remove the share
    Remove-PSDrive $using:driveName -Force
}


# Get current logged-in user from remote computer
function Get-CurrentUser {
    [CmdletBinding()]
    param( 
        [Parameter(Mandatory = $true)]
        [string]$ComputerName
    )
  
    $queryResults = (qwinsta /server:$ComputerName | ForEach-Object { (($_.trim() -replace "\s+",","))} | ConvertFrom-Csv)
    foreach ($i in $queryResults.username){
        try {$i.ToUInt32($null) -ne "String" | Out-Null} 
        catch {$result += $i}
    }
  return $result
  }

