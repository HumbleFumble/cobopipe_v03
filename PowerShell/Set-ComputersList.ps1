
function Set-ComputersList {
    [CmdletBinding()]
    param (
        [Parameter][string[]]$ExcludeList
    )

    $numbers = @()
    1..33 | ForEach-Object {
        if ($ExcludeList -notcontains $_){
            $numbers += $_ 
        }
    }
    $ComputersList = @()
    $numbers |  ForEach-Object { 
        $ComputersList += "wsx" + $_
    }
    $ComputersList
}