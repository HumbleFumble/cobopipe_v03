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