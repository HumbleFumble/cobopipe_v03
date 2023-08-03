
function CopyFromNetworkDrive {
    param (
        [string]$NetworkPath,
        [string]$DriveLetter,
        [string[]]$SourceFolders,
        [string]$DestinationFolder
    )

    # Mount the network drive
    $pathExists = Test-Path -Path $Networkpath
    If (-not ($pathExists)) {
        New-PSDrive -Name $DriveLetter -PSProvider FileSystem -Root $NetworkPath -Persist
    }
    foreach($SourceFolder in $SourceFolders){
        # Full source path
        $fullSourcePath = $SourceFolder
        #//$DriveLetter + ":\\" + $SourceFolder

        # Check if the source folder exists
        if (Test-Path -Path $fullSourcePath) {
            # Copy the folder to the local destination
            Copy-Item -Path $fullSourcePath -Destination $DestinationFolder -Recurse -force
            Write-Host $fullSourcePath + "copied successfully to " + $DestinationFolder
        } else {
            Write-Host $fullSourcePath + " does not exist!"
        }
    }

    # Remove the network drive after the copy
    Remove-PSDrive -Name $DriveLetter
}
$NetworkPath = "\\192.168.0.225\tools\"
$DriveLetter = "T"
$SourceFolders = @("T:\_Software\Adobe\After Effects\plugin_packages\HOJ_Production_Collection\*","T:\_Software\Adobe\After Effects\plugin_packages\FXConsole_Plugin_Part\*")
$DestinationFolder = "C:\Program Files\Adobe\Adobe After Effects 2023\Support Files\Plug-ins\"
CopyFromNetworkDrive -NetworkPath $NetworkPath -DriveLetter $DriveLetter -SourceFolders $SourceFolders  -DestinationFolder $DestinationFolder

$SourceFolders = @("T:\_Pipeline\cobopipe_v02-001\AfterEffect\AE_UI_Panel_Calls\*","T:\_Software\Adobe\After Effects\plugin_packages\FXConsole_ScriptFolder_Part\*")
$DestinationFolder = "C:\Program Files\Adobe\Adobe After Effects 2023\Support Files\Scripts\ScriptUI Panels\"
CopyFromNetworkDrive -NetworkPath $NetworkPath -DriveLetter $DriveLetter -SourceFolders $SourceFolders  -DestinationFolder $DestinationFolder