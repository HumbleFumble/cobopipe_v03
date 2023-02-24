#-------------------------------------------------------------------------------------------------------------------------------------------
function Rename-File {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)][string]$MatchString,
        [Parameter(Mandatory = $true)][string]$Directory,
        [switch]$FullPath,
        [switch]$Rename        
    )
    $items = Get-ChildItem -Path $Directory -Recurse
    $newlist = New-Object System.Collections.ArrayList
    ForEach ($item in $items){
        if($item.BaseName -match $MatchString){
            if ($FullPath){
                Write-Host "Match found in" $item.Directory.Parent.Name " - " $item.FullName
                $newlist += $item
            }else{
                Write-Host "Match found in" $item.Directory.Parent.Name
                $newlist += $item
            }
        }
    }
    
    if(!$newlist){
        Write-Host "No item matching basename `"$MatchString`" was found" -ForegroundColor Yellow
    break
    }else{
        
        $index = 0
        if ($Rename){
            $renamefile = Read-Host -Prompt "`nRename files? [y/n]"
            if ($renamefile -eq "y"){
                $name = Read-Host -Prompt "`nEnter new name"
                ForEach ($item in $items){
                    if($item.BaseName -match $MatchString){
                        $newname = $item.Directory.FullName + "\" + $name + $item.Extension
                        Rename-Item -Path $item.FullName -NewName "$newname"
                        if (Test-Path -Path $newname){
                        $index += 1
                        }
                    }
                }
                Write-Host "`n"$index "out of"$newlist.Count "items successfully renamed!" -ForegroundColor Green
            }
        }
    }
    return $newlist.Directory.Parent.FullName | Sort-Object | Get-Unique
}
# END Rename-File
#-------------------------------------------------------------------------------------------------------------------------------------------