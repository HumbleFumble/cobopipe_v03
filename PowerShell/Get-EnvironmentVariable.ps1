function Get-EnvironmentVariable {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)][string]$Variable
    )
    $envmachine = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine) 
    $envmachinesplit = $envmachine -split ";"
    if ($envmachinesplit.Contains($Variable)){Write-Host "True"}
}