# Silent PowerShell web install
# ------------------------------------------------------------------------------------------------------------------------------
Invoke-Expression "& { $(Invoke-RestMethod "https://aka.ms/install-powershell.ps1") } -UseMSI -quiet"

# Dynamic switch
# ------------------------------------------------------------------------------------------------------------------------------
$SwitchList | ForEach-Object {
    Write-Host "Choice"$([int]$SwitchList.IndexOf($_) + 1)":"  $SwitchList.name[$SwitchList.IndexOf($_)]
}
$var = Read-Host -Prompt "Enter switch number"
foreach ($i in $SwitchList){
    switch ($var){
        ([int]$SwitchList.IndexOf($i) + 1) {$SwitchList.name[$SwitchList.IndexOf($i)]}
    }
}



# -----------------------------------------------------------------------------
# Run bat files remotely
#------------------------------------------------------------------------------
# The drive from which the bat file is being executed needs to be mapped. 
# The "persit" switch ensures the drive persits in new sessions
# Make sure PowerShell has been ran as administrator
# Mapping the drive
New-PSDrive -Name "T" -Root "\\dumpap3\tools" -PSProvider "FileSystem" -Persist

# Run the file
& "T:\_Pipeline\cobopipe_v02-001\BAT_files\update_harmony_hotbar.bat"

# Remove-PSDrive -Name "T" -force   # Remove drive
# Get-PSDrive   # List of currently mapped drives
# Check if the drive has already been mapped
# if ((Get-PSDrive).Name.Contains("T")){"It does"}


# Get remaining space on "C:\" drive
# -------------------------------------------------------------------------------------------------------------
[string][math]::Round((Get-Volume -DriveLetter "C").SizeRemaining/1GB, 2) + "GB"
# Or create object and use it with Invoke-Command -ComputerName <computer> -ScriptBlock {<command>}
$remaining = [math]::Round((Get-Volume -DriveLetter "C").SizeRemaining/1GB, 2)
$table = [pscustomobject]@{FreeSpaceGB = "$remaining"}
$table

# Install chocolatey
#-----------------------------------------------------------------------------------------------------------------------
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))


# Remove drive registry key
#-----------------------------------------------------------------------------------------------------------------------
Remove-Item -Path $("$Path" + "\" + "$DriveLetter")


# Get remaining free space
#-----------------------------------------------------------------------------------------------------------------------
(get-ciminstance -ClassName Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace /1gb -as [int]


# Script template for running remote installations
#-----------------------------------------------------------------------------------------------------------------------
$creds = Get-Credential -UserName cphbom\plp -Message:$false

Invoke-Command -ComputerName wsx2 -ScriptBlock { 
New-PSDrive -Name "T" -PSProvider FileSystem -Root "\\dumpap3\tools" -Persist -Credential $using:creds
Import-Module "T:\_Pipeline\cobopipe_v02-001\PowerShell\Custom-Functions.psm1"

}