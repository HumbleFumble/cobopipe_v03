from reloadModules import resetSession

resetSession()

import maya.cmds as cmds

from Maya_Functions.ref_util_functions import convertReference, getReferenceType, isProxy, isIngest, isInstance, \
    instanceProxy


def createIngest(info):
    ref_node = cmds.file(info['path'].replace('_Proxy', '_Ingest'), reference=True, namespace=info['asset_name'])
    for referenced_node in cmds.referenceQuery(ref_node, nodes=True):
        if referenced_node.split(':')[-1] == 'Geo_Group':
            geo_group = referenced_node
        elif referenced_node.split(':')[-1] == 'Rig_Group':
            rig_group = referenced_node
        elif referenced_node.split(':')[-1] == 'Ctrl_Group':
            ctrl_group = referenced_node
        elif referenced_node.split(':')[-1] == 'SuperRoot_Ctrl':
            superRoot = referenced_node

    cmds.xform(superRoot, matrix=info['xform'])
    for attribute, value in info['customAttributes'].iteritems():
        cmds.setAttr(superRoot + '.' + attribute, value)
    if info['parent']:
        if cmds.objExists(info['parent']):
            cmds.parent(geo_group, info['parent'])
    if cmds.objExists('|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl'):
        cmds.parent(ctrl_group, '|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl')
    if cmds.objExists('|Root_Group|Rig_Group'):
        cmds.parent(rig_group, '|Root_Group|Rig_Group')

    return superRoot


def createProxy(info):
    ref_node = cmds.file(info['path'].replace('_Ingest', '_Proxy'), reference=True, namespace=info['asset_name'])
    for referenced_node in cmds.referenceQuery(ref_node, nodes=True):
        if referenced_node.split(':')[-1] == 'Proxy':
            proxyNode = referenced_node

    cmds.xform(proxyNode, matrix=info['xform'])
    for attribute, value in info['customAttributes'].iteritems():
        cmds.setAttr(proxyNode + '.' + attribute, value)
    if info['parent']:
        cmds.parent(proxyNode, info['parent'])

    return proxyNode


def convertReference(node, type):
    # Making sure we are using longname
    node = cmds.ls(node, long=True)[0]

    # Getting the current type of the reference
    currentType = getReferenceType(node)

    # Making sure we have the right node for fetching information
    if currentType in ['Proxy']:
        if not node.split(':')[-1] == 'Proxy':
            referenced_nodes = cmds.referenceQuery(node, nodes=True)
            for referenced_node in referenced_nodes:
                if referenced_node.split(':')[-1] == 'Proxy':
                    node = cmds.ls(referenced_node, long=True)[0]
    elif currentType in ['Instance']:
        if 'Proxy' not in node.split(':')[-1]:
            referenced_nodes = cmds.referenceQuery(node, nodes=True)
            for referenced_node in referenced_nodes:
                if 'Proxy' in referenced_node.split(':')[-1]:
                    node = cmds.ls(referenced_node, long=True)[0]
    elif currentType in ['Ingest']:
        if not node.split(':')[-1] == 'SuperRoot_Ctrl':
            referenced_nodes = cmds.referenceQuery(node, nodes=True)
            for referenced_node in referenced_nodes:
                if referenced_node.split(':')[-1] == 'SuperRoot_Ctrl':
                    node = cmds.ls(referenced_node, long=True)[0]

    info = getReferenceInfo(node)

    if type == 'Ingest' and currentType != 'Ingest':
        selectTarget = createIngest(info)
        if currentType != 'Instance':
            cmds.file(info['ref_path'], removeReference=True)
        if currentType == 'Instance':
            cmds.delete(node)
    elif type == 'Proxy' and currentType != 'Proxy':
        selectTarget = createProxy(info)
        if currentType != 'Instance':
            cmds.file(info['ref_path'], removeReference=True)
        if currentType == 'Instance':
            cmds.delete(node)
    elif type == 'Instance' and currentType != 'Instance':
        if currentType == 'Ingest':
            proxyNode = createProxy(info)
            cmds.file(info['ref_path'], removeReference=True)
            proxyInfo = getReferenceInfo(proxyNode)
            selectTarget = instanceProxy(proxyNode, proxyInfo)
            print(selectTarget)
        elif currentType == 'Proxy':
            selectTarget = instanceProxy(node, info)

    else:
        return None

    if selectTarget:
        if cmds.objExists(selectTarget):
            cmds.select(selectTarget)
        return selectTarget
    else:
        return None


def handleConvertReference(selection, type):
    return_list = []
    for node in selection:
        output = None
        if getReferenceType(node):
            output = convertReference(node, type)
        elif cmds.nodeType(node) == 'transform' and not cmds.listRelatives(node, shapes=True):
            output = handleConvertReference(cmds.listRelatives(node, children=True), type)

        if output:
            return_list.append(output)
    return return_list


def convertReferences(type):
    selection = cmds.ls(sl=True, long=True)
    output = handleConvertReference(selection, type)
    cmds.select(deselect=True)
    for item in output:
        cmds.select(item, add=True)


def removeReference(node):
    from Maya_Functions.general_util_functions import isShape
    if isInstance(node):
        if cmds.listRelatives(node, shapes=True) and not isShape(node):
            cmds.delete(node)
        else:
            parent = cmds.listRelatives(node, parent=True, fullPath=True)
            if parent:
                parent = parent[0]
                removeReference(parent)
    elif cmds.referenceQuery(node, isNodeReferenced=True):
        path = cmds.referenceQuery(node, filename=True)
        cmds.file(path, removeReference=True)
    else:
        print('>> ' + node + ' is not a valid reference node')


def referenceSortByType(nodes, dict={}):
    if nodes:
        for node in nodes:
            type = getReferenceType(node)
            if type:
                if type not in dict.keys():
                    dict[type] = []
                if node not in dict[type]:
                    dict[type].append(node)
            elif not type and cmds.nodeType(node) == 'transform' and not cmds.listRelatives(node, shapes=True):
                output = referenceSortByType(cmds.listRelatives(node, children=True, fullPath=True), dict)
                for _type, _nodes in output.iteritems():
                    if _type not in dict:
                        dict[_type] = []
                    for _node in _nodes:
                        if _node not in dict[_type]:
                            dict[_type].append(_node)
    return dict


def removeReferences():
    nodeList = []
    selection = cmds.ls(sl=True, long=True)
    sorted = referenceSortByType(selection, {})
    if 'Instance' in sorted.keys():
        for node in sorted['Instance']:
            print('Attempting to delete: ' + str(node))
            removeReference(node)
    for type, nodes in sorted.iteritems():
        if type != 'Instance':
            for node in nodes:
                print('Attempting to delete: ' + str(node))
                removeReference(node)