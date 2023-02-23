# Web install PowerShell silent
# ------------------------------------------------------------------------------------------------------------------------------
iex "& { $(irm https://aka.ms/install-powershell.ps1) } -UseMSI -quiet"

# Dynamic switch
# ------------------------------------------------------------------------------------------------------------------------------
$SwitchList | ForEach-Object {
    Write-Host "Choice"$([int]$SwitchList.IndexOf($_) + 1)":"  $SwitchList.name[$SwitchList.IndexOf($_)]
}
$var = Read-Host -Prompt "Enter switch number"
foreach ($i in $SwitchList){
    switch ($var){
        ([int]$SwitchList.IndexOf($i) + 1) {$SwitchList.name[$SwitchList.IndexOf($i)]}
    }
}

# Uninstall Python
get-cimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python 3.9.1 tcl*" | Invoke-CimMethod -MethodName Uninstall
get-cimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python 3.9.1 pip*" | Invoke-CimMethod -MethodName Uninstall
get-cimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python 3.9.1*" | Invoke-CimMethod -MethodName Uninstall