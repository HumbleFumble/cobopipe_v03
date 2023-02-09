function Remove-EnvironmentVariable {
     param (
     [Parameter(Mandatory=$true)][string]$Variable,
     [switch]$FromSystemEnvironment,
     [switch]$FromUserEnvironment
     )
     if ($FromSystemEnvironment){
          $envmachine = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::Machine)
          if ($envmachine -split ";"[0] -eq $Variable){
            [Environment]::SetEnvironmentVariable("Path", $($envmachine.Replace($Variable + ";", "")), [EnvironmentVariableTarget]::Machine)
          }else {
            [Environment]::SetEnvironmentVariable("Path", $($envmachine.Replace(";" + $Variable, "")), [EnvironmentVariableTarget]::Machine)
          }

     }
     if ($FromUserEnvironment){
          $envuser = [Environment]::GetEnvironmentVariable("Path", [EnvironmentVariableTarget]::User)

          if ($envuser -split ";"[0] -eq $Variable){
            [Environment]::SetEnvironmentVariable("Path", $($envuser.Replace($Variable + ";", "")), [EnvironmentVariableTarget]::User)
          }else {
            [Environment]::SetEnvironmentVariable("Path", $($envuser.Replace(";" + $Variable, "")), [EnvironmentVariableTarget]::User)
          }
     }

}