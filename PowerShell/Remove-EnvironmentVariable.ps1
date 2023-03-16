function Remove-EnvironmentVariable {
     param (
     [Parameter(Mandatory=$true)][string]$Variable,
     [switch]$FromSystemEnvironment,
     [switch]$FromUserEnvironment
     )
     if ($FromSystemEnvironment){
          $envmachine = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
          if (($envmachine -split ";").Contains($Variable)){
               [Environment]::SetEnvironmentVariable("Path", $($envmachine.Replace($Variable, "")), [EnvironmentVariableTarget]::Machine)
          }elseif (($envmachine -split ";").Contains($Variable + "\")) {
               [Environment]::SetEnvironmentVariable("Path", $($envmachine.Replace($Variable, "")), [EnvironmentVariableTarget]::Machine)
          }
     }
     if ($FromUserEnvironment){
          $envuser = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)
          if (($envuser -split ";").Contains($Variable)){
               [Environment]::SetEnvironmentVariable("Path", $($envuser.Replace($Variable, "")), [EnvironmentVariableTarget]::User)
          }elseif (($envuser -split ";").Contains($Variable + "\")){
               [Environment]::SetEnvironmentVariable("Path", $($envuser.Replace($Variable, "")), [EnvironmentVariableTarget]::User)
           }
     }
}