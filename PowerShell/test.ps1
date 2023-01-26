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

$apps = @{
    "firefox" = @{
        "path" = "firefox.exe" 
        "args" = "/S"
        }
    "maya" = @{
        "path" = "MayaExtracted\Setup.exe" 
        "args" = "--silent"
        }
    "vray" = @{
        "path" = "VRay\installVray.cmd" 
        "args" = ""
        }    
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
    Start-Process -FilePath "\\WSX3\shared\VRay\installVray.cmd" -Wait
    Remove-PSDrive -Name "W"
} 