

$creds = Get-Credential -UserName cphbom\deadline -Message:$false
$machine_list = 1..33

foreach($u in $machine_list)
{
    $ComputerName = "WSX" + $u
    Enter-PSSession -ComputerName $ComputerName -Credential $creds
    Set-ExecutionPolicy Bypass
    $ComputerName

    if (!(Test-Path T:))
    {
        New-PSDrive -Name "T" -PSProvider FileSystem -Root "\\dumpap3\tools" -Persist -Credential $creds
    }
    T:\_Software\Deadline\submitter_plugins\Maya\Installers\Maya-submitter-windows-installer.exe --mode unattended --install_type all
    Exit-PSSession
}



