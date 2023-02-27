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
function Uninstall-Python {
    get-cimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python ..... tcl*" | Invoke-CimMethod -MethodName Uninstall
    get-cimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python ..... pip*" | Invoke-CimMethod -MethodName Uninstall
    get-cimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python *" | Invoke-CimMethod -MethodName Uninstall
}
$python =  get-cimInstance -ClassName Win32_Product | Where-Object -Property Name -Match "python *"
$python | Where-Object -Property name -Match "tcl*" | Invoke-CimMethod -MethodName Uninstall
$python | Where-Object -Property name -Match "pip*" | Invoke-CimMethod -MethodName Uninstall
$python | Where-Object -Property name -Match "python*" | Invoke-CimMethod -MethodName Uninstall -ErrorAction SilentlyContinue