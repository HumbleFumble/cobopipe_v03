import maya.cmds as cmds


# def unlock(node):
#     if not cmds.listRelatives(node, children=True) == None:
#         for child in cmds.listRelatives(node, children=True):
#             unlock(child)
#             # cmds.lockNode(child, lock = False)
#     cmds.lockNode(node, lock=False)
#     print('Unlocked: ' + node)


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
        if 'maxValue' in keys or 'all' in keys and hasMaxValue:
            maxValue = cmds.attributeQuery(attribute, node=source, maximum=True)
            if isinstance(maxValue, list):
                maxValue = maxValue[0]
            values.update({'maxValue': maxValue})


    if 'hasMinValue' in keys or 'all' in keys:
        hasMinValue = cmds.attributeQuery(attribute, node=source, minExists=True)
        if isinstance(hasMinValue, list):
            hasMinValue = hasMinValue[0]
        values.update({'hasMinValue': hasMinValue})
        if 'minValue' in keys or 'all' in keys and hasMinValue:
            minValue = cmds.attributeQuery(attribute, node=source, minimum=True)
            if isinstance(minValue, list):
                minValue = minValue[0]
            values.update({'minValue': minValue})

    if 'hasSoftMaxValue' in keys or 'all' in keys:
        hasSoftMaxValue = cmds.attributeQuery(attribute, node=source, softMaxExists=True)
        if isinstance(hasSoftMaxValue, list):
            hasSoftMaxValue = hasSoftMaxValue[0]
        values.update({'hasSoftMaxValue': hasSoftMaxValue})
        if 'softMaxValue' in keys or 'all' in keys and hasSoftMaxValue:
            softMaxValue = cmds.attributeQuery(attribute, node=source, minimum=True)
            if isinstance(softMaxValue, list):
                softMaxValue = softMaxValue[0]
            values.update({'softMaxValue': softMaxValue})

    if 'hasSoftMinValue' in keys or 'all' in keys:
        hasSoftMinValue = cmds.attributeQuery(attribute, node=source, softMinExists=True)
        if isinstance(hasSoftMinValue, list):
            hasMaxValue = hasSoftMinValue[0]
        values.update({'hasSoftMinValue': hasSoftMinValue})

        if 'softMinValue' in keys or 'all' in keys and hasSoftMaxValue:
            softMinValue = cmds.attributeQuery(attribute, node=source, minimum=True)
            if isinstance(softMinValue, list):
                softMinValue = softMinValue[0]
            values.update({'softMinValue': softMinValue})

    return values


def transferAttributes(source, target, attributes=None):
    if not attributes:
        attributes = getAttributes(source)
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
            elif values['type'] == 'string':
                cmds.addAttr(target,
                             longName=values['longName'],
                             dt="%s" % values['type'],
                             hidden=values['hidden'],
                             keyable=True)
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



        print("CopyAttr on: ", source, " -> ", target)

        from Maya_Functions.general_util_functions import unlockOutputConnections
        locked = unlockOutputConnections(source)
        cmds.copyAttr(source, target,
                      values = True,
                      inConnections = True,
                      outConnections = True,
                      keepSourceConnections = False,
                      attribute=[attribute])
        for to_lock in locked:
            cmds.setAttr(to_lock, lock=1)

            #self.attrValueDic[attribute] = value
            # print(type)
            # cmds.addAttr(longName=attribute, attributeType=)
            # cmds.copyAttr(source, target, values = True, attribute=attribute)

# def createVrmeshWithAttributes(source, target):
#     #print(selection)
#     unlock(source)
#     #print(' ')
#     attributes = getAttributes(source)
#     cmds.select(target)
#     target = cmds.vrayCreateProxy(node='VRayProxy', dir='C:/Users/mmcb', fname='C:/Users/mmcb/vray.vrmesh', exportType=1,
#                          createProxyNode=True, existing=False, previewFaces=1000,overwrite=True, vertexColorsOn=True,
#                          ignoreHiddenObjects=True, previewType="clustering")
#     #print(target)
#     transferAttributes(source, target, attributes)

