Set-UAC -Off

#Log 
Start-Transcript -path C:\Users\$env:USERNAME\Desktop\autoInstallLog.txt -append

Import-Module "C:\Program Files\PowerShell\7\Modules\Custom-Functions"

# Powershell silent web install
if (! (Test-Path -Path "C:\Program Files\PowerShell\7\pwsh.exe")){
    Invoke-Expression "& { $(Invoke-RestMethod https://aka.ms/install-powershell.ps1) } -UseMSI -quiet"
}else {
    Write-Host "`nPowerShell 7 already installed on this system"
}

[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; 
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

Start-Sleep 5

choco install nuget.commandline
choco install dotnet-6.0-sdk -y
nuget help | Select-Object -First 1
choco install vlc -y
choco install GoogleChrome -y
choco install firefox -y
choco install QuickTime -y
choco install winrar -y

Set-UAC -On