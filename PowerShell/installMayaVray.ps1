Invoke-Command -ComputerName wsx22 -ScriptBlock {
	Start-Process -FilePath '\\WSX3\shared\Maya2022extracted\Setup.exe' -ArgumentList "--silent" -Wait
	
	Start-Sleep 5
	
	do {
		Get-Process "setup"
		Start-Sleep 1
		}
		until(!(Get-Process "setup"))
	 
	Start-Process -FilePath "\\WSX3\shared\VRay\vray_adv_52002_maya2022_x64.exe" -ArgumentList "-gui=0 -configFile=\\WSX3\shared\VRay\VRayConfig.xml -quiet=1 -auto" 
	}