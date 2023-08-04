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
            New-PSDrive -Name "T" -PSProvider FileSystem -Root "\\dumpap3\tools" -Persist -Credential $using:creds
            . $using:ScriptPath
#            & $using:ScriptPath -AtTime $using:AtTime
            CopyFromNetworkDrive -NetworkPath $script_args.NetworkPath -DriveLetter $script_args.DriveLetter -FolderMap $script_args.CopyMap
    } -Args $script_args
}


$arg_map = @{
    NetworkPath = "\\192.168.0.225\tools\"
    DriveLetter = "T"
    CopyMap = @{
        "T:\_Software\Adobe\After Effects\plugin_packages\HOJ_Production_Collection\*" = "%programfiles%\Adobe\Adobe After Effects 2023\Support Files\Plug-ins\";
        "T:\_Software\Adobe\After Effects\plugin_packages\FXConsole_Plugin_Part\*" = "%programfiles%\Adobe\Adobe After Effects 2023\Support Files\Plug-ins\";
        "T:\_Pipeline\cobopipe_v02-001\AfterEffect\AE_UI_Panel_Calls\*" = "%programfiles%\Adobe\Adobe After Effects 2023\Support Files\Scripts\ScriptUI Panels\";
        "T:\_Software\Adobe\After Effects\plugin_packages\FXConsole_ScriptFolder_Part\*" = "%programfiles%\Adobe\Adobe After Effects 2023\Support Files\Scripts\ScriptUI Panels\"
    }
}
#CopyFromNetworkDrive -NetworkPath $arg_map.NetworkPath -DriveLetter $arg_map.DriveLetter -FolderMap $arg_map.CopyMap

$creds = Get-Credential -UserName cphbom\deadline
#$machine_list = 1..33
$machine_list = @("33")


foreach($u in $machine_list)
{
    $ComputerName = "WSX" + $u
    Invoke-Script -UserName "CPHBOM\deadline" -ComputerName $ComputerName -ScriptPath "\\dumpap3\tools\_Pipeline\cobopipe_v02-001\PowerShell\CopyFromNetworkDrive.ps1" -creds $creds -script_args $arg_map
}


