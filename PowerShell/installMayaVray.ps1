Set-Executionpolicy Bypass
Start-Process -FilePath '\\dumpap3\tools\_Software\Maya\Maya2022-4\Maya2022extracted\Setup.exe' -ArgumentList "--silent" -Wait

Start-Sleep 10

do {
	Get-Process "setup"
	Start-Sleep 1
	}
	until(!(Get-Process "setup"))
 
Start-Process -FilePath "\\dumpap3\tools\_Software\Chaosgroup\vray_adv_52002_maya2022_x64.exe" -ArgumentList "-gui=0 -configFile=\\dumpap3\tools\_Software\Chaosgroup\config.xml -quiet=1 -auto" 

Set-Executionpolicy Restricted