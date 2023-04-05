net use t: \\dumpap3\tools
T:
pwsh -Command "Set-ExecutionPolicy Bypass;& T:/_Pipeline/cobopipe_v02-001/PowerShell/ScriptBlocks/DeleteThinkBoxFolder.ps1"
PAUSE