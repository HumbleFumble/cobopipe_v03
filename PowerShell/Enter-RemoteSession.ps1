# Basic remote session function with two mandatory parameters - computer name and username
#------------------------------------------------------------------------------------------------------------------------
function Enter-RemoteSession {
    param (
        [Parameter(Mandatory=$true)][string]$UserName,
        [Parameter(Mandatory=$true)][string]$ComputerName
    )
    
    # Get credentials
    $creds = Get-Credential -UserName $username
      
    # Check if there is already opened session and set the prefix as enumerator
    $prefix = ((Get-PSSession).ComputerName.count + 1)
    $index = 0
    $session = $null
    
    Write-Host "`nConnecting..."
    do { # Try and try to open
        Start-Sleep -Milliseconds 500
    # Remote session with appropriate name (computername/session/session number)
        $session = New-PSSession -Name ($ComputerName + "RS" + $prefix) -ComputerName $computername -Credential $creds
        $index += 1
    }until (
    # Until it's open
        Get-PSSession
    )
    # Option to enter the session     
    if ($session.Availability -eq 'Available' -and $session.State -eq 'Opened'){
        Write-Host "`nSuccessfully connected to $ComputerName!" -ForegroundColor Green
        $readhost = Read-Host "`nEnter session? [y/n]"
        if ($readhost -eq "Y"){
            Enter-PSSession $session
        }
        else {
            continue
        }    
    }
    else {
        Write-Host "`nCould not establish connection to $ComputerName" -ForegroundColor Red
    }
}