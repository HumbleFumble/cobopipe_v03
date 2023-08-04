## This script is meant to be run in a powershell.
## This script updates AfterEffects script and plugin folders, it makes them if they are not there already

function Invoke-Script {

param (
    [Parameter(Mandatory)][string]$UserName,
    [Parameter(Mandatory)][string[]]$ComputerName,
    [Parameter(Mandatory)][string]$ScriptPath,
    [Parameter()][string]$AtTime,
    [Parameter()][PSCredential]$creds,
    [Parameter()][Hashtable]$script_args
)

    if(! ($creds))
    {
        $creds = Get-Credential -UserName $UserName -Message:$false
    }
    Invoke-Command -ComputerName $ComputerName -ScriptBlock {
        param($script_args)
        Write-Output $script_args
        if (! ($AtTime)){
            $AtTime = Get-Date -Format "HH:mm"
        }else{
            if (! ($AtTime -match "\d\d:\d\d")){
            Write-Output "`nPlease enter time in the following format: `"HH:mm`""
            break
            }
        }
        Set-ExecutionPolicy Bypass

        # Find if AE is install and the highest version
        # Define the directory where Adobe After Effects is typically installed.
        $adobeDir = [Environment]::ExpandEnvironmentVariables("%programfiles%\Adobe")
        # Check if the directory exists.
        if (Test-Path $adobeDir) {
            # Get a list of all Adobe After Effects installations.
            $aeInstalls = Get-ChildItem $adobeDir | Where-Object { $_.Name -like "*Adobe After Effects*" }
            # Extract the version numbers using regular expressions.
            $versions = $aeInstalls | ForEach-Object { if ($_.Name -match "\d+") { $matches[0] } }
            # Get the highest version.
            $highestVersion = $versions | Measure-Object -Maximum
            Write-Host "The highest version of Adobe After Effects installed is: $($highestVersion.Maximum)"
        }
        else {
            Write-Host "Adobe directory not found."
            return $false
        }
        $new_map = @{}
        foreach($p in $script_args.CopyMap.keys){
            if( $script_args.CopyMap.$p.Contains("%aftereffects%"))
            {
                $temp_path =  [Environment]::ExpandEnvironmentVariables("%programfiles%\Adobe\Adobe After Effects ") + $highestVersion.Maximum + "\Support Files"
                $final_path = $script_args.CopyMap.$p.replace("%aftereffects%",$temp_path)
                $new_map.add($p, $final_path)
            }else{
                $new_map.add($p, $script_args.CopyMap.$p)
            }

        }
        $script_args.CopyMap = $new_map
        Write-Output $script_args.CopyMap

        New-PSDrive -Name "T" -PSProvider FileSystem -Root "\\dumpap3\tools" -Persist -Credential $using:creds
        . $using:ScriptPath
#        & $using:ScriptPath -AtTime $using:AtTime
        CopyFromNetworkDrive -NetworkPath $script_args.NetworkPath -DriveLetter $script_args.DriveLetter -FolderMap $script_args.CopyMap
    } -Args $script_args
}


#### INFO: ####
#### Added a fake env var called %aftereffects% to the destination path.
#### Which in the script gets replaced with: "%programfiles%\Adobe\Adobe After Effects 2023\Support Files\" at runtime on the local machine
#### So its a way to get the newest version of After effects and find the programfiles folder, even if its called "Programmer".

$arg_map = @{
    NetworkPath = "\\192.168.0.225\tools\"
    DriveLetter = "T"
    CopyMap = @{
        "T:\_Software\Adobe\After Effects\plugin_packages\HOJ_Production_Collection\*" = "%aftereffects%\Plug-ins\";
        "T:\_Software\Adobe\After Effects\plugin_packages\FXConsole_Plugin_Part\*" = "%aftereffects%\Plug-ins\";
        "T:\_Pipeline\cobopipe_v02-001\AfterEffect\AE_UI_Panel_Calls\*" = "%aftereffects%\Scripts\ScriptUI Panels\";
        "T:\_Software\Adobe\After Effects\plugin_packages\FXConsole_ScriptFolder_Part\*" = "%aftereffects%\Scripts\ScriptUI Panels\"
    }
}
#CopyFromNetworkDrive -NetworkPath $arg_map.NetworkPath -DriveLetter $arg_map.DriveLetter -FolderMap $arg_map.CopyMap

$creds = Get-Credential -UserName cphbom\deadline
#$machine_list = 1..33 #Use this variable for all the machines
$machine_list = @("15")


foreach($u in $machine_list)
{
    $ComputerName = "WSX" + $u
    Invoke-Script -UserName "CPHBOM\deadline" -ComputerName $ComputerName -ScriptPath "\\dumpap3\tools\_Pipeline\cobopipe_v02-001\PowerShell\CopyFromNetworkDrive.ps1" -creds $creds -script_args $arg_map
}


