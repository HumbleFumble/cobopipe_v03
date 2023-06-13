import site
#site.addsitedir("T:/_Pipeline/cobopipe_v02-001/")
site.addsitedir("C:/Users/cg/PycharmProjects/cobopipe_v02-001/")

# Simply import file from directory to execute
import Fusion_Functions.Fusion_Utility as FU
cur_class = FU.UtilityClass(fusion=fusion)
cur_class.FindLoaders()