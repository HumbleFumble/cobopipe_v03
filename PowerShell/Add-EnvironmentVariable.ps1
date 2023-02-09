function Add-EnvironmentVariable {
    param (
    [Parameter(Mandatory=$true)][string]$Variable,
    [switch]$ToSystemEnvironment,
    [switch]$ToUserEnvironment,
    [switch]$AsFirstEntry
    )
    if ($ToSystemEnvironment){
         $envmachine = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
         if($AsFirstEntry){
              [Environment]::SetEnvironmentVariable("Path", $(($Variable + ";") + $envmachine), [EnvironmentVariableTarget]::Machine) 
         }else{
         [Environment]::SetEnvironmentVariable("Path", $($envmachine + $Variable), [EnvironmentVariableTarget]::Machine)
         }
    }
    if ($ToUserEnvironment){
         $envuser = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
         if($AsFirstEntry){
              [Environment]::SetEnvironmentVariable("Path", $(($Variable + ";") + $envuser), [EnvironmentVariableTarget]::User) 
         }else{
         [Environment]::SetEnvironmentVariable("Path", $($envuser + $Variable), [EnvironmentVariableTarget]::User)
         }
    }

}