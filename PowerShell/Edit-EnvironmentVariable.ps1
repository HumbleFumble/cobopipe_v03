function Edit-EnvironmentVariable {
    param(
    [Parameter(Mandatory=$true)][string]$Variable,
    [String]$VaribleKey="Path",
    [Parameter()][Boolean]$ReplaceKey=$false,
    [Boolean]$RemoveVarible=$false
    )
    Write-Host "Env Var: " $VaribleKey
    Write-Host "Removing: " $RemoveVarible
    if (-Not $RemoveVarible){
         $envmachine = [Environment]::GetEnvironmentVariable($VaribleKey, [EnvironmentVariableTarget]::Machine)
         Write-Host "HERE is current env: " $envmachine
         if($envmachine)
         {
             if ($true -eq $ReplaceKey)
             {
                 [Environment]::SetEnvironmentVariable($VaribleKey, $Variable, [EnvironmentVariableTarget]::Machine)
             }
             else
             {
                 if (-Not $envmachine.Contains($Variable))
                 {
                     Write-Host "Adding: " $envmachine
                     [Environment]::SetEnvironmentVariable($VaribleKey, $( ($Variable + ";") + $envmachine ), [EnvironmentVariableTarget]::Machine)
                 }

             }
         }else{
                 Write-Host "not found the env" $envmachine
                 [Environment]::SetEnvironmentVariable($VaribleKey, $Variable, [EnvironmentVariableTarget]::Machine)
             }
    }
    else{
        $envmachine = [Environment]::GetEnvironmentVariable($VaribleKey, [EnvironmentVariableTarget]::Machine)

        if($envmachine)
        {
            if ( -Not $envmachine.Contains(";"))
            {
                [Environment]::SetEnvironmentVariable($VaribleKey,$null, [EnvironmentVariableTarget]::Machine)
            }else{
                if ( ($envmachine -split ";").Contains($Variable))
                {
                    Write-Host "removing part of : " $envmachine
                    [Environment]::SetEnvironmentVariable($VaribleKey, $($envmachine.Replace($Variable+";", "") ), [EnvironmentVariableTarget]::Machine)
                }
                elseif (($envmachine -split ";").Contains($Variable + "\"))
                {
                    Write-Host "removing part of : " $envmachine
                    [Environment]::SetEnvironmentVariable($VaribleKey, $($envmachine.Replace($Variable, "") ), [EnvironmentVariableTarget]::Machine)
                }

            }
        }
    }

}