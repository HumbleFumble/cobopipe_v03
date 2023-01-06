# This file goes to your local drive in: 'C:\Users\<User>\AppData\Roaming\Blackmagic Design\Fusion\Scripts\Comp'

# Python 3.6 Imports access to Fusion directory on drive
import site
site.addsitedir("T:/_Pipeline/cobopipe-v02-001/AfterEffect/AE_Scripts/")

# Python 2.7 Imports access to Fusion directory on drive
# import sys
# sys.path.append("P:/tools/_Scripts/Production_scripts/KiwiStrit/Maya/Fusion")

# Simply import file from directory to execute
import Fusion_Functions.CreateNewFromComp as CNFC
CNFC.run(fusion=fusion, composition=composition)