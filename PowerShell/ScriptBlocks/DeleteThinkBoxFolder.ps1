
param (
    [Parameter(Mandatory, Position = 0)][string[]]$ComputerName
)
Set-ExecutionPolicy Bypass

$creds = Get-Credential -UserName cphbom\deadline -Message:$false
Invoke-Command -ComputerName $ComputerName -ScriptBlock { 
    $path = "C:\Users\deadline\AppData\Local\Thinkbox"
    Remove-Item -Path $path -Confirm:$false -Recurse
} -Credential $creds

Set-ExecutionPolicy Restricted