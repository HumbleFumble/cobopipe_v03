function Get-EnvironmentVariable {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)][string]$Variable,
        [switch]$FromSystemEnvironment,
        [switch]$FromUserEnvironment
    )
    if ($FromSystemEnvironment){
        $envmachine = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine) 
        $envmachinesplit = $envmachine -split ";"
        if ($envmachinesplit.Contains($Variable)){
            Write-Output "Variable FOUND in system path"
        }
        elseif ($envmachinesplit.Contains($Variable + "\")) {
            Write-Output "Variable FOUND in system path"
        }
        else {
            Write-Output "Variable NOT FOUND in system path"
        }
    }elseif ($FromUserEnvironment) {
        
        $envuser = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User) 
        $envmachinesplit = $envuser-split ";"
        if ($envmachinesplit.Contains($Variable)){
            Write-Output "Variable found in user path"
        }else {
            Write-Output "Variable not found in user path"
        }
        
    }

}