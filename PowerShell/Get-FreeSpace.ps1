function Get-FreeSpace {
$FreeSpace = (get-ciminstance -ClassName Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace /1gb -as [int]
$table = [pscustomobject]@{FreeSpace = "$FreeSpace"; Unit = "GB"}
$table
}