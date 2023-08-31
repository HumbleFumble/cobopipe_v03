
param(
[Parameter(Mandatory=$true)][string]$Variable,
[String]$VariableKey="Path",
[Parameter()][Boolean]$ReplaceKey=$false,
[Boolean]$RemoveVarible=$false
)
Write-Host "Env Var: " $VariableKey
Write-Host "Removing: " $RemoveVarible
if (-Not $RemoveVarible){
     $envmachine = [Environment]::GetEnvironmentVariable($VariableKey, [EnvironmentVariableTarget]::Machine)
     Write-Host "HERE is current env: " $envmachine
     if($envmachine)

     {
         if ($true -eq $ReplaceKey)
         {
             [Environment]::SetEnvironmentVariable($VariableKey, $Variable, [EnvironmentVariableTarget]::Machine)
         }
         else
         {
             if (-Not $envmachine.Contains($Variable))
             {
                 Write-Host "Adding: " $envmachine
                 [Environment]::SetEnvironmentVariable($VariableKey, $( ($Variable + ";") + $envmachine ), [EnvironmentVariableTarget]::Machine)
             }

         }
     }else{
             Write-Host "not found the env" $envmachine
             [Environment]::SetEnvironmentVariable($VariableKey, $Variable, [EnvironmentVariableTarget]::Machine)
         }
}
else{
    $envmachine = [Environment]::GetEnvironmentVariable($VariableKey, [EnvironmentVariableTarget]::Machine)

    if($envmachine)
    {
        if ( -Not $envmachine.Contains(";"))
        {
            [Environment]::SetEnvironmentVariable($VariableKey,$null, [EnvironmentVariableTarget]::Machine)
        }else{
            if ( ($envmachine -split ";").Contains($Variable))
            {
                Write-Host "removing part of : " $envmachine
                [Environment]::SetEnvironmentVariable($VariableKey, $($envmachine.Replace($Variable+";", "") ), [EnvironmentVariableTarget]::Machine)
            }
            elseif (($envmachine -split ";").Contains($Variable + "\"))
            {
                Write-Host "removing part of : " $envmachine
                [Environment]::SetEnvironmentVariable($VariableKey, $($envmachine.Replace($Variable, "") ), [EnvironmentVariableTarget]::Machine)
            }

        }
    }
}

