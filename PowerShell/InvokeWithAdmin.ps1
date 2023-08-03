#DOESN'T WORK DON'T USE
# InvokeWithAdmin.ps1

# Parameters for the function
$NetworkPath = "\\192.168.0.225\tools\"
$DriveLetter = "T"
$SourceFolders = @("T:\_Software\Adobe\After Effects\plugin_packages\HOJ_Production_Collection\*","T:\_Software\Adobe\After Effects\plugin_packages\FXConsole_Plugin_Part\*")
$DestinationFolder = "C:\Program Files\Adobe\Adobe After Effects 2023\Support Files\Plug-ins\"

# Path to the script containing the function
#$scriptPath = "T:\_Pipeline\cobopipe_v02-001\PowerShell\CopyFromNetworkDrive.ps1"
$scriptPath = "C\CopyFromNetworkDrive.ps1"

# Check if running as administrator
if (-Not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    # Relaunch script as an administrator
    Write-Output "Starting Admin"
    Start-Process powershell.exe -ArgumentList "-ExecutionPolicy Bypass -File $PSCommandPath" -Verb RunAs -PassThru -Wait
    }else
{
    # Dot-source the main script to import the function
    . $scriptPath

    # Call the function
    CopyFromNetworkDrive -NetworkPath $NetworkPath -DriveLetter $DriveLetter -SourceFolders $SourceFolders -DestinationFolder $DestinationFolder
}

