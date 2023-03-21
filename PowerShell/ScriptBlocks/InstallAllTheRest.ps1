Start-Transcript -path C:\Users\$env:USERNAME\Desktop\autoInstallLog.txt -append

# Powershell silent web install; Check if PowerShell 7 has been istaled on the system
if (! (Test-Path -Path "C:\Program Files\PowerShell\7\pwsh.exe")){
    Invoke-Expression "& { $(Invoke-RestMethod https://aka.ms/install-powershell.ps1) } -UseMSI -quiet"
}else {
    Write-Host "`nPowerShell 7 already installed on this system"
}

# Install Chocolatey
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; 
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

Start-Sleep 5

# Install apps via Chocolatey
choco install nuget.commandline     # Install NuGet
choco install dotnet-6.0-sdk -y     # Install .NET
nuget help | Select-Object -First 1 # Get NuGet version
choco install vlc -y                # VLC Player
choco install GoogleChrome -y       # Chrome
choco install firefox -y            # Firefox
choco install QuickTime -y          # QuickTime
choco install winrar -y             # WinRar