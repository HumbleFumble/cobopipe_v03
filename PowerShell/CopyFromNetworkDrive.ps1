
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
            Write-Host "Folder copied successfully!"
        } else {
            Write-Host "Source folder does not exist!"
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