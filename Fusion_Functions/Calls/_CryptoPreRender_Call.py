# This file goes to your local drive in: 'C:\Users\<User>\AppData\Roaming\Blackmagic Design\Fusion\Scripts\Comp'

import site
site.addsitedir("T:/_Pipeline/cobopipe_v02-001/")

# Simply import file from directory to execute
import Fusion_Functions.Fusion_Utility as FU
cur_class = FU.UtilityClass(fusion=fusion)
cur_class.CryptoPreRender()