"""
This script is meant to run through and find all the computers and get the info on them saved out.1GB
Requires:
Windows 10: Go to Settings → Apps → Optional features → Add a feature. Find 'RSAT: Active Directory Domain Services and Lightweight Directory Tools' and install it.
Then in powershell (admin) run: Add-WindowsCapability -Online -Name Rsat.ActiveDirectory.DS-LDS.Tools~~~~0.0.1.0


"""


$computers = Get-ADComputer -Filter * | Sort-Object -Property Name | Select-Object -ExpandProperty Name

$results = @()

foreach ($computer in $computers) {
    try {
        $cpu = Get-WmiObject -Class Win32_Processor -ComputerName $computer | Select-Object -ExpandProperty Name
        $ram = Get-WmiObject -Class Win32_PhysicalMemory -ComputerName $computer | Measure-Object -Property Capacity -Sum | % { $_.Sum / 1GB }
        $gpu = Get-WmiObject -Class Win32_VideoController -ComputerName $computer | Select-Object -ExpandProperty Name
        $ip = (Get-WmiObject -Class Win32_NetworkAdapterConfiguration -ComputerName $computer | Where-Object { $_.IPAddress -ne $null }).IPAddress

        $results += [PSCustomObject]@{
            ComputerName = $computer
            CPU = $cpu
            RAM = "${ram} GB"
            GPU = $gpu
            IP = $ip -join ', '
        }
    } catch {
        Write-Warning "Failed to get info for $computer"
    }
}

# Print to screen
$results | Format-Table -AutoSize

# Save to CSV file
$filePath = "C:\Temp\Workstation_List.csv"  # Specify your desired file path
$results | Export-Csv -Path $filePath -NoTypeInformation

Write-Host "Results saved to $filePath"