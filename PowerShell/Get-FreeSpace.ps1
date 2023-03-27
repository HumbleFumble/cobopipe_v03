function Get-FreeSpace {
    
    param (
        [string]$DriveLetter
    )
    
    if (!($DriveLetter)){
        $DriveLetter = "C"
    }
    [math]::Round((Get-PSDrive $DriveLetter).Free /1GB, 2)

}