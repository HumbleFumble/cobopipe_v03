function Update-CustomFunctions {
    $functions = "Add-EnvironmentVariable.ps1", 
                 "Enter-RemoteSession.ps1", 
                 "Get-HostInfo.ps1", 
                 "Install-App.ps1", 
                 "Remove-EnvironmentVariable.ps1", 
                 "Rename-File.ps1", 
                 "Set-SecurityLevel.ps1",
                 "Get-EnvironmentVariable.ps1",
                 "Update-CustomFunctions.ps1"

    $functionsdir = "C:\Users\plp\VsCodeProjects\cobopipe_v02-001\PowerShell\" 
    $functionslist = foreach ($i in $functions){$functionsdir + $i}
    $functionslist | ForEach-Object {Get-Content $_ | Add-Content "C:\Users\$env:username\VsCodeProjects\cobopipe_v02-001\PowerShell\Custom-Functions.psm1"}
    
    Import-Module "C:\Users\$env:username\VsCodeProjects\cobopipe_v02-001\PowerShell\Custom-Functions.psm1"

    if (Get-Command -module Custom-Functions){
        Write-Host "`nModule `"Custom-Functions`" loaded and ready`n" 
    }else{
        Write-Host "`nModule `"Custom-Functions`" could not be loaded`n" -ForegroundColor Red
    }

}