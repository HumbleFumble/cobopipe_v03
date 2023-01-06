# This file goes to your local drive in: 'C:\Users\<User>\AppData\Roaming\Blackmagic Design\Fusion\Scripts\Comp'
# This will be the regular way a Fusion python tool should be set up

# Python 3.6 Imports access to Fusion directory on drive
import site
site.addsitedir("T:/_Pipeline/cobopipe-v02-001/AfterEffect/AE_Scripts/")

# Python 2.7 Imports access to Fusion directory on drive
# import sys
# sys.path.append("P:/tools/_Scripts/Production_scripts/KiwiStrit/Maya/Fusion")

import Fusion_Functions.__HelloWorld as HW

# Pass default fusion UI reference to the tool to give it access to fusion functionality
tool = HW.HelloWorld(fusion=fusion)

# # Proves the system works!
# tool.greetings()
# tool.printFusionReference()
# tool.printLoaderSavers()