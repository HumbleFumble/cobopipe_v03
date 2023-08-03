function Invoke-Script {

param (
    [Parameter(Mandatory)][string]$UserName,
    [Parameter(Mandatory)][string[]]$ComputerName,
    [Parameter(Mandatory)][string]$ScriptPath,
    [Parameter()][string]$AtTime,
    [Parameter()][PSCredential]$creds
)

    if(! ($creds))
    {
        $creds = Get-Credential -UserName $UserName -Message:$false
    }
    Invoke-Command -ComputerName $ComputerName -ScriptBlock {

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
            & $using:ScriptPath -AtTime $using:AtTime

    }
}


$creds = Get-Credential -UserName cphbom\deadline
#$machine_list = 1..33
$machine_list = @("2","15")

foreach($u in $machine_list)
{
    $ComputerName = "WSX" + $u
    Invoke-Script -UserName "CPHBOM\deadline" -ComputerName $ComputerName -ScriptPath "\\dumpap3\tools\_Pipeline\cobopipe_v02-001\PowerShell\CopyFromNetworkDrive.ps1" -creds $creds
}


