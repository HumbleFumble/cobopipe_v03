import maya.cmds as cmds


def InstanceRef(cur_obj_list=None,sl=True):
    return_list = []
    if not cur_obj_list:
        cur_obj_list = cmds.ls(sl=True,long=True)
    for obj in cur_obj_list:
        obj_name = obj
        if "|" in obj_name:
            obj_name = obj.split("|")[-1]
        cur_namespace = ":".join(obj_name.split(":")[:-1])
        cmds.namespace(set=cur_namespace)
        return_list.append(cmds.instance(obj)[0])
        cmds.namespace(set=":")
    if sl:
        cmds.select(return_list, r=True)
        print(return_list)
    return return_list