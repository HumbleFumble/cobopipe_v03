function Invoke-Script {

param (
    [Parameter(Mandatory)][string]$UserName,
    [Parameter(Mandatory)][string[]]$ComputerName,
    [Parameter(Mandatory)][string]$ScriptPath,
    [Parameter()][string]$AtTime
)
    
if (! ($AtTime)){
    $AtTime = Get-Date -Format "HH:mm"
}else{
    if (! ($AtTime -match "\d\d:\d\d")){
    Write-Output "`nPlease enter time in the following format: `"HH:mm`""
    break
    }
}

$creds = Get-Credential -UserName $UserName -Message:$false
    
Invoke-Command -ComputerName $ComputerName -ScriptBlock {

        Set-ExecutionPolicy Bypass
    
        New-PSDrive -Name "T" -PSProvider FileSystem -Root "\\dumpap3\tools" -Persist -Credential $using:creds
    
        Import-Module "T:\_Pipeline\cobopipe_v02-001\PowerShell\Custom-Functions.psm1"
    
        & $using:ScriptPath -AtTime $using:AtTime
    
    }
}