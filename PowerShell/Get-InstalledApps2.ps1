
# List with numbers that need to excepted from the computers list
$ExcludeList =  "1", "3", "7", "12","14", "15", "16", "18", "25", "30", "33"

# Declare new array
$numbers = @()

# For each number from 1 to 33, if the except list doesn't contain it, add it to $numbers array 
1..33 | ForEach-Object {
    if ($ExcludeList -notcontains $_){
        $numbers += $_ 
    }
}

# Declare new array
$ComputersList = @()

# Add "wsx" to each item and create new array. This creates array with the computer names
$numbers |  ForEach-Object { 
    $ComputersList += "wsx" + $_
}

# Get information about the computers in the array
$newlist = foreach ($computer in $ComputersList){
    Get-HostInfo -ComputerName $computer
}

# ---------------------------------------------------------------------------------------------------

$applist = @{Maya = "^Autodesk Maya \d\d\d\d"; Python = "Python ..... Executables *"}#, "^Toon Boom*", "Adobe*", "Deadline*", "Chrome*", "Firefox*", "VLC*"

# ---------------------------------------------------------------------------------------------------
$computers = Invoke-Command -ComputerName $newlist.name -ScriptBlock {

    $Wow6432Node = "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
    $Microsoft = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"

    $using:applist | ForEach-Object {
         switch ($_){
            "Adobe*" {
                $n = Get-ChildItem $Wow6432Node | Get-ItemProperty | Where-Object -Property DisplayName -Match $_ | Select-Object Displayname, DisplayVersion
                $n
            }
            "VLC*" {
                $n = Get-ChildItem $Wow6432Node | Get-ItemProperty | Where-Object -Property DisplayName -Match $_ | Select-Object Displayname, DisplayVersion
                $n
            }
            "Toon Boom*" {
                $n = Get-ChildItem $Wow6432Node | Get-ItemProperty | Where-Object -Property DisplayName -Match $_ | Select-Object Displayname, DisplayVersion
                $n
            }
            Default {
                $n = Get-ChildItem $Microsoft | Get-ItemProperty | Where-Object -Property DisplayName -Match $_ | Select-Object Displayname, DisplayVersion
                $n
            }
        }
    }
}

$computers | Select-Object -Property * -ExcludeProperty PSShowComputerName, PSSourceJobInstanceId, RunspaceId | ConvertTo-Json | Out-File -FilePath "C:\users\plp\desktop\PowerShell\applist.json" | ConvertFrom-Json
$computers | Format-Table