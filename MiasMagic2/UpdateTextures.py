import os

def update_textures(splitter, path_replace):
    import maya.cmds as cmds
    """# update texture paths
    splitter = the string to split by. Takes the last index after the split
    path_replace = the string to put infront after the split.
    """

    file_nodes = cmds.ls(type='file')
    # print('Files :', file_nodes)
    print('\n\nTextureUpdate: ' + str(file_nodes) + '\n\n')

    if file_nodes !=None:
        for node in file_nodes:
            if node != None:
                # print('NODE : ', node)
                tex_path = cmds.getAttr('%s.fileTextureName' % (node))
                tex_path = tex_path.replace(os.sep, '/')
                while '//' in tex_path:
                    tex_path = tex_path.replace('//', '/')
                tex_path = tex_path.replace('Error_', '')
                tex_path = tex_path.replace('SetDress', 'Setdress')
                tex_path = tex_path.replace('/Trees/', '/Forest/')
                tex_path = tex_path.replace('/Bushes/', '/Forest/')
                tex_path = tex_path.replace('/Grounds/', '/Forest/')

                print('tex_path: ' + tex_path)

                splitter = splitter.replace(os.sep, '/')
                while '//' in splitter:
                    splitter = splitter.replace('//', '/')
                splitter = splitter.replace('Error_', '')
                splitter = splitter.replace('SetDress', 'Setdress')
                splitter = splitter.replace('/Trees/', '/Forest/')
                splitter = splitter.replace('/Bushes/', '/Forest/')
                splitter = splitter.replace('/Grounds/', '/Forest/')

                print('splitter: ' + splitter)

                """Here change to split by old-base path and replace with new-base path"""
                if splitter in tex_path:
                    end_path = tex_path.split(splitter)[-1]
                    new_path = '%s/%s' % (path_replace, end_path)
                    new_path = new_path.replace(os.sep, '/')
                    while '//' in new_path:
                        new_path = new_path.replace('//', '/')
                    new_path = new_path.replace('Error_', '')
                    new_path = new_path.replace('SetDress', 'Setdress')
                    new_path = new_path.replace('/Trees/', '/Forest/')
                    new_path = new_path.replace('/Bushes/', '/Forest/')
                    new_path = new_path.replace('/Grounds/', '/Forest/')

                    print('new_path: ' + new_path)

                    if os.path.exists(new_path):
                        print(new_path)
                        cmds.setAttr('%s.fileTextureName' % (node), new_path, type='string')
                    else:
                        print('Could not find the new texture path : ', new_path)
                        error_path = 'Error_' + tex_path
                        cmds.setAttr('%s.fileTextureName' % (node), error_path, type='string')
                else:
                    print('Could not find texture path : ' + splitter + ' in ' + tex_path)
                    error_path = 'Error_' + tex_path
                    cmds.setAttr('%s.fileTextureName' % (node), error_path, type='string')


def updateRef(split_path, new_path):
    import maya.cmds as cmds
    refs = cmds.file(q=True, r=True)
    ref_nodes = []
    for ref in refs:
        ref_node = cmds.referenceQuery(ref, referenceNode=True)
        if split_path in ref:
            new_ref_path = new_path + ref.split(split_path)[-1]
            if 'Char/Module' in new_ref_path:
                new_ref_path = new_ref_path.replace('Char/Module', 'RigModule')
            print(new_ref_path)
            if os.path.exists(new_ref_path):
                print(new_ref_path)
                try:
                    cmds.file(new_ref_path, loadReference=ref_node)
                except:
                    pass
            else:
                if new_path not in ref:
                    print('Error: Could not find ' + new_ref_path)
                    while 'Error_' in ref:
                        ref = ref.replace('Error_', '')
                    error_ref = 'Error_' + ref
                    try:
                        cmds.file(error_ref, loadReference=ref_node)
                    except:
                        pass
                else:
                    while 'Error_' in ref:
                        ref = ref.replace('Error_', '')
                    try:
                        cmds.file(ref, loadReference=ref_node)
                    except:
                        pass
        else:
            print('Error: ' + split_path + ' not in ' + ref)


def addPublishSet():
    import maya.cmds as cmds
    if cmds.objExists('RemoveInPublish'):
        cmds.delete('RemoveInPublish')
    if not cmds.objExists('PublishSet'):
        cmds.sets(name='PublishSet')
    nodes = cmds.ls(assemblies=True, long=True)
    for node in nodes:
        if cmds.objExists('RemoveInPublish'):
            if not node in cmds.sets(node, isMember='RemoveInPublish'):
                cmds.sets(node, add='PublishSet')
        else:
            cmds.sets(node, add='PublishSet')
    if cmds.objExists('|Top_Group'):
        cmds.rename('|Top_Group', 'Root_Group')
    cmds.lockNode('PublishSet', lock=True)
    groupOrder = ['|Root_Group|Ctrl_Group', '|Root_Group|Rig_Group', '|Root_Group|Geo_Group',
                  '|Root_Group|Texture_Group', '|Root_Group|Light_Group', '|Root_Group|Groom_Group']
    for group in groupOrder:
        try:
            cmds.reorder(group, back=True)
        except:
            pass