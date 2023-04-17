[string]$userName = 'cphbom\deadline'
[string]$userPassword = 'lids2.beth'

# Convert to SecureString
[securestring]$secStringPassword = ConvertTo-SecureString $userPassword -AsPlainText -Force

#$creds = Get-Credential -UserName cphbom\deadline
$creds = New-Object System.Management.Automation.PSCredential ($userName, $secStringPassword)
$job = Start-Job {$path = "C:\Users\deadline\AppData\Local\Thinkbox"
    Remove-Item -Path $path -Confirm:$false -Recurse} -cred $creds
Wait-Job $job
Receive-Job $job

