function Remove-ThinkBoxFolder-WithLaunchControl {
    param (
        [Parameter()][string[]]$ComputerName = "computername"
    )
    & deadlinecommand.exe -RemoteControl $ComputerName StopSlave
    $creds = Get-Credential -UserName cphbom\deadline -Message:$false
    Invoke-Command -ComputerName $ComputerName -ScriptBlock {

        $path = "C:\Users\deadline\AppData\Local\Thinkbox"
        Remove-Item -Path $path -Confirm:$false -Recurse

    } -Credential $creds
    & deadlinecommand.exe -RemoteControl $ComputerName LaunchSlave
}
