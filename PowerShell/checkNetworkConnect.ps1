$username = "CPHAFID1\afirender"
$credential = Get-Credential -UserName $username -Message "Enter password for $username"

$computers = @('CPHAFID1-WS090', 'CPHAFID1-WS114', 'CPHAFID1-WS130')

Invoke-Command -ComputerName $computers -ScriptBlock {
    $computerName = $env:COMPUTERNAME
    $networkAdapters = Get-WmiObject -Class Win32_NetworkAdapter | Where-Object { $_.NetEnabled -eq $true }
    foreach ($adapter in $networkAdapters) {
        $speedMbps = [math]::Round($adapter.Speed / 1MB)
        [PSCustomObject]@{
            ComputerName = $computerName
            SpeedMbps = $speedMbps
        }
    }
} -Credential $credential | Format-Table -Property ComputerName, SpeedMbps -AutoSize
