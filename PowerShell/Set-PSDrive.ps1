
param(
    [string]$DriveLetter
)
if (! $DriveLetter){
$DriveLetter = "T"
}

$whoami = whoami
$user = whoami /user
$sid = ($user -match $env:USERDOMAIN)[0].Replace($whoami + " ", "")
$DrivePath = "\\dumpap3\tools"
$Path = "REGISTRY::HKEY_USERS\$sid\Network"

if (! (Get-Item -Path $($Path + "\" + $DriveLetter) -ErrorAction SilentlyContinue)){
    New-Item -Path $Path -Name $DriveLetter
    New-ItemProperty -Path $Path\$DriveLetter\ -Name ConnectFlags -PropertyType DWORD -Value 0
    New-ItemProperty -Path $Path\$DriveLetter\ -Name ConnectionType -PropertyType DWORD -Value 1
    New-ItemProperty -Path $Path\$DriveLetter\ -Name DeferFlags -PropertyType DWORD -Value 4
    New-ItemProperty -Path $Path\$DriveLetter\ -Name ProviderName -PropertyType String -Value "Microsoft Windows Network"
    New-ItemProperty -Path $Path\$DriveLetter\ -Name ProviderType -PropertyType DWORD -Value 131072
    New-ItemProperty -Path $Path\$DriveLetter\ -Name RemotePath -PropertyType String -Value "$DrivePath"
    New-ItemProperty -Path $Path\$DriveLetter\ -Name UserName -PropertyType String
}else {
    Write-Output "Drive `"$DriveLetter`" already mapped"
}