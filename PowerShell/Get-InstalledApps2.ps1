
# List with numbers that need to excepted from the computers list
# $ExcludeList =  "1", "3", "7", "12","14", "15", "16", "18", "25", "30", "33"

$xmlfile = "C:\Users\plp\VsCodeProjects\cobopipe_v02-001\PowerShell\Get-InstalledApps2_config.xml"
[xml]$config = Get-Content $xmlfile
$ExcludeList = $config.settings.ChildNodes.Excludelist -split ","

# Declare new array
$numbers = @()

# For each number from 1 to 33, if the except list doesn't contain it, add it to $numbers array 
1..33 | ForEach-Object {
    if ($ExcludeList -notcontains $_){
        $numbers += $_ 
    }
}

# Declare new array
$ComputersList = @()

# Add "wsx" to each item and create new array. This creates array with the computer names
$numbers |  ForEach-Object { 
    $ComputersList += "wsx" + $_
}
$ComputersList
# # Get information about the computers in the array
# $newlist = foreach ($computer in $ComputersList){
#     Get-HostInfo -ComputerName $computer
# }


$applist = @(
    [pscustomobject]@{Name = "Python"; Regex = "Python ..... Executables *"},
    [pscustomobject]@{Name = "Maya"; Regex = "Autodesk Maya \d\d\d\d"},
    [pscustomobject]@{Name = "Adobe After Effects"; Regex = "Adobe After Effects*"},
    [pscustomobject]@{Name = "Adobe Media Encoder"; Regex = "Adobe Media Encoder*"},
    [pscustomobject]@{Name = "Adobe Photoshop"; Regex = "Adobe Photoshop*"},
    [pscustomobject]@{Name = "Adobe Premiere Pro"; Regex = "Adobe Premiere Pro*"},
    [pscustomobject]@{Name = "Adobe Acrobat"; Regex = "Adobe Acrobat*"},
    [pscustomobject]@{Name = "VLC"; Regex = "VLC*"},
    [pscustomobject]@{Name = "Deadline"; Regex = "Deadline*"},
    [pscustomobject]@{Name = "Chrome"; Regex = "Chrome*"},
    [pscustomobject]@{Name = "Firefox"; Regex = "Firefox*"},
    [pscustomobject]@{Name = "Fusion"; Regex = "Fusion*"},
    [pscustomobject]@{Name = "Toon Boom"; Regex = "Toon Boom Harmony 22 Premium*"}
)

$computers = Invoke-Command -ComputerName $ComputersList -ScriptBlock { 
foreach($item in $using:applist) {
    
    $Wow6432Node = "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
    $Microsoft = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*"
    function Find-App {
    param (
        [switch]$Maya,
        [switch]$Default
    )
    if ($Maya){
        $result = Get-ChildItem $Microsoft | Get-ItemProperty | Where-Object {$_.DisplayName -Match $item.Regex} | Where-Object {$_.DisplayVersion -notmatch "^\d\d\d\d"} | Select-Object Displayname, DisplayVersion
        if (!$result){
            $result = [pscustomobject]@{DisplayName =  $item.Name; DisplayVersion = ""; Status = "Missing"}
        }else{
            $result | Add-Member -MemberType NoteProperty -Name Status -Value "Installed"
        }
        $result
    }elseif ($Default) {
        $result = Get-ChildItem $Microsoft | Get-ItemProperty | Where-Object {$_.DisplayName -Match $item.Regex} | Select-Object Displayname, DisplayVersion
        if (!$result){$result = [pscustomobject]@{DisplayName =  $item.Name; DisplayVersion = ""; Status = "Missing"}
        }else{
            $result | Add-Member -MemberType NoteProperty -Name Status -Value "Installed"
        }
        $result
    }else {
        $result = Get-ChildItem $Wow6432Node | Get-ItemProperty | Where-Object {$_.DisplayName -Match $item.Regex} | Select-Object Displayname, DisplayVersion
        if (!$result){$result = [pscustomobject]@{DisplayName =  $item.Name; DisplayVersion = ""; Status = "Missing"}
        }else{
            $result | Add-Member -MemberType NoteProperty -Name Status -Value "Installed"
        }
        $result
            }
        }
        
        switch ($item.Name){
            "Adobe" {Find-App}
            "VLC" {Find-App -Default}
            "Toon Boom" {Find-App}
            "Maya" {Find-App -Maya}
            Default {Find-App -Default}
        }
    }
  $allresults
}

$computers | Where-Object {$_.status -eq "Missing"} | Select-Object -ExcludeProperty RunspaceId, PSShowComputerName, DisplayVersion, Status | ConvertTo-Json -Depth 4 | Out-File -FilePath "C:\Users\plp\VsCodeProjects\cobopipe_v02-001\PowerShell\applist.json"
# $computers | where {$_.status -eq "Installed" -and $_.displayname -eq "Toon Boom Harmony 22 Premium*"} | select DisplayName,  PSComputerName
# $computers | ft