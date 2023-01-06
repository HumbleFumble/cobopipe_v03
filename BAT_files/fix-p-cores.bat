@echo off
powercfg /powerthrottling disable /path "C:\Program Files\Autodesk\Maya2020\bin\mayabatch.exe"
powercfg /powerthrottling disable /path "C:\Program Files\Autodesk\Maya2020\bin\maya.exe"
EXIT /B 0