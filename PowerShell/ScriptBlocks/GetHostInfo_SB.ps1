
$numbers = 1..33

# Declare new array
$ComputersList = @()

# Add "wsx" to each item and create new array. This creates array with the computer names
$numbers |  ForEach-Object { 
    $ComputersList += "wsx" + $_
}

# Get information about the computers in the array. Get-HostInfo gather information for each computer in the list
$newlist = foreach ($computer in $ComputersList){
    Get-HostInfo -ComputerName $computer -WinRMStatus -CurrentUser -IPAddress
}
$newlist | Select-Object name, winrmstatus | ConvertTo-Json -Depth 4 | Out-File -FilePath "C:\Users\plp\VsCodeProjects\cobopipe_v02-001\PowerShell\complist.json"
