import maya.cmds as cmds


def InstanceRef(cur_obj_list=None):
    return_list = []
    if not cur_obj_list:
        cur_obj_list = cmds.ls(sl=True)
    for obj in cur_obj_list:
        cur_namespace = ":".join(obj.split(":")[:-1])
        cmds.namespace(set=cur_namespace)
        return_list.append(cmds.instance(obj))
        cmds.namespace(set=":")
    return return_list