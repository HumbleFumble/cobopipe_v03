from Log.CoboLoggers import getLogger
logger = getLogger()
from getConfig import getConfigClass
CC = getConfigClass()

try:
    import maya.cmds as cmds
    in_maya=True
except:
    in_maya=False
import PublishReport
import Maya_Functions.yeti_util_functions as yeti_util
import subprocess


def stritHairOff(asset_name="Strit",file_path=""):
    cmds.file(file_path, open=True, f=True)
    asset_yeti = cmds.ls("*::%s*:yetiNode_BodyShape" % asset_name)
    if asset_yeti:
        asset_yeti = asset_yeti[0]
        cmds.setAttr("%s.yetiVariableF_topHairSwitch" % asset_yeti, 0)
        cmds.select(asset_yeti, r = True)
    else:
        print("Can't find the yeti node")
        return False
    yeti_util.CacheLightScene(only_selection=True, set_groom=True)
    cmds.file(save=True)
    cmds.quit(f=True)




def setStritsCapAndHair():
    """
    pick strits splineC ctrl, and the caps Adjustment ctrl, and run the script.
    :return:
    """
    selection = cmds.ls(sl=True)
    target_goal = selection[0]
    name_space = target_goal.split(target_goal.split(":")[-1])[0]
    target = selection[1]
    if cmds.objExists("SplineC_Loc_Group"):
        cmds.delete("SplineC_Loc_Group")
    cmds.file("P:/930383_KiwiStrit3/Production/Temp/Hat_Placement.ma", i=True,options="v=0;")

    import Maya_Functions.general_util_functions as gen_util
    gen_util.Align(target_goal, "SplineC_Loc_Group")
    gen_util.alignByMatrix("Hat_Loc", [target])

    cmds.delete(["SplineC_Loc_Group", "Hat_Loc"])
    cmds.setAttr("%syetiNode_BodyShape.yetiVariableF_topHairSwitch" % name_space, 0)
    cmds.setAttr("%syetiNode_BodyShape.imageSearchPath" % name_space,
                 "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/Char/Main/Strit/03_Texture/TIF;P:/930383_KiwiStrit3/Production/Assets/3D_Assets/Char/Main/Strit/03_Texture/TIF/LengthTexture/BernieCapA",
                 type="string")


def runStritHairOffThreads():
    from Multiplicity import ThreadPool
    cur_threadpoll = ThreadPool.ThreadPool(max_threads=5)
    thread_list = []
    from Maya_Functions.general_util_functions import runCmdsInMayaPy

    pr = PublishReport.PublishReport()
    pr.getData(scope="Assets")
    pr.getData(scope="E07_SQ020")
    shot_scope = "E07_SQ020_SH070"
    shots_with_strit = pr.getShotsUsingAsset(identity="Strit",scope=shot_scope)
    shots_with_bean = pr.getShotsUsingAsset(identity="BeanieKiwiA", scope=shot_scope)
    shot_list = []
    for s in shots_with_strit:
        if s in shots_with_bean:
            print("Found in %s" % s)
            shot_info = pr.data[s].getInfoDict()
            shot_path = CC.get_shot_light_file(**shot_info)
            if shot_path:
                shot_list.append(shot_path)

    for shot in shot_list:
        # print(shot)
        content = "from KiwiStrit3.project_functions import stritHairOff\nstritHairOff(file_path='{file_path}')".format(file_path=shot)
        # print(content)
        thread_list.append(ThreadPool.Worker(func=runCmdsInMayaPy, content=content))
    cur_threadpoll.startBatch(thread_list, use_amount=5)

if __name__ == '__main__':
    pass
    # shot_list = ["E07_SQ040_SH010","E07_SQ040_SH020","E07_SQ040_SH030","E07_SQ040_SH040","E07_SQ040_SH050","E07_SQ040_SH060","E07_SQ040_SH070","E07_SQ040_SH090","E07_SQ040_SH100","E07_SQ040_SH110","E07_SQ040_SH120","E07_SQ040_SH130","E07_SQ040_SH140","E07_SQ040_SH150","E07_SQ040_SH170","E07_SQ040_SH190","E07_SQ040_SH200","E07_SQ040_SH220","E07_SQ040_SH240","E07_SQ040_SH250","E07_SQ040_SH260"]
    #runStritHairOffThreads()

#2:
#100 + 110 + 130