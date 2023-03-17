param (
    [switch]$SetTime
)

if ($SetTime){
    $AtTime = $SetTime
}else {
    $AtTime = Get-Date -Format "HH:mm"
}

Write-Output $AtTime