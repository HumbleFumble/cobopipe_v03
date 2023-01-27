# Install VRay
# ! From elevated prompt ! ("start pwsh -Credential "")
# It seems with open session from elevated propt installations go as anticipated

$creds = Get-Credential -UserName "cphbom\administrator"
$session = New-PSSession -ComputerName vm1 -Credential $creds


Invoke-Command -Session $session -ScriptBlock {

    New-PSDrive -Name "W" -Root "\\WSX3\shared" -PSProvider "FileSystem" -Credential $using:creds -Persist
    Set-ExecutionPolicy Bypass
    Start-Process -FilePath "\\WSX3\shared\VRay\installVray.cmd" -Wait
    Remove-PSDrive -Name "W"
    Set-ExecutionPolicy Restricted
} 



# Installing application. It appears that the application must have option for silent install to be installed remotely.
$creds = Get-Credential -UserName "network\admin"
$driveRoot = "\\driveroot\folder"
$driveName = "drive letter"
$computerName = 'computer name'
# Perhaps a loop here that iterates over a list of desired apps and sets the variables below

$appRelativePath = '\' + $apps['firefox']['path']
$installApp = $driveRoot + $appRelativePath
$appArgs = $apps['firefox']['args']

Invoke-Command -ComputerName $computerName -ScriptBlock {
    # Map the network share within PowerShell
    New-PSDrive -Name $using:driveName -Root $using:driveRoot -PSProvider "FileSystem" -Credential $using:creds -Persist
    Set-ExecutionPolicy Bypass
    # The arguments for launching the application are app-specific 
    Start-Process -FilePath $using:installApp -ArgumentList $using:appArgs -Wait
    # Remove the share
    Remove-PSDrive $using:driveName -Force
    Set-ExecutionPolicy Restricted
}

# Install V-Ray and Maya

$creds = Get-Credential -UserName "cphbom\administrator"
$session = New-PSSession -ComputerName vm1 -Credential $creds


Invoke-Command -Session $session -ScriptBlock {

    New-PSDrive -Name "W" -Root "\\WSX3\shared" -PSProvider "FileSystem" -Credential $using:creds -Persist
    Set-ExecutionPolicy Bypass
    Start-Process -FilePath "\\WSX3\shared\Maya2022extracted\Setup.exe" -ArgumentList "--silent" -Wait
    Start-Sleep 3
    Start-Process -FilePath "\\WSX3\shared\VRay\installVray.cmd" -ArgumentList "" -Wait
    Remove-PSDrive -Name "W"
} 

# Open session to remote computer and install applications from custom object

$computerName = 'vm1'
$driveRoot = "\\wsx3\shared"
$driveName = "W"

$creds = Get-Credential -UserName "cphbom\administrator"
$session = New-PSSession -ComputerName $computerName -Credential $creds

Invoke-Command -Session $session -ScriptBlock {

    New-PSDrive -Name $using:driveName -Root $using:driveRoot -PSProvider "FileSystem" -Credential $using:creds -Persist
    Set-ExecutionPolicy Bypass
    # Installing applications from custom object
    # This function installs a program with the parameters in a pscustomobject
    function Install-App {
        [CmdletBinding()]
        param ([PSCustomObject]$parameters)
    
        if (!($parameters.arguments)){
            Start-Process $parameters.path -Wait
        }
        else {
            Start-Process $parameters.path -ArgumentList $parameters.arguments -Wait
        }    
    }

    # Array of custom objects containing the application name, path to it and the arguments it should be run with, if any
    $apps = @(
        [pscustomobject]@{Name = "Maya 2022"; Path = "\\wsx3\shared\Maya2022extracted\Setup.exe"; Arguments = "--silent"}
        [pscustomobject]@{Name = "V-Ray"; Path = "\\wsx3\shared\VRay\installVray.cmd"; Arguments = ""}
    )

    # Loop over the array of custom objects
    foreach ($i in $apps){
        Install-App $i
        Start-Sleep 3
    }

    Remove-PSDrive -Name $using:driveName
    Set-ExecutionPolicy Restricted
} 

# Test connection to host
$list = "wsx2", "wsx11", "wsx19", "wsx24"
foreach ($i in $list){
    Write-Host "$($i) $((Test-Connection $i -Count 1).status)"
}