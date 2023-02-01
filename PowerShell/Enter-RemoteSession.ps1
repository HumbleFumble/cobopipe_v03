
# Basic remote session function with two mandatory parameters - computer name and username
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
    do { # Try to open
        Start-Sleep -Milliseconds 300
        Write-Host "Connecting..."
    # Remote session with appropriate name (computername/session/session number)
        $session = New-PSSession -Name ($ComputerName + "RS" + $prefix) -ComputerName $computername -Credential $creds
        $index += 1
    }until (
    # Keep trying until is open
        Get-PSSession
    )
    
    if ($?){
        Write-Host "Successfully connected to $ComputerName!`n"
        $readhost = Read-Host "Enter session? [y/n]"
        if ($readhost -eq "Y"){
            Enter-PSSession $session
        }
        else {
            continue
        }    
    }
    else {
        Write-Host "`n;Something went wrong :("
    }
}