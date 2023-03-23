

#To connect with deadline user:
$creds = Get-Credential -UserName cphbom\deadline -Message:$false
#Start-Process pwsh -Credential $creds

$numbers = 15..15
# Declare new array
$ComputersList = @()
# Add "wsx" to each item and create new array. This creates array with the computer names
$numbers |  ForEach-Object {
    $ComputersList += "WSX" + $_
}

# Get information about the computers in the array. Get-HostInfo gather information for each computer in the list
#$newlist = foreach ($computer in $ComputersList){
#    Get-HostInfo -ComputerName $computer -WinRMStatus -CurrentUser -IPAddress
#}
#$newlist


#To remove folder:
$path = "C:\Users\deadline\AppData\Local\Thinkbox\"

#Close the first terminal

foreach($ws in $ComputersList){
    Invoke-Command -ComputerName $ws -Credential $creds -ScriptBlock { Remove-Item -Path $using:path -Confirm:$false -Recurse }
}







