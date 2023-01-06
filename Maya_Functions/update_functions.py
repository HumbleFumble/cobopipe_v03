import maya.cmds as cmds
import os
import ClearImportedModules as CIM
CIM.dropCachedImports("YetiFunctions")


import datetime
from Maya_Functions.file_util_functions import saveFile
import Maya_Functions.yeti_util_functions as YF
log_file = "C:/Temp/KiwiStrit3/TransferUpdateLog.txt"
from Log.CoboLoggers import getLogger
logger = getLogger()


def ToLogFunction(old_string,new_string):

    now = datetime.datetime.now()
    cur_time = now.strftime("%Y-%m-%d %H:%M:%S")
    # cur_time = "{:.4f}s".format(time.time())
    old_string = "%s\n%s->%s" %(old_string,cur_time,new_string)
    return old_string


def update_ref_and_textures(replace_dict): #changed to list of tuples?
    """
    Made to run through a maya file and check for paths of textures and refs and yeti-paths and replace
    the paths found accordingly with the orig/new string.
    :param orig_string: The string it will try to replace
    :param new_string: The string it with put in place of orig_string
    :return:
    """
    to_log_string = ""
    scene_name = cmds.file(q=True,sn=True)
    to_log_string = ToLogFunction(to_log_string,"OPENING SCENE: %s \n------------------------------------------------\n" % scene_name)

    refs = cmds.file(q=True, r=True)
    for ref_path in refs:
        logger.info(ref_path)
        ref_node = cmds.referenceQuery(ref_path, referenceNode=True)
        if "ApprovalLight" in ref_path:  # Remove the approval light reference
            cmds.file(ref_path, rr=True, f=True)
            continue
        final_ref_string = ref_path
        #Special check for module changes. Unigue to KS2-KS3
        # module_dict = {'/Char/Module/EyesA/02_Ref/EyesA_Model': '/RigModule/Head/EyesA/02_Ref/EyesA_Rig', '/Char/Module/LegsA/02_Ref/LegsA_Model': '/RigModule/Leg/LegsA/02_Ref/LegsA_Rig',
        #                 '/Char/Module/ArmsA/02_Ref/ArmsA_Model': '/RigModule/Arm/ArmsA/02_Ref/ArmsA_Rig',
        #                 '/Char/Module/ArmARight/02_Ref/ArmARight_Model': '/RigModule/Arm/ArmARight/02_Ref/ArmARight_Rig'}
        # for mkey in module_dict.keys():
        #     if mkey in final_ref_string:
        #         final_ref_string = final_ref_string.replace(mkey,module_dict[mkey])
        #Now return to the norm.
        for rkey in replace_dict.keys():
            if rkey in final_ref_string:
                final_ref_string = final_ref_string.replace(rkey,replace_dict[rkey])
            if "{" in final_ref_string:
                final_ref_string = final_ref_string.split("{")[0]
        if os.path.exists(final_ref_string) and not final_ref_string ==ref_path:
            logger.info('Replacing %s with %s' % (ref_path, final_ref_string))
            # to_log_string = ToLogFunction(to_log_string, 'Replacing %s with %s' % (ref_path, final_ref_string))
            cmds.file(final_ref_string, loadReference=ref_node)
        else:
            logger.warning("Can't find new file %s based on %s" % (final_ref_string, ref_path))
            to_log_string = ToLogFunction(to_log_string, "Can't find new file %s based on %s" % (final_ref_string, ref_path))
            # else:
            #     print("Can't replace %s in %s" % (new_string, ref_path))
    file_nodes = cmds.ls(type='file')
    for cur_node in file_nodes:
        tex_path = cmds.getAttr('%s.fileTextureName' % (cur_node))
        final_tex_path = tex_path
        for nkey in replace_dict.keys():
            if nkey in tex_path:
                final_tex_path = final_tex_path.replace(nkey,replace_dict[nkey])
            # else:
            #     print("Can't replace %s with %s in %s" % (nkey,replace_dict[nkey], final_tex_path))
        if os.path.exists(final_tex_path):
            logger.info('Replacing %s with %s' % (tex_path, final_tex_path))
            # to_log_string = ToLogFunction(to_log_string,'Replacing %s with %s' % (tex_path, final_tex_path))
            cmds.setAttr('%s.fileTextureName' % (cur_node), final_tex_path, type='string')
        else:
            to_log_string = ToLogFunction(to_log_string, "Can't find %s -> %s" % (tex_path,final_tex_path))
            logger.info("Can't find %s -> %s" % (tex_path,final_tex_path))


    cur_nodes = YF.GetYetiNodes(from_selection=False, only_visible=False)
    for cur in cur_nodes:
        YF.UpdateYetiNode(cur, replace_dict)
    if not to_log_string[-3] == "-":
        saveFile(log_file, save_info=to_log_string, overwrite=False)


def updateTextureAndRefPathsByTuple(replace_list): #changed to list of tuples?
    """
    Made to run through a maya file and check for paths of textures and refs and yeti-paths and replace
    the paths found accordingly with the orig/new string.
    :param orig_string: The string it will try to replace
    :param new_string: The string it with put in place of orig_string
    :return:
    """
    scene_name = cmds.file(q=True,sn=True)
    refs = cmds.file(q=True, r=True)
    for ref_path in refs:
        ref_node = cmds.referenceQuery(ref_path, referenceNode=True)
        if "ApprovalLight" in ref_path:  # Remove the approval light reference
            cmds.file(ref_path, rr=True, f=True)
            continue
        final_ref_string = ref_path
        debug_crash = 0
        while "//" in final_ref_string and debug_crash<100:
            final_ref_string = final_ref_string.replace("//", "/")
            debug_crash = debug_crash +1
        #Now return to the norm.
        for rkey,rvalue in replace_list:
            if rkey in final_ref_string:
                final_ref_string = final_ref_string.replace(rkey,rvalue)
            if "{" in final_ref_string:
                final_ref_string = final_ref_string.split("{")[0]
        if os.path.exists(final_ref_string) and not final_ref_string == ref_path:
            logger.info('Replacing %s with %s' % (ref_path, final_ref_string))
            # to_log_string = ToLogFunction(to_log_string, 'Replacing %s with %s' % (ref_path, final_ref_string))
            cmds.file(final_ref_string, loadReference=ref_node)
        else:
            logger.warning("Can't find new file %s based on %s" % (final_ref_string, ref_path))
            # to_log_string = ToLogFunction(to_log_string, "Can't find new file %s based on %s" % (final_ref_string, ref_path))
            # else:
            #     print("Can't replace %s in %s" % (new_string, ref_path))
    file_nodes = cmds.ls(type='file')
    for cur_node in file_nodes:
        tex_path = cmds.getAttr('%s.fileTextureName' % (cur_node))
        final_tex_path = tex_path
        debug_crash = 0
        while "//" in final_tex_path and debug_crash<100:
            final_tex_path = final_tex_path.replace("//", "/")
            debug_crash = debug_crash +1
        for nkey,nvalue in replace_list:
            if nkey in tex_path:
                final_tex_path = final_tex_path.replace(nkey,nvalue)
            # else:
            #     print("Can't replace %s with %s in %s" % (nkey,replace_dict[nkey], final_tex_path))
        if os.path.exists(final_tex_path):
            logger.info('Replacing %s with %s' % (tex_path, final_tex_path))
            # to_log_string = ToLogFunction(to_log_string,'Replacing %s with %s' % (tex_path, final_tex_path))
            cmds.setAttr('%s.fileTextureName' % (cur_node), final_tex_path, type='string')
        else:
            # to_log_string = ToLogFunction(to_log_string, "Can't find %s -> %s" % (tex_path,final_tex_path))
            logger.warning("Can't find %s -> %s" % (tex_path,final_tex_path))


    cur_nodes = YF.GetYetiNodes(from_selection=False, only_visible=False)
    for cur in cur_nodes:
        YF.UpdateYetiNode(cur, replace_list)