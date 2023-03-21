function Update-CustomFunctions {
    $functions = "Add-EnvironmentVariable.ps1", 
                 "Enter-RemoteSession.ps1", 
                 "Get-HostInfo.ps1", 
                 "Install-App.ps1", 
                 "Remove-EnvironmentVariable.ps1", 
                 "Rename-File.ps1", 
                 "Set-SecurityLevel.ps1",
                 "Get-EnvironmentVariable.ps1",
                 "Set-ComputersList.ps1",
                 "Update-CustomFunctions.ps1"


    
    if ((Get-CimInstance -Namespace root/CIMV2 -ClassName Win32_ComputerSystem).Domain){
        $functionsdir = "C:\Users\plp\VsCodeProjects\cobopipe_v02-001\PowerShell\"
    }
    
    Clear-Content "C:\Users\plp\VsCodeProjects\cobopipe_v02-001\PowerShell\Custom-Functions.psm1"

    $functionslist = foreach ($i in $functions){$functionsdir + $i}
    $functionslist | ForEach-Object {Get-Content $_ | Add-Content ($functionsdir + "Custom-Functions.psm1")}
    
    
}
