#-------------------------------------------------------------------------------------------------------------------------------------------
function Rename-File {
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
                Write-Host "Match found in" $item.Directory.Parent.Name " - " $item.Directory
                $newlist += $item
            }else{
                Write-Host "Match found in" $item.Directory.Parent.Name
            $newlist += $item
            }
        }
    }
    if(!($newlist)){
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

# ForEach ($item in $items){
#     if($item.BaseName -match $MatchString){
#         if ($FullPath){
#             Write-Host "Match found in" $item.Directory.Parent.Name " - " $item.Directory
#             $new += $item
#         }else{
#             Write-Host "Match found in" $item.Directory.Parent.Name
#         $new += $item
#         }
#     }
# }

# Display only non-matching results
#
# foreach ($item in $items){
#     if ($null -eq $newlist[$list.IndexOf($item)]){
#         $newlist.Add($item)
#     }else{
#         foreach ($n in $newlist){
#             if ($n -ne $item){
#                 $newlist.Add($item)
#             }
#         }
#     }
# }