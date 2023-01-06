import maya.cmds as cmds

def unlock(node):
    if not cmds.listRelatives(node, children=True) == None:
        for child in cmds.listRelatives(node, children=True):
            unlock(child)
            # cmds.lockNode(child, lock = False)
    cmds.lockNode(node, lock=False)
    print('Unlocked: ' + node)


def getAttributes(node):
    attributes = []
    data = cmds.listAttr(node, userDefined=True)
    if data != None:
        for attribute in data:
            attributes.append(attribute)
    return attributes

def getAttributeValues(source, attribute, keys=['all']):
    values = {}

    if 'niceName' in keys or 'all' in keys:
        niceName = cmds.attributeName(source + '.' + attribute, nice=True)
        values.update({'niceName':niceName})

    if 'longName' in keys or 'all' in keys:
        longName = cmds.attributeName(source + '.' + attribute, long=True)
        values.update({'longName':longName})

    if 'value' in keys or 'all' in keys:
        value = cmds.getAttr(source + '.' + attribute)
        values.update({'value':value})

    if 'keyable' in keys or 'all' in keys:
        keyable = cmds.getAttr(source + '.' + attribute, keyable=True)
        values.update({'keyable':keyable})

    if 'lock' in keys or 'all' in keys:
        lock = cmds.getAttr(source + '.' + attribute, lock=True)
        values.update({'lock':lock})

    if 'type' in keys or 'all' in keys:
        type = cmds.getAttr(source + '.' + attribute, type=True)
        values.update({'type':type})

    if 'size' in keys or 'all' in keys:
        size = cmds.getAttr(source + '.' + attribute, size=True)
        values.update({'size':size})

    if 'time' in keys or 'all' in keys:
        time = cmds.getAttr(source + '.' + attribute, time=True)
        values.update({'time':time})

    if 'silent' in keys or 'all' in keys:
        silent = cmds.getAttr(source + '.' + attribute, silent=True)
        values.update({'silent':silent})

    if 'settable' in keys or 'all' in keys:
        settable = cmds.getAttr(source + '.' + attribute, settable=True)
        values.update({'settable':settable})

    if 'expandEnvironmentVariables' in keys or 'all' in keys:
        expandEnvironmentVariables = cmds.getAttr(source + '.' + attribute, expandEnvironmentVariables=True)
        values.update({'expandEnvironmentVariables':expandEnvironmentVariables})

    if 'asString' in keys or 'all' in keys:
        asString = cmds.getAttr(source + '.' + attribute, asString=True)
        values.update({'asString':asString})

    if 'channelBox' in keys or 'all' in keys:
        channelBox = cmds.getAttr(source + '.' + attribute, channelBox=True)
        values.update({'channelBox':channelBox})

    if 'caching' in keys or 'all' in keys:
        caching = cmds.getAttr(source + '.' + attribute, caching=True)
        values.update({'caching':caching})

    if 'multiIndices' in keys or 'all' in keys:
        multiIndices = cmds.getAttr(source + '.' + attribute, multiIndices=True)
        values.update({'multiIndices':multiIndices})

    if 'hidden' in keys or 'all' in keys:
        hidden = cmds.attributeQuery(attribute, node=source, hidden=True)
        values.update({'hidden': hidden})

    if 'defaultValue' in keys or 'all' in keys:
        defaultValue = cmds.attributeQuery(attribute, node=source, listDefault=True)
        if isinstance(defaultValue, list):
            defaultValue = defaultValue[0]
        values.update({'defaultValue': defaultValue})

    if 'enumName' in keys or 'all' in keys:
        enumName = cmds.attributeQuery(attribute, node=source, listEnum=True)
        if isinstance(enumName, list):
            enumName = enumName[0]
        values.update({'enumName': enumName})

    if 'hasMaxValue' in keys or 'all' in keys:
        hasMaxValue = cmds.attributeQuery(attribute, node=source, maxExists=True)
        if isinstance(hasMaxValue, list):
            hasMaxValue = hasMaxValue[0]
        values.update({'hasMaxValue': hasMaxValue})

    if 'hasMinValue' in keys or 'all' in keys:
        hasMinValue = cmds.attributeQuery(attribute, node=source, minExists=True)
        if isinstance(hasMinValue, list):
            hasMinValue = hasMinValue[0]
        values.update({'hasMinValue': hasMinValue})

    if 'hasSoftMaxValue' in keys or 'all' in keys:
        hasSoftMaxValue = cmds.attributeQuery(attribute, node=source, softMaxExists=True)
        if isinstance(hasSoftMaxValue, list):
            hasSoftMaxValue = hasSoftMaxValue[0]
        values.update({'hasSoftMaxValue': hasSoftMaxValue})

    if 'hasSoftMinValue' in keys or 'all' in keys:
        hasSoftMinValue = cmds.attributeQuery(attribute, node=source, softMinExists=True)
        if isinstance(hasSoftMinValue, list):
            hasMaxValue = hasSoftMinValue[0]
        values.update({'hasSoftMinValue': hasSoftMinValue})

    if 'maxValue' in keys or 'all' in keys:
        maxValue = cmds.attributeQuery(attribute, node=source, maximum=True)
        if isinstance(maxValue, list):
            maxValue = maxValue[0]
        values.update({'maxValue': maxValue})

    if 'minValue' in keys or 'all' in keys:
        minValue = cmds.attributeQuery(attribute, node=source, minimum=True)
        if isinstance(minValue, list):
            minValue = minValue[0]
        values.update({'minValue': minValue})

    if 'softMaxValue' in keys or 'all' in keys:
        softMaxValue = cmds.attributeQuery(attribute, node=source, minimum=True)
        if isinstance(softMaxValue, list):
            softMaxValue = softMaxValue[0]
        values.update({'softMaxValue': softMaxValue})

    if 'softMinValue' in keys or 'all' in keys:
        softMinValue = cmds.attributeQuery(attribute, node=source, minimum=True)
        if isinstance(softMinValue, list):
            softMinValue = softMinValue[0]
        values.update({'softMinValue': softMinValue})

    return values


def transferAttributes(source, target, attributes):
    for attribute in attributes:
        if not cmds.attributeQuery(attribute, node=target, exists=True):
            values = getAttributeValues(source, attribute)

            # for key in values:
            #     print(key + ': ' + str(values[key]))

            if values['type'] == 'enum':
                cmds.addAttr(target,
                             longName=values['longName'],
                             attributeType=values['type'],
                             hidden=values['hidden'],
                             keyable=True,
                             enumName=values['enumName'])

            else:
                cmds.addAttr(target,
                             longName=values['longName'],
                             attributeType=values['type'],
                             hidden=values['hidden'],
                             keyable=True)

            if values['enumName'] != None:
                    cmds.addAttr(target + '.' + attribute, edit=True, attributeType='enum', enumName=values['enumName'])

            if values['hasMaxValue'] == True:
                cmds.addAttr(target + '.' + attribute, edit=True, maxValue=values['maxValue'])

            if values['hasMinValue'] == True:
                cmds.addAttr(target + '.' + attribute, edit=True, minValue=values['minValue'])

            if values['hasSoftMaxValue'] == True:
                cmds.addAttr(target + '.' + attribute, edit=True, softMaxValue=values['softMaxValue'])

            if values['hasSoftMinValue'] == True:
                cmds.addAttr(target + '.' + attribute, edit=True, softMinValue=values['softMinValue'])


            cmds.setAttr(target + '.' + attribute, lock=values['lock'], keyable=values['keyable'])

            cmds.copyAttr(source, target,
                          values = True,
                          inConnections = True,
                          outConnections = True,
                          keepSourceConnections = False,
                          attribute=[attribute])

def propAssetTransfer(ref_render):
    import maya.cmds as cmds
    cmds.file(ref_render, i=True)
    for topChild in cmds.listRelatives('Top_Group', children=True, fullPath=True):
        rootChild = topChild.replace('Top_Group', 'Root_Group')
        if cmds.objExists(rootChild):
            cmds.delete(rootChild)
            cmds.parent(topChild, 'Root_Group')
        else:
            cmds.parent(topChild, 'Root_Group')
    groupOrder = ['|Root_Group|Ctrl_Group', '|Root_Group|Rig_Group', '|Root_Group|Geo_Group',
                  '|Root_Group|Texture_Group', '|Root_Group|Light_Group']
    for group in groupOrder:
        cmds.reorder(group, back=True)
    cmds.delete('Top_Group')

# def setdressAssetTransfer(asset_info, new_asset_info):
#     import maya.cmds as cmds
#
#     new_asset_info["asset_step"] = "Base"
#     base_file = CC.get_asset_work_file(**new_asset_info)
#     render_ref = CC.old.get_Render(**asset_info)
#
#     cmds.file(base_file, open=True, f=True)
#     cmds.file(type='mayaAscii')
#
#     cmds.file(ref_render, i=True)
#     cmds.select('Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl')
#     attributes = getAttributes('Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl')
#     transferAttributes('Top_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl', 'Root_Group', attributes)
#     geoChildren = cmds.listRelatives('Geo_Group', children=True, fullPath=True)
#     if geoChildren:
#         for geoChild in geoChildren:
#             if not cmds.nodeType(geoChild)[-10:] == 'Constraint':
#                 cmds.parent(geoChild, 'Full')
#     cmds.lockNode('Proxy', lock=False)
#     cmds.delete('Proxy')
#     cmds.duplicate('Full', name='Proxy')
#     cmds.sets('Proxy', remove='Smooth_Set')
#     cmds.lockNode('Proxy', lock=True)
#     nodes = cmds.ls(dagObjects=True, sets=True)
#     topLevelNodes = []
#     if nodes:
#         for node in nodes:
#             if cmds.listRelatives(node, parent=True) == None:
#                 topLevelNodes.append(node)
#
#     # Looping through all nodes in the scene without parents
#     # and if they don't fit on the pre-approved list, delete the node
#     for node in topLevelNodes:
#         if node not in ['persp', 'top', 'front', 'side', 'Root_Group', 'Full', 'Proxy', 'Smooth_Set', 'defaultLightSet', 'defaultObjectSet', 'initialParticleSE', 'initialShadingGroup']:
#             cmds.lockNode(node, lock=False)
#             cmds.delete(node)
#
#     # Check if asset_type attribute exists, then check if it's SetDress and change it to Setdress
#     if cmds.attributeQuery('asset_type', node='Root_Group', exists=True):
#         if cmds.getAttr("Root_Group.asset_type" ) == "SetDress":
#             cmds.setAttr("Root_Group.asset_type", "Setdress", type="string")
#
#     # Check if asset_category attribute exists,
#     # then check if it is either Ground, Bush or Tree and if so replace with Forest
#     if cmds.attributeQuery('assetCategory', node='Root_Group', exists=True):
#         if cmds.getAttr("Root_Group.asset_category") in ['Ground', 'Bush', 'Tree']:
#             cmds.setAttr("Root_Group.asset_category", "Forest", type="string")
#
#     cmds.file(save=True)
#     cmds.quit(f=True)



    # for topChild in cmds.listRelatives('Top_Group', children=True, fullPath=True):
    #     rootChild = topChild.replace('Top_Group', 'Root_Group')
    #     if cmds.objExists(rootChild):
    #         cmds.delete(rootChild)
    #         cmds.parent(topChild, 'Root_Group')
    #     else:
    #         cmds.parent(topChild, 'Root_Group')
    # groupOrder = ['|Root_Group|Ctrl_Group', '|Root_Group|Rig_Group', '|Root_Group|Geo_Group',
    #               '|Root_Group|Texture_Group', '|Root_Group|Light_Group']
    # for group in groupOrder:
    #     cmds.reorder(group, back=True)
    # cmds.delete('Top_Group')

if __name__ == '__main__':
    pass
    #import maya.standalone

    #maya.standalone.initialize('python')
    # import maya.cmds as cmds
    #
    # cmds.file('P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Assets/3D_Assets/Setdress/Grounds/HillB/01_Work/Maya/HillB_Base.ma', open=True, f=True)
    # cmds.file(type='mayaAscii')
    # setdressAssetTransfer('P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/Setdress/Grounds/HillB/02_Ref/HillB_Render.mb')
    # from assetTransfer import assetTransfer
    # # assetTransfer('%s')
    # from UpdateTextures import update_textures

    # # update_textures('%s', '%s')
    # cmds.file(save=True)
    # cmds.quit(f=True)