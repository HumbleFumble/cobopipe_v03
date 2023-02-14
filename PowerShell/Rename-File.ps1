#-------------------------------------------------------------------------------------------------------------------------------------------
function Rename-File {
    param (
        [Parameter(Mandatory = $true)][string]$MatchString,
        [Parameter(Mandatory = $true)][string]$Directory,
        [switch]$FullPath,
        [switch]$Rename        
    )
    $items = Get-ChildItem -Path $Directory -Recurse
    $new = New-Object System.Collections.ArrayList
    #------------------------------------------------------------------------------------------------------
    ForEach ($item in $items){
        if($item.BaseName -match $MatchString){
            if ($FullPath){
                Write-Host "Match found in" $item.Directory.Parent.Name " - " $item.Directory
                $new += $item
            }else{
                Write-Host "Match found in" $item.Directory.Parent.Name
                $new += $item
            }
        }
    }
    #------------------------------------------------------------------------------------------------------
    if($new = $null){
        Write-Host "No item matching basename `"$MatchString`" was found" -ForegroundColor Yellow
    }else {
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
                Write-Host "`n"$index "out of"$new.Count "items successfully renamed!" -ForegroundColor Green
            }
        }
    }
}
# END Rename-File
#-------------------------------------------------------------------------------------------------------------------------------------------


ForEach ($item in $items){
    if($item.BaseName -match $MatchString){
        if ($FullPath){
            Write-Host "Match found in" $item.Directory.Parent.Name " - " $item.Directory
            $new += $item
        }else{
            Write-Host "Match found in" $item.Directory.Parent.Name
        $new += $item
        }
    }
}