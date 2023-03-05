
$applist = @(
    [pscustomobject]@{Name = "Maya"; Regex = "Autodesk Maya \d\d\d\d"},
    [pscustomobject]@{Name = "Python"; Regex = "Python ..... Executables *"},
    [pscustomobject]@{Name = "Adobe"; Regex = "Adobe*"},
    [pscustomobject]@{Name = "VLC"; Regex = "VLC*"},
    [pscustomobject]@{Name = "Toon Boom"; Regex = "Toon Boom*"},
    [pscustomobject]@{Name = "BlaBla"; Regex = "BlaBla*"}
)

$allresults = foreach($item in $applist) {
    
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
            "VLC" {Find-App}
            "Toon Boom" {Find-App}
            "Maya" {Find-App -Maya}
            Default {Find-App -Default}
        }
    }

$allresults