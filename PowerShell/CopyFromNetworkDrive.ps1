
function CopyFromNetworkDrive {
    param (
        [string]$NetworkPath,
        [string]$DriveLetter,
        [Hashtable]$FolderMap
    )

    # Mount the network drive
    $pathExists = Test-Path -Path $Networkpath
    Write-Host "Path check: " $pathExists
    If (-not ($pathExists)) {
        New-PSDrive -Name $DriveLetter -PSProvider FileSystem -Root $NetworkPath -Persist
    }

    foreach($SourceFolder in $FolderMap.keys){
        # Full source path
        $fullSourcePath = $SourceFolder
        $DestinationPath = [Environment]::ExpandEnvironmentVariables($FolderMap.$SourceFolder)
        Write-Host $DestinationPath
        #//$DriveLetter + ":\\" + $SourceFolder

        # Check if the source folder exists
        if (Test-Path -Path $fullSourcePath ) {
            # Copy the folder to the local destination
            Copy-Item -Path $fullSourcePath -Destination $DestinationPath  -Recurse -Force
            Write-Host $fullSourcePath "copied successfully to " $DestinationPath
        } else {
            Write-Host $fullSourcePath + " does not exist!"
        }
    }

    # Remove the network drive after the copy
    #Remove-PSDrive -Name $DriveLetter
}
#$NetworkPath = "\\192.168.0.225\tools\"
#$DriveLetter = "T"

#$arg_map = @{
#    NetworkPath = "\\192.168.0.225\tools\"
#    DriveLetter = "T"
#    CopyMap = @{
#        "T:\_Software\Adobe\After Effects\plugin_packages\HOJ_Production_Collection\*" = "%programfiles%\Adobe\Adobe After Effects 2023\Support Files\Plug-ins\";
#        "T:\_Software\Adobe\After Effects\plugin_packages\FXConsole_Plugin_Part\*" = "%programfiles%\Adobe\Adobe After Effects 2023\Support Files\Plug-ins\";
#        "T:\_Pipeline\cobopipe_v02-001\AfterEffect\AE_UI_Panel_Calls\*" = "%programfiles%\Adobe\Adobe After Effects 2023\Support Files\Scripts\ScriptUI Panels\";
#        "T:\_Software\Adobe\After Effects\plugin_packages\FXConsole_ScriptFolder_Part\*" = "%programfiles%\Adobe\Adobe After Effects 2023\Support Files\Scripts\ScriptUI Panels\"
#    }
#}
#
#CopyFromNetworkDrive -NetworkPath $arg_map.NetworkPath -DriveLetter $arg_map.DriveLetter -FolderMap $arg_map.CopyMap
