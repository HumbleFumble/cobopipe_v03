
# List with numbers that need to excepted from the computers list
$exceptnumbers =  "1", "12", "15", "16", "25", "30", "33"

# Declare new array
$numbers = @()

# For each number from 1 to 33, if the except list doesn't contain it, add it to $numbers array 
1..33 | ForEach-Object {if ($exceptnumbers -notcontains $_){$numbers += $_ }}

# Declare new array
$ComputersList = @()

# Add "wsx" to each item and create new array. This creates array with the computer names
$numbers |  ForEach-Object { $ComputersList += "wsx" + $_}

# Get information about the computers in the array
$newlist = foreach ($i in $ComputersList){Get-HostInfo -ComputerName $i -WinRMStatus -IPAddress -CurrentUser}

$applist = "^Autodesk Maya \d\d\d\d", "python*", "^Toon Boom*", "Deadline*"

# Run on remote computer. Invoke-Commmand accepts list as ComputerName and runs parallelly by default
# $result variable collects all the results a can be further broken down by computer if necessary
$result = Invoke-Command -ComputerName $newlist.name -ScriptBlock {

# Get list with all entries in Win32_Product
$list = Get-CimInstance -ClassName Win32_Product

# Decalre empty list
$newlist = @()

# Import $applist from local computer and match each entry against the list with installed apps
$using:applist | ForEach-Object {$newlist += $list | Where-Object -Property Name -Match $_ | Select-Object name, version}

# Add a property to the list, containing the computer name
$newlist | Add-Member -MemberType NoteProperty -Name "Computer" -Value $env:COMPUTERNAME
$newlist
}

# Sort the result
$format = foreach ($i in $ComputersList) {
$result | Where-Object {$_.Computer -like $i} | Select-Object -Property name, version, computer
"---------------------------------------------------------------------------"
}

$format