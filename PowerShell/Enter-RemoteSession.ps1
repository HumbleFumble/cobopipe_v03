
# Basic remote session function with two mandatory parameters - computer name and username
function Enter-RemoteSession {
    param (
    [Parameter(Mandatory=$true)][string]$UserName,
    [Parameter(Mandatory=$true)][string]$ComputerName
    )
    
    $sessionName = $ComputerName + " RS"
    $creds = Get-Credential -UserName $username
    $session = New-PSSession -Name $sessionName -ComputerName $computername -Credential $creds
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
    else {Write-Host "`n;Something went wrong :("}
    
}