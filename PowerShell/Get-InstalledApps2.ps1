#-------------------------------------------------------------------------------------------------------------------------------------------
function Get-HostInfo {
    param (
        [Parameter(Mandatory=$true)][string]$ComputerName,
        [switch]$IPAddress,
        [switch]$CurrentUser,
        [switch]$WinRMStatus
    )
    
    $ComputerInfo = [pscustomobject]@{
        Name        = "$ComputerName"
        IPAddress   = ""
        CurrentUser = ""
        WinRMStatus = ""
    }

    switch ($true) {
        
        $IPAddress {
            if(!($ComputerName)){
                Write-Host "Please enter host name and try again" -ForegroundColor Yellow
                break
            }else {
                try {
                    $ComputerInfo.IPAddress = [System.Net.Dns]::GetHostAddresses($ComputerName).IPAddressToString
                } catch{
                    Write-Host "No such host is known" -ForegroundColor Red
                }
            }
        }
        
        $CurrentUser {
            if(!($ComputerName)){
                Write-Host "Please enter host name and try again" -ForegroundColor Yellow
                break
            }else {
                $username = Invoke-Command -ComputerName $ComputerName -ScriptBlock {
                    # if ((Get-NetFirewallRule -DisplayGroup "File and printer sharing").Disabled){
                    #     Set-NetFirewallRule -DisplayGroup "File And Printer Sharing" -Profile "Domain" -Enabled True
                    # }
                $queryResults = (qwinsta /server:$ComputerName | ForEach-Object { (($_.trim() -replace '\s+',',')) } | ConvertFrom-Csv)
                foreach ($i in $queryResults){
                    if($i.STATE -eq "Active"){
                        $i.USERNAME
                    }
                } 
                }
                $ComputerInfo.CurrentUser = $username 
            }
        }
        
        $WinRMStatus {
            if(!($ComputerName)){
            Write-Host "Please enter computer name and try again" -ForegroundColor Yellow
            break
            }else {
                if (Test-WSMan -ComputerName $ComputerName -ErrorAction SilentlyContinue){
                    $ComputerInfo.WinRmStatus = "Available"
                }else {
                    Write-Host "$ComputerName unreachable" -ForegroundColor Red
                }                
            }
        }
        
        Default {          
            if (Test-WSMan $ComputerName){
                Write-Host "$ComputerName available and configured" -ForegroundColor Green
            }else {
                Write-Host "$ComputerName unreachable" -ForegroundColor Red
            }
        }
    }
    return $ComputerInfo
}


# ---------------------------------------------------------------------------------------------------
# Requires Get-HostInfo!!!
# ---------------------------------------------------------------------------------------------------

# List with numbers that need to excepted from the computers list
$exceptnumbers =  "1", "3", "7", "12","14", "15", "16", "18", "25", "30", "33"

# Declare new array
$numbers = @()

# For each number from 1 to 33, if the except list doesn't contain it, add it to $numbers array 
1..33 | ForEach-Object {
    if ($exceptnumbers -notcontains $_){
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
$newlist = foreach ($i in $ComputersList){
    Get-HostInfo -ComputerName $i -WinRMStatus -IPAddress -CurrentUser
}

# ---------------------------------------------------------------------------------------------------

$applist = "^Autodesk Maya \d\d\d\d", "Python ..... Executables *"#, "^Toon Boom*", "Adobe*", "Deadline*", "Chrome*", "Firefox*", "VLC*"

# ---------------------------------------------------------------------------------------------------
$computers = Invoke-Command -ComputerName $newlist.name -ScriptBlock {

    $using:applist | ForEach-Object {
         switch ($_){
             "Adobe*"     {$n = Get-ChildItem "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" | Get-ItemProperty | Where-Object -Property DisplayName -Match $_ | Select-Object Displayname, DisplayVersion
                           $n}
             "VLC*"       {$n = Get-ChildItem "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" | Get-ItemProperty | Where-Object -Property DisplayName -Match $_ | Select-Object Displayname, DisplayVersion
                           $n}
             "Toon Boom*" {$n = Get-ChildItem "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" | Get-ItemProperty | Where-Object -Property DisplayName -Match $_ | Select-Object Displayname, DisplayVersion
                           $n}
             Default  {$n = Get-ChildItem "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" | Get-ItemProperty | Where-Object -Property DisplayName -Match $_ | Select-Object Displayname, DisplayVersion
                           $n}
         }
     }
   
}

$computers |  Select-Object -Property * -ExcludeProperty PSShowComputerName, PSSourceJobInstanceId, RunspaceId | ConvertTo-Json | Out-File -FilePath "C:\users\plp\desktop\PowerShell\applist.json" | ConvertFrom-Json
$computers | ft