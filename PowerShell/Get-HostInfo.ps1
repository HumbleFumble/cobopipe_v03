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

# END Get-HostInfo 
#-------------------------------------------------------------------------------------------------------------------------------------------