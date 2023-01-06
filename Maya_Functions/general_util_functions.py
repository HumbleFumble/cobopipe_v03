import maya.cmds as cmds
from getConfig import getConfigClass
CC = getConfigClass()
from Log.CoboLoggers import getLogger

logger = getLogger()

def virusCheck():
    found = False
    if checkForUserSetupAndVirus():
        found = True
    if removeVirusScriptNodes():
        found = True
    if found:
        cmds.warning("FOUND THE VIRUS IN ON YOUR MACHINE/FILE. PLEASE RUN CLEAN UPS!")
        saveVirusLog(cmds.file(q=True, sn=True))
    else:
        cmds.warning("No Virus found :) ! ")

def openAndCleanFile(cur_file):
    logger.info("Looking for Virus in: %s" % cur_file)
    cmds.file(cur_file, open=True, esn=False, f=True)
    checkForUserSetupAndVirus()
    extra_clean_list = removeVirusScriptNodes()
    if extra_clean_list:
        if extra_clean_list == True:
            cmds.file(save=True)
            logger.info("Virus have been cleaned from %s" % cur_file)
            saveVirusLog(cur_file)
            return True
        else:
            findAndCleanFiles(extra_clean_list)
            if openAndCleanFile(cur_file):
                return True
    #logger.info("Found no Virus in: %s" % cur_file)
    return False

def saveVirusLog(file_name):
    import Maya_Functions.file_util_functions as file_util
    import os
    folder,file_only = os.path.split(file_name)
    if "." in file_only:
        file_only = file_only.split(".")[0]
    save_path = "%s/VirusLogs/%s.txt" % (CC.get_publish_report_folder(),file_only)
    file_util.saveFile(save_path,"Virus found!")

def removeVirusScriptNodes():
    find_scripts = cmds.ls(type="script")
    to_delete = []
    for cur_script in find_scripts:
        if "vaccine_gene" in cur_script:
            to_delete.append(cur_script)
        if "breed_gene" in cur_script:
            to_delete.append(cur_script)
    if to_delete:
        logger.warning("FOUND %s in %s" %(to_delete, cmds.file(q=True,sn=True)))
        check_list = []
        for d in to_delete:
            if ":" in d:
                name = ":".join(d.split(":")[:-1])
                if not name in check_list:
                    check_list.append(name)
                    logger.critical("VIRUS IN REF: %s" % name)
        if check_list:
            return check_list
        cmds.delete(to_delete)
        return True
    else:
        logger.info("Found No Virus in %s" % cmds.file(q=True,sn=True))
    return False

def RemoveAssets(assets_to_keep):
    refs = cmds.file(q=True, reference=True)
    # logger.info("Keeping refs: %s" % assets_to_keep)
    for ref in refs:
        # node = cmds.referenceQuery(ref, rfn=True, topReference=True)
        if not cmds.referenceQuery(ref, isLoaded=True):
            cmds.file(ref, loadReference=True)
        cur = cmds.referenceQuery(ref, namespace=True, topReference=True, shortName=True)
        if not cur in assets_to_keep:
            logger.debug("REMOVING: %s" % ref)
            cmds.file(ref, rr=True)

def GetAssetsinShot(shot_node_name):
    assets = cmds.getAttr("%s.assetlinks" % shot_node_name)
    if assets != None and assets != "":
        if "," in assets:
            assets = assets.split(',')  # convert to list so we can append
            assets = sorted(assets)
            return assets
        else:
            return [assets]
    else:
        return False

def findAssetByName(name):
    import os
    top_path = CC.get_asset_top_path()
    # all_node_list = {}
    for fol_type in os.listdir(top_path):
        if "." in fol_type:
            continue
        for fol_category in os.listdir("%s/%s" % (top_path, fol_type)):
            if "." in fol_category:
                continue
            for fol_asset in os.listdir("%s/%s/%s" % (top_path, fol_type,fol_category)):
                if "." in fol_asset:
                    continue
                temp_asset_dict = {"asset_name":fol_asset,"asset_type":fol_type,"asset_category":fol_category}
                if fol_asset == name:
                    return temp_asset_dict
    return False


def getAllWorkFiles(asset_dict):
    work_types = CC.ref_order[asset_dict["asset_type"]]
    to_return = []
    for cur_step in work_types:
        asset_dict["asset_step"] = cur_step
        work_file = CC.get_asset_work_file(**asset_dict)
        to_return.append(work_file)
    return to_return

def findAndCleanFiles(asset_list):
    import PublishAssets.PublishMaster as PM
    for a in asset_list:
        if "Anim:" in a:
            a = a.split("Anim:")[-1]
        logger.info("Looking for %s Asset" % a)
        a_dict = findAssetByName(a)
        if a_dict:
            work_files = getAllWorkFiles(a_dict)
            for cur_step in work_files:
                if openAndCleanFile(cur_step):
                    work_step = cur_step.split("_")[-1].split(".ma")[0]
                    a_dict["asset_step"] = work_step
                    a_publish = PM.ReadyPublish(asset_info=a_dict)
                    a_publish.StartPublish()

def checkForUserSetupAndVirus():
    import os
    check_scripts = cmds.internalVar(userAppDir=True) + '/scripts/'
    content = os.listdir(check_scripts)
    name_list = ["vaccine.py","vaccine.pyc","userSetup.py"]
    to_delete = []
    for c in content:
        if c in name_list:
            to_delete.append(c)
    if to_delete:
        logger.warning("Virus Found/Deleting: %s" % to_delete)
        for d in to_delete:
            os.remove(check_scripts + d)
        return True
    else:
        logger.info("Found No Virus scripts in scripts-folder")
        return False


    #check_path_vaccine = cmds.internalVar(userAppDir=True) + '/scripts/vaccine.py'
    #check_path_vaccine_pyc = cmds.internalVar(userAppDir=True) + '/scripts/vaccine.pyc'
    #check_path_user_setup = cmds.internalVar(userAppDir=True) + '/scripts/userSetup.py'


def setupModuleEyes():
    delete_list = ["L_Eye_Module","R_Eye_Module"]
    transfer_connections_list = [("EyesA:L_Eye_Ctrl_Group", "L_Eye_Ctrl_Group"),
                                 ("EyesA:R_Eye_Ctrl_Group", "R_Eye_Ctrl_Group")]
    align_list = [("EyesA:L_Eye_Ctrl_Group", "L_Eye_Module"),
                  ("EyesA:R_Eye_Ctrl_Group", "R_Eye_Module"),
                  ("EyesA:L_EyeMain_Ctrl_Group", "L_EyeMain_Ctrl_Group"),
                  ("EyesA:R_EyeMain_Ctrl_Group", "R_EyeMain_Ctrl_Group")]
    eye_aim_list = [("EyesA:L_EyeAim_Ctrl_Group", "L_EyeAim_Ctrl_Group"),
                    ("EyesA:R_EyeAim_Ctrl_Group", "R_EyeAim_Ctrl_Group")]
    parenting_list = [("Root_Ctrl", "EyesA:L_Eye_Ctrl_Group"),
                      ("Root_Ctrl", "EyesA:R_Eye_Ctrl_Group"),
                      ("Rig_Group", "EyesA:L_Eye_Rig_Group"),
                      ("Rig_Group", "EyesA:R_Eye_Rig_Group"),
                      ("Geo_Group", "EyesA:L_Eye_Geo_Group"),
                      ("Geo_Group", "EyesA:R_Eye_Geo_Group")]
    hiding_list = ["R_Eye_Geo_Group",
                   "L_Eye_Geo_Group",
                   "R_Eye_Ctrl_Group",
                   "L_Eye_Ctrl_Group",
                   "R_EyeAim_Ctrl_Group",
                   "L_EyeAim_Ctrl_Group",
                   "R_Eye_Geo_Group",
                   "L_Eye_Geo_Group",
                   "EyesA:L_Eye_Rig_Group",
                   "EyesA:R_Eye_Rig_Group"]

    # for target in delete_list:
    #     if cmds.objExists(target):
    #         cmds.delete(target)

    for target, source in transfer_connections_list:
        if not cmds.objExists(target) or not cmds.objExists(source):
            continue
        print("\nSetting up: " + source + " & " + target)

        # transfer outputs
        transferOutputConnections(target, source)

        # transfer inputs
        input_c_list = cmds.listConnections(source, p=True, d=True, c=True)
        if input_c_list:
            for x in range(0, len(input_c_list), 2):
                dest = input_c_list[x]
                plug_source = input_c_list[x + 1]
                dest = "%s.%s" % (target, dest.split(".")[-1])
                print("- " * 4 + "Connecting: " + plug_source + " & " + dest)
                if "constraintParentInverseMatrix" in plug_source:
                    cmds.connectAttr(dest, plug_source, f=True)
                    print("- " * 8 + "Connected (inverse matrix found)")
                else:
                    if cmds.attributeQuery(dest.split(".")[-1], node=dest.split(".")[0], exists=True):
                        cmds.connectAttr(plug_source, dest, f=True)
                        print("- " * 8 + "Connected (regular flow)")

    for target, source in align_list:
        # aligning
        if not cmds.objExists(target) or not cmds.objExists(source):
            continue
        alignByMatrix(source, [target])

    for target, source in eye_aim_list:
        # positioning
        if not cmds.objExists(target) or not cmds.objExists(source):
            continue
        moveToWSPosition(source=source, target=target)
        if cmds.objExists("Look_Ctrl"):
            cmds.parentConstraint("Look_Ctrl", target, maintainOffset=True)

    for parent, child in parenting_list:
        # parenting
        if not cmds.objExists(parent) or not cmds.objExists(child):
            continue
        cmds.parent(child, parent)

    for item in hiding_list:
        if not cmds.objExists(item):
            continue
        try:
            cmds.setAttr(item+".visibility", lock=False)
        except:
            print("Can't unlock from ref")
        cmds.select(d=True)
        cmds.hide(item)
        try:
            cmds.disconnectAttr("Root_Ctrl.hideEyes", item + ".visibility")
        except:
            pass
        print("Hidden: " + item)


#mayapy.exe -c "import maya.standalone;	maya.standalone.initialize('python');	import maya.cmds as cmds;	import subprocess;	from RenderSubmit import RenderSubmitFunctions;	RSF = RenderSubmitFunctions();	cmds.file('P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E05/E05_SQ020/E05_SQ020_SH010/02_Light/E05_SQ020_SH010_Light.ma', open=True, f=True);	RSF.SaveRenderFileFunc(render_file='P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/E05/E05_SQ020/E05_SQ020_SH010/04_Publish/E05_SQ020_SH010_ColorB_Render.ma',render_layer=False,only_bg=False,bubbles=False);	cmds.file(save=True);    cmds.quit(f=True);	"
#21:18:02,059 - 21:17:03,592
def reissue_uuids(request=None):
    import maya.cmds as cmds
    import maya.api.OpenMaya as api2
    from functools import partial
    """
    Found and stole it here: http://www.csa3d.com/code/universally-unique-identifiers-are-not-necessarily-unique.html
    Generates new UUIDs for the requested dependency nodes, including 'read-only' nodes.

    Request resolution order
        1. requested node or list of nodes
        2. selected nodes
        3. all dependency nodes loaded in scene

    :param request: Nodes to issue new UUIDs
    :type request: list|str|unicode

    :returns: Nothing
    :rtype: None
    """
    logger.info("ReIssue UUIDs")
    get_depends = partial(cmds.ls, dep=True)
    depend_nodes = get_depends(request) or get_depends(selection=True) or get_depends()

    selection_list = api2.MSelectionList()
    [selection_list.add(node) for node in depend_nodes]

    iter_selection = api2.MItSelectionList(selection_list)  # MItDag unavailable until Maya 2016 SP6 ext 2
    i = 0
    while not iter_selection.isDone():
        i += 1
        if i % 100 == 0:
            print(i)
        node = api2.MFnDependencyNode(iter_selection.getDependNode())
        uuid = api2.MUuid().generate()
        node.setUuid(uuid)
        iter_selection.next()

def moveToWSPosition(source, target):
    """
    Moves a target object to source objects world space position
    :param source: str, defines source object
    :param target: str, defines target object
    :return: tuple, transformation difference between source and target objects
    """

    # GET WS (WORLD SPACE) POSITIONS
    sWS = cmds.xform(source, q=1, ws=1, rp=1)
    tWS = cmds.xform(target, q=1, ws=1, rp=1)

    # COMPARE WS FOR DIFFERENCE
    for sX, sY, sZ in [sWS]:
        for tX, tY, tZ in [tWS]:
            dX = sX - tX
            dY = sY - tY
            dZ = sZ - tZ

    # MOVE TARGET RELATIVELY TO SOURCE POSITION
    # print("Difference: " + str(dX) + " " + str(dY) + " " + str(dZ))
    cmds.move(dX, dY, dZ, target, relative=True)

    return dX, dY, dZ


def SetStringAttribute(on_obj="", attr_name="", attr_value="", create=True):
    if not cmds.attributeQuery(attr_name, n=on_obj, ex=True) and create:
        cmds.addAttr(on_obj, longName=attr_name, dt="string")
    cmds.setAttr("%s.%s" % (on_obj, attr_name), attr_value, type="string")


def CheckAttribute(c_obj, c_attr):
    if cmds.attributeQuery(c_attr, node=c_obj, ex=True):
        return_value = cmds.getAttr("%s.%s" % (c_obj, c_attr))
        # if return_value == "":
        # 	return False
        # else:
        return return_value
    else:
        return False


def isShape(fullPath):
    if not cmds.objExists(fullPath):
        return None
    else:
        if 'shape' in cmds.nodeType(fullPath, inherited=True):
            return True
        else:
            return False


def Align(target=None, moving=None):
    if not target and not moving:
        sel = cmds.ls(sl=True)
        target = sel[0]
        moving = sel[1]
    p_delete = cmds.parentConstraint(target, moving, mo=False, n="PO_ToDelete")
    s_delete = cmds.scaleConstraint(target, moving, mo=False, n="SC_ToDelete")
    cmds.delete(p_delete)
    cmds.delete(s_delete)


def alignByMatrix(target_goal=None, moving=None):
    if not target_goal and not moving:
        sel = cmds.ls(sl=True)
        moving = sel[0:-1]
        target_goal = sel[-1]
    m_goal = cmds.xform(target_goal, q=True, matrix=True, ws=True)
    if not isinstance(moving, list):
        moving = list(moving)
    for t in moving:
        cmds.xform(t, matrix=m_goal, ws=True)


def transferOutputConnections(source=None, target=None):
    if not source or not target:
        selection = cmds.ls(sl=True)
        source_list = selection[0:-1]
        target = selection[-1]
        for source in source_list:
            transferOutputConnections(source, target)
    else:
        my_cons = cmds.listConnections(target, p=True)
        if my_cons:
            for cur_con in my_cons:
                if cmds.connectionInfo(cur_con, isDestination=True):
                    # print(cmds.connectionInfo(cur_con,isDestination=True))
                    target_from_con = cmds.connectionInfo(cur_con, sfd=True)
                    source_from_con = "%s.%s" % (source, target_from_con.split(".")[-1])
                    if cmds.attributeQuery(target_from_con.split(".")[-1], node=source, exists=True):
                        locked = cmds.getAttr(cur_con, lock=True)
                        print("%s - locked = %s" % (cur_con, locked))
                        cmds.setAttr(cur_con, lock=0)
                        cmds.connectAttr(source_from_con, cur_con, f=True)
                        cmds.setAttr(cur_con, lock=locked)
                    # cmds.connectAttr(target,f=True)


def transferInputConnections(source=None, target=None):
    if not source or not target:
        selection = cmds.ls(sl=True)
        source_list = selection[0:-1]
        target = selection[-1]
        for source in source_list:
            transferInputConnections(source, target)
    else:
        my_cons = cmds.listConnections(target, p=True)
        for cur_con in my_cons:
            if cmds.connectionInfo(cur_con, isDestination=True):
                # print(cmds.connectionInfo(cur_con,isDestination=True))
                target_from_con = cmds.connectionInfo(cur_con, sfd=True)
                source_from_con = "%s.%s" % (source, target_from_con.split(".")[-1])
                if cmds.attributeQuery(target_from_con.split(".")[-1], node=source, exists=True):
                    locked = cmds.getAttr(cur_con, lock=True)
                    print("%s - locked = %s" % (cur_con, locked))
                    cmds.setAttr(cur_con, lock=0)
                    cmds.connectAttr(source_from_con, cur_con, f=True)
                    cmds.setAttr(cur_con, lock=locked)

def loadGridOfRefs():
    for z in range(1, 10):
        for x in range(1, 10):
            my_ref = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/Setdress/Tree/SnowyTreeA/02_Ref/SnowyTreeA_Render.mb"
            ref_file = cmds.file(my_ref, r=True, namespace="SnowyTreeA_Ref_%s_%s" % (x, z))
            cmds.move(x * 35, 0, z * 35, "SnowyTreeA_Ref_%s_%s:Proxy" % (x, z))
    my_ref = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/Setdress/Tree/SnowyTreeA/02_Ref/SnowyTreeA_Render.mb"
    ref_file = cmds.file(my_ref, r=True, namespace="SnowyTreeA_Ref_Instance")
    for z in range(1, 10):
        for x in range(1, 10):
            instance_obj = cmds.instance("SnowyTreeA_Ref_Instance:Proxy")
            cmds.move(x * 35, 0, z * 35, instance_obj)


def unlockOutputConnections(source=None, lock=False):
    return_list = []
    if not source:
        selection = cmds.ls(sl=True)
        source = selection[0]
    else:
        my_cons = cmds.listConnections(source, p=True)
        if my_cons:
            for cur_con in my_cons:
                if cmds.connectionInfo(cur_con, isDestination=True):
                    locked = cmds.getAttr(cur_con, lock=True)
                    try:
                        logger.info("Unlocking: %s" % cur_con)
                        cmds.setAttr(cur_con, lock=lock)
                    except Exception as e:
                        print(e)
                    if locked:
                        return_list.append(cur_con)
    return return_list

def fix_ui_offscreen():
    import maya.mel as mel
    mel.eval('for ($window in `lsUI -windows`) { window -e -tlc 0 0 $window ; }')


def replaceAddDoubleLinear(source):
    target = cmds.createNode('plusMinusAverage', name=source.replace('ADL', 'PMA'))
    input = cmds.listConnections(source, destination=False, plugs=True)
    if input:
        input = input[0]
        cmds.connectAttr(input, target + '.input1D[0]')
        cmds.setAttr(target + '.input1D[1]', 1)

        for attribute in cmds.listConnections(source, source=False, destination=True, plugs=True):
            cmds.setAttr(attribute, lock=False)
            cmds.connectAttr(target + '.output1D', attribute, force=True)

        cmds.delete(source)