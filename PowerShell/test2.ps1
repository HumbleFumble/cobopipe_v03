
param (
[string]$username, 
[switch]$blabla
)

if (-not $username){
$username = whoami
}

$creds = Get-Credential -UserName $username -Message:$false

New-PSDrive -Name "T" -PSProvider FileSystem -Root "\\dumpap3\tools" -Scope Global -Persist -Credential $creds
Import-Module "T:\_Pipeline\cobopipe_v02-001\PowerShell\Custom-Functions.psm1"
