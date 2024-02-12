$username = "CPHAFID1\afirender"
$credential = Get-Credential -UserName $username -Message "Enter password for $username"

#$simple_computers = Get-Content -Path "C:\Temp\NetworkSpeed_ComputerList.txt"
$simple_computers = @('RN501')
$prefix = 'CPHAFID1-'
$computers = $simple_computers | ForEach-Object { $prefix + $_ }

Invoke-Command -ComputerName $computers -ScriptBlock {
    $computerName = $env:COMPUTERNAME
    $networkAdapters = Get-WmiObject -Class Win32_NetworkAdapter | Where-Object { $_.NetEnabled -eq $true }
    foreach ($adapter in $networkAdapters) {
        $speedMbps = [math]::Round($adapter.Speed / 1MB)
        [PSCustomObject]@{
            ComputerName = $computerName
            SpeedMbps = $speedMbps
            Adapter = $adapter.Name
        }
    }
} -Credential $credential | Format-Table -Property ComputerName, Adapter, SpeedMbps -AutoSize
