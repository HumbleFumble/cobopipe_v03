import maya.cmds as cmds
import os
from Log.CoboLoggers import getLogger
logger = getLogger()

from getConfig import getConfigClass
CC = getConfigClass()

import pprint
pp = pprint.PrettyPrinter(indent=4)

def InstanceRef(cur_obj_list=None):
    return_list = []
    if not cur_obj_list:
        cur_obj_list = cmds.ls(sl=True)
    for obj in cur_obj_list:
        cur_namespace = obj
        if "|" in cur_namespace:
            cur_namespace = cur_namespace.split("|")[-1]
        cur_namespace = ":".join(cur_namespace.split(":")[:-1])
        cmds.namespace(set=cur_namespace)
        return_list.append(cmds.instance(obj))
        cmds.namespace(set=":")
    return return_list

def removeProxyShaderIssueEdits():
    import maya.mel as mel
    my_sel = cmds.file(q=True, r=True)
    for sel in my_sel:
        my_ref = cmds.referenceQuery(sel, rfn=True)

        ref_edits = cmds.referenceQuery(my_ref, es=True, scs=True, ec="disconnectAttr")
        if ref_edits:
            proceed_next = False
            for check in ref_edits:
                if "VRayProxyPreview" in check or "VRayProxy_vraymeshmtlSG" in check:
                    print(check)
                    proceed_next = True
            if proceed_next:
                print("WORKING ON %s" % ref_edits)
                cmds.file(ur=my_ref)
                for e in ref_edits:
                    if "VRayProxyPreview" in e or "VRayProxy_vraymeshmtlSG" in e:
                        e_cmd = e.split(" ")[-2].split("|")[-1]
                        if not e_cmd != "":
                            mel_cmd = 'referenceEdit -failedEdits true -successfulEdits true -editCommand disconnectAttr -removeEdits "%s "%s";' % (
                            e_cmd, my_ref)
                            print("Trying to remove: %s" % mel_cmd)
                            mel.eval("%s" % mel_cmd)
                cmds.file(lr=my_ref)
            else:
                print("Found No proxy edits")

def RemoveRefEdit(search_filter=["colorSpace"], exclude_filter=["instObjGroups","translate","rotate","scale"],attr_cmds=["setAttr","connectAttr","disconnectAttr"]):
    all_refs = cmds.file(q=True, r=True)
    for c_ref in all_refs:
        for cmd_attr in attr_cmds:
            ref_edits = cmds.referenceQuery(c_ref, es=True, scs=True, ec=cmd_attr)
            logger.info(ref_edits)
            for e in ref_edits:
                remove_edit = True
                if search_filter:
                    remove_edit = False
                for search_fil in search_filter:
                    if search_fil in e:
                        remove_edit = True
                for exclude_fil in exclude_filter:
                    if exclude_fil in e:
                        remove_edit = False
                if remove_edit:
                    e_cmd = e.split(" ")[1]
                    logger.info("On %s trying to remove ref edits with: %s" % (c_ref, search_filter))
                    # print("On %s trying to remove ref edits with: %s" % (c_ref, search_filter))
                    cmds.referenceEdit(e_cmd, failedEdits=True, successfulEdits=True, removeEdits=True,editCommand=cmd_attr)


# Converts fullPath to OpenMaya API DagNode
# (Avoid if possible)
def getDagNode(fullPath):
    import maya.OpenMaya as om
    if not cmds.objExists(fullPath):
        return None
    else:
        selectionList = om.MSelectionList()
        selectionList.add(fullPath)
        dagPath = om.MDagPath()
        selectionList.getDagPath(0, dagPath)
        return dagPath


# def replaceInstancesBasedOnNamespace(cur_namespace=None,selection=True):
#
#     if selection:
#         selected = cmds.ls(sl=True,l=True)
#     all_instance = getInstances()
#     namespace_instances = []
#     for cur_i in all_instance:
#         if "|%s:" % cur_namespace in cur_i:
#             namespace_instances.append(cur_i)
#     orig = getOriginal(namespace_instances[0])
#     orig_parent = cmds.listRelatives(orig, p=True, type="transform", f=True)[0]
#     sorted_list = sorted(list(set(namespace_instances)))
#     # print("ORG: %s -> %s" %(orig,orig_parent))
#     # for s in sorted_list:
#     #     print(s)
#
#     # print("Sorted List: %s" % sorted_list)
#     print("FOUND: %s as orig based on %s" % (orig, namespace_instances[0]))
#     for cur_ni in sorted_list:
#         if cmds.objExists(cur_ni):
#             print("Starting on: %s" % cur_ni)
#             cur_parent = cmds.listRelatives(cur_ni, p=True, type="transform", f=True)[0]
#             if selection:
#                 if not cur_parent in selected:
#                     continue
#                 else:
#                     print("Found %s in %s" % (cur_parent,selected))
#             if not cur_parent == orig_parent:
#                 print("Doing stuff to %s" % cur_parent)
#                 cur_goal = cmds.xform(cur_parent, q=True, matrix=True, ws=True)
#                 instance_parent = cmds.listRelatives(cur_parent, p=True, type="transform", f=True)[0]
#                 new_instance = InstanceRef([orig_parent])[0]
#                 print("Moving %s" % new_instance)
#
#                 cmds.xform(new_instance, matrix=cur_goal, ws=True)
#                 cmds.parent(new_instance, instance_parent)
#
#                 print("Unparent %s" % cur_parent)
#                 cmds.parent(cur_parent, w=True)


# Gets all instanced nodes in the scene (Not the same as instance reference)
def getInstances():
    import maya.OpenMaya as om
    instances = []
    iterDag = om.MItDag(om.MItDag.kBreadthFirst)
    while not iterDag.isDone():
        instanced = om.MItDag.isInstanced(iterDag)
        if instanced:
            instances.append(iterDag.fullPathName())
        iterDag.next()
    return instances


# Checks if current node is instanced (Not the same as an instance reference)
def isInstancedNode(fullPath):
    from general_util_functions import isShape
    if not cmds.objExists(fullPath):
        return None
    else:
        if isShape(fullPath):
            shape = fullPath
        else:
            shape = cmds.listRelatives(fullPath, shapes=True, fullPath=True)[0]
        dag_node = getDagNode(shape)
        return dag_node.isInstanced()


# Verifies if the node is a proxy reference
def isProxy(ref_node):
    if cmds.referenceQuery(ref_node, isNodeReferenced=True):
        ref_path = cmds.referenceQuery(ref_node, filename=True)
        type = ref_path.split('/')[-1].split('.')[0].split('_')[-1]
        if type == 'Proxy':
            return True
    return False


# Verifies if the node is an ingest reference
def isIngest(ref_node):
    if cmds.referenceQuery(ref_node, isNodeReferenced=True):
        ref_path = cmds.referenceQuery(ref_node, filename=True)
        type = ref_path.split('/')[-1].split('.')[0].split('_')[-1]
        if type == 'Ingest':
            return True
    return False

# Verifies if the node is a render reference
def isRender(ref_node):
    if cmds.referenceQuery(ref_node, isNodeReferenced=True):
        ref_path = cmds.referenceQuery(ref_node, filename=True)
        type = ref_path.split('/')[-1].split('.')[0].split('_')[-1]
        if type == 'Render':
            return True
    return False


# Verifies if the node is an anim reference
def isAnim(ref_node):
    if cmds.referenceQuery(ref_node, isNodeReferenced=True):
        ref_path = cmds.referenceQuery(ref_node, filename=True)
        type = ref_path.split('/')[-1].split('.')[0].split('_')[-1]
        if type == 'Anim':
            return True
    return False


# Verifies if the node is an instance of a proxy
def isInstance(node):
    from Maya_Functions.general_util_functions import isShape

    # Making sure we are working with long name
    node = cmds.ls(node, long=True)[0]

    # Making sure we have the shape and the transform
    if not isShape(node):
        shape = cmds.listRelatives(node, shapes=True, fullPath=True)
        if shape:
            shape = shape[0]
        else:
            return False
        node = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
    else:
        shape = node
        parent = cmds.listRelatives(shape, parent=True, fullPath=True)
        if parent:
            node = parent[0]

    # If shape is referenced and the node above the shape is an instanced node but not reference we can be sure it is an instanced node
    if cmds.referenceQuery(shape, isNodeReferenced=True):
        if not cmds.referenceQuery(node, isNodeReferenced=True):
            if isInstancedNode(node):
                return True
    return False


# Returns the type of reference (ingest, proxy or instance)
def getReferenceType(node):
    if isInstance(node):
        return 'Instance'
    else:
        if cmds.referenceQuery(node, isNodeReferenced=True):
            if isProxy(node):
                return 'Proxy'
            elif isIngest(node):
                return 'Ingest'
            elif isRender(node):
                return 'Render'
            elif isAnim(node):
                return 'Anim'
            else:
                return None


# Finds the source of the given instance
def getOriginal(fullPath):
    from general_util_functions import isShape
    if not cmds.objExists(fullPath):
        return None
    else:
        if isShape(fullPath):
            returnShape = True
            shape = fullPath
            parent = cmds.listRelatives(shape, parent=True, fullPath=True)[0]
        else:
            if cmds.nodeType(fullPath) == 'transform':
                returnShape = False
                parent = fullPath
                shape = cmds.listRelatives(parent, shapes=True, fullPath=True)[0]
            else:
                return None
        # transform_nodes = cmds.ls(type='transform', long=True)
        # for transform_node in transform_nodes:
        #     temp_shapes = cmds.listRelatives(transform_node, shapes=True, fullPath=True)
        #     if temp_shapes:
        #         for temp_shape in temp_shapes:
        #             if temp_shape.split('|')[-1] == shape.split('|')[-1]:
        #                 print(temp_shape)
        #                 temp_parent = cmds.listRelatives(temp_shape, parent=True, fullPath=True)[0]
        #                 if isInstancedNode(temp_parent) and cmds.referenceQuery(temp_parent, isNodeReferenced=True):
        #                     if returnShape:
        #                         return temp_shape
        #                     else:
        #                         return temp_parent

        temp_shape = cmds.ls(shape.split('|')[-1], long=True)[0]
        temp_parent = cmds.listRelatives(temp_shape, parent=True, fullPath=True)[0]
        if isInstancedNode(temp_parent) and cmds.referenceQuery(temp_parent, isNodeReferenced=True):
            if returnShape:
                return temp_shape
            else:
                return temp_parent



# Finds all Proxy references that is the source of an instance
def getInstanceSources():
    from Maya_Functions.general_util_functions import isShape
    instances = getInstances()
    sources = {}
    for instance in instances:
        if '|' in instance:
            shortName = instance.split('|')[-1]
        if ':' in instance:
            shortName = shortName.split(':')[-1]
        if 'VRay' not in shortName:
            if isShape(instance):
                parent = cmds.listRelatives(instance, parent=True, fullPath=True)[0]
                if not cmds.referenceQuery(parent, isNodeReferenced=True):
                    source = getOriginal(parent)
                    if source:
                        if source not in sources.keys():
                            sources[source] = [parent]
                        else:
                            if parent not in sources[source]:
                                sources[source].append(parent)
    return sources


# def sortDictionary(unsorted, sortKey, identifier):
#     sorted = {}
#     for temp in unsorted:
#         key = str(temp[sortKey])
#         identity = temp[identifier]
#         if key not in sorted.keys():
#             sorted[key] = [identity]
#         else:
#             sorted[key].append(identity)
#     return sorted


# def instanceProxies(nodes):
#     # Fetches all instanced proxies in the scene
#     sourceNodes = getInstanceSources()
#     print(sourceNodes)
#
#     if type(nodes) != type([]):
#         nodes = [nodes]
#
#     # Gets all references in scene and sort them by file path
#     ref_dict = {}
#     for node in nodes:
#         if isProxy(node):
#             ref_node = cmds.referenceQuery(node, referenceNode=True)
#             ref_path = cmds.referenceQuery(ref_node, filename=True).split('{')[0]
#             if ref_path in ref_dict.keys():
#                 ref_dict[ref_path].append(ref_node)
#             else:
#                 ref_dict[ref_path] = [ref_node]
#
#     # Gets all the information needed to instance all references
#     assets = []
#     for path, nodes in ref_dict.iteritems():
#         unsorted = []
#         for node in nodes:
#             asset = {'ref_node': node}
#             proxy = None
#             for referencedNode in cmds.referenceQuery(node, nodes=True, dagPath=True):
#                 if referencedNode.split(':')[-1] == 'Proxy':
#                     proxy = cmds.ls(referencedNode, long=True)[0]
#             if proxy:
#                 attributes = cmds.listAttr(proxy, userDefined=True)
#                 dict = {}
#                 if attributes != None:
#                     for attribute in attributes:
#                         dict[attribute] = cmds.getAttr(proxy + '.' + attribute)
#                     asset['customAttributes'] = dict
#             unsorted.append(asset)
#         if 'customAttributes' in unsorted[0].keys():
#             sorted = sortDictionary(unsorted, 'customAttributes', 'ref_node')
#         unsortedOriginals = []
#         if sourceNodes:
#             for node in sourceNodes.keys():
#                 asset = {'ref_node': node}
#                 proxy = None
#                 for referencedNode in cmds.referenceQuery(node, nodes=True, dagPath=True):
#                     if referencedNode.split(':')[-1] == 'Proxy':
#                         proxy = cmds.ls(referencedNode, long=True)[0]
#                 if proxy:
#                     attributes = cmds.listAttr(proxy, userDefined=True)
#                     dict = {}
#                     if attributes != None:
#                         for attribute in attributes:
#                             dict[attribute] = cmds.getAttr(proxy + '.' + attribute)
#                         asset['customAttributes'] = dict
#                 unsortedOriginals.append(asset)
#             if 'customAttributes' in unsorted[0].keys():
#                 sortedOriginals = sortDictionary(unsortedOriginals, 'customAttributes', 'ref_node')
#
#             for key, nodes in sorted.iteritems():
#                 proxies = []
#                 targetNode = None
#                 for node in nodes:
#                     proxy = None
#                     for referencedNode in cmds.referenceQuery(node, nodes=True, dagPath=True):
#                         if referencedNode.split(':')[-1] == 'Proxy':
#                             proxy = cmds.ls(referencedNode, long=True)[0]
#                     if proxy:
#                         proxies.append(proxy)
#                 for i, node in enumerate(nodes):
#                     proxy = None
#                     for referencedNode in cmds.referenceQuery(node, nodes=True, dagPath=True):
#                         if referencedNode.split(':')[-1] == 'Proxy':
#                             proxy = cmds.ls(referencedNode, long=True)[0]
#                     if proxy:
#                         if proxy not in sourceNodes.keys():
#                             asset = {'ref_node': node}
#                             preSource = None
#                             if key in sortedOriginals.keys():
#                                 if cmds.referenceQuery(sortedOriginals[key][0], filename=True).split('{')[0] == path:
#                                     preSource = sortedOriginals[key][0]
#                             else:
#                                 for item in proxies:
#                                     print('item: ' + str(item))
#                                     if item in sourceNodes.keys():
#                                         preSource = item
#                             if not preSource:
#                                 if i == 0:
#                                     targetNode = proxy
#                                     asset['targetNode'] = targetNode
#                                     asset['clone'] = False
#                                 else:
#                                     asset['targetNode'] = targetNode
#                                     asset['clone'] = True
#                             else:
#                                 targetNode = preSource
#                                 asset['targetNode'] = targetNode
#                                 asset['clone'] = True
#                             asset['path'] = path
#                             asset['xform'] = cmds.xform(proxy, query=True, ws=True, matrix=True)
#                             asset['proxy'] = proxy
#                             asset['namespace'] = cmds.referenceQuery(node, namespace=True).replace(':', '')
#                             if cmds.listRelatives(proxy, parent=True, f=True):
#                                 asset['parent'] = cmds.listRelatives(proxy, parent=True, f=True)[0]
#                             else:
#                                 asset['parent'] = None
#                             assets.append(asset)
#                         else:
#                             logger.info(proxy + ' already instanced')
#
#     # Instances all references using the collected information
#     for asset in assets:
#         print(asset)
#         if asset['clone']:
#             original_namespace = cmds.referenceQuery(asset['targetNode'], ns=True)
#             if original_namespace:
#                 if original_namespace != cmds.namespaceInfo(currentNamespace=True):
#                     cmds.namespace(set=':' + original_namespace)
#             instanceObject = cmds.instance(asset['targetNode'], name='Proxy')
#             cmds.namespace(set=':')
#             cmds.xform(instanceObject, matrix=asset['xform'])
#             if cmds.objExists(asset['ref_node']):
#                 exact_path = cmds.referenceQuery(asset['ref_node'], filename=True)
#                 cmds.file(exact_path, removeReference=True)
#             if asset['parent']:
#                 if cmds.listRelatives(instanceObject, parent=True, f=True):
#                     if cmds.listRelatives(instanceObject, parent=True, f=True)[0] != asset['parent']:
#                         cmds.parent(instanceObject, asset['parent'])


# Gets the necessary info to create an ingest, proxy or instance reference from existing reference of either type


# Gets the main node containing transformations and user defined attributes (Proxy/superRoot)
def getMainNode(node):
    type = getReferenceType(node)

    if type in ['Proxy']:
        if not node.split(':')[-1] == 'Proxy':
            referenced_nodes = cmds.referenceQuery(node, nodes=True)
            for referenced_node in referenced_nodes:
                if referenced_node.split(':')[-1] == 'Proxy':
                    node = cmds.ls(referenced_node, long=True)[0]

    elif type in ['Instance']:
        if 'Proxy' not in node.split(':')[-1]:
            referenced_nodes = cmds.referenceQuery(node, nodes=True)
            for referenced_node in referenced_nodes:
                if 'Proxy' in referenced_node.split(':')[-1]:
                    node = cmds.ls(referenced_node, long=True)[0]

    elif type in ['Ingest']:
        if not node.split(':')[-1] == 'SuperRoot_Ctrl':
            referenced_nodes = cmds.referenceQuery(node, nodes=True)
            for referenced_node in referenced_nodes:
                if referenced_node.split(':')[-1] == 'SuperRoot_Ctrl':
                    node = cmds.ls(referenced_node, long=True)[0]

    return node

def getReferenceInfo(node, skipTarget=False):
    ref_dict = {}
    ref_dict['type'] = getReferenceType(node)

    # Making sure we have the right node to take info from
    node = getMainNode(node)
    ref_dict['node'] = node
    if ref_dict['type'] == 'Instance':
        shape = cmds.listRelatives(node, shapes=True)
        if shape:
            shape = shape[0]
        ref_dict['ref_node'] = cmds.referenceQuery(shape, referenceNode=True)
        ref_dict['ref_path'] = cmds.referenceQuery(shape, filename=True)
    else:
        ref_dict['ref_node'] = cmds.referenceQuery(node, referenceNode=True)
        ref_dict['ref_path'] = cmds.referenceQuery(node, filename=True)
    ref_dict['path'] = ref_dict['ref_path'].split('{')[0]
    ref_dict['asset_name'] = ref_dict['path'].split('/')[8]
    xform_node = node #Check if Root_Ctrl should be the xform goal, otherwise use the node as xform.
    if ref_dict['type'] == "Ingest": # If type = ingest, check for Root_Ctrl
        node_children = cmds.listRelatives(node,ad=True,fullPath=True)
        for child in node_children:
            if child.endswith("Root_Ctrl"):
                xform_node = child
    ref_dict['xform'] = cmds.xform(xform_node, query=True, ws=True, matrix=True)
    if node.split(':')[-1] == 'SuperRoot_Ctrl':
        for item in cmds.referenceQuery(node, nodes=True):
            if item.split(':')[-1] == 'Geo_Group':
                parent = cmds.listRelatives(item, parent=True, f=True)
        else:
            logger.warning('Could not find Geo_Group in Ingest reference')
    else:
        parent = cmds.listRelatives(node, parent=True, f=True)
    if parent:
        ref_dict['parent'] = parent[0]
    else:
        ref_dict['parent'] = None

    attributes = cmds.listAttr(node, userDefined=True)
    attr_dict = {}
    if attributes != None:
        for attribute in attributes:
            attr_dict[attribute] = cmds.getAttr(node + '.' + attribute)
    ref_dict['customAttributes'] = attr_dict

    if not skipTarget:
        ref_dict['target'] = None
        targetList = []
        instanceSources = getInstanceSources()
        for source in instanceSources.keys():
            source_path = cmds.referenceQuery(source, filename=True).split('{')[0]
            if not ref_dict['target']:
                if source_path == ref_dict['path']:
                    attributes = cmds.listAttr(source, userDefined=True)
                    attr_dict = {}
                    if attributes != None:
                        for attribute in attributes:
                            attr_dict[attribute] = cmds.getAttr(source + '.' + attribute)
                    if ref_dict['customAttributes'] == attr_dict:
                        ref_dict['target'] = source

        if not ref_dict['target']:
            paths = cmds.file(query=True, reference=True)
            for path in paths:
                if ref_dict['path'] == path.split('{')[0]:
                    if not ref_dict['ref_path'] == path:
                        if cmds.referenceQuery(path, isLoaded=True):
                            referenced_nodes = cmds.referenceQuery(path, nodes=True)
                            if referenced_nodes:
                                for referenced_node in referenced_nodes:
                                    if not ref_dict['target']:
                                        if referenced_node.split(':')[-1] == 'Proxy':
                                            attributes = cmds.listAttr(referenced_node, userDefined=True)
                                            attr_dict = {}
                                            if attributes != None:
                                                for attribute in attributes:
                                                    attr_dict[attribute] = cmds.getAttr(referenced_node + '.' + attribute)
                                            if ref_dict['customAttributes'] == attr_dict:
                                                ref_dict['target'] = referenced_node
                            else:
                                print("Can't find reference to %s - gets %s" % (path, referenced_nodes))
                        else:
                            print("Skipping: %s - because its unloaded" % path)
    return ref_dict


# Instances a proxy given the proxy itself is not the source of any instance
# and there exists another proxy of the same of the same path and matching user defined attributes
def instanceProxy(proxy, info=None, skipProxyCheck=False, skipSourceCheck=False):
    # Checks if the object is indeed a proxy by our pipeline standards.
    if skipProxyCheck:
        isProxy_check = True
    else:
        isProxy_check = isProxy(proxy)

    # Checks if the proxy is currently source for an instance
    if skipSourceCheck:
        isSource = True
    else:
        if getOriginal(proxy) == None:
            isSource = True
        else:
            isSource = False

    # Disregards if not proxy or check was skipped
    if isProxy_check:
        # Disregards if the proxy is currently source for an instance or check was skipped
        if isSource:
            if not info:
                info = getReferenceInfo(proxy)
            if info['target']:
                logger.info('Instancing ' + proxy + ' from ' + info['target'])
                instanceObject = cmds.instance(info['target'], name=info['target'].split('|')[-1].split(':')[0] + ':Proxy')
                cmds.xform(instanceObject, matrix=info['xform'])
                if cmds.objExists(info['ref_node']):
                    exact_path = cmds.referenceQuery(info['ref_node'], filename=True)
                    cmds.file(exact_path, removeReference=True)
                if info['parent']:
                    if cmds.listRelatives(instanceObject, parent=True, f=True):
                        if cmds.listRelatives(instanceObject, parent=True, f=True)[0] != info['parent']:
                            cmds.parent(instanceObject, info['parent'])
                    else:
                        cmds.parent(instanceObject, info['parent'])
                return instanceObject[0]
    return None


# Returns all proxy references in a scene
def getAllProxyNodes():
    proxyNodes = []
    paths = cmds.file(query=True, reference=True)
    for path in paths:
        nodes = cmds.referenceQuery(path, nodes=True)
        if nodes:
            for node in nodes:
                if node.split(':')[-1] == 'Proxy':
                    node = cmds.ls(node, long=True)[0]
                    if isProxy(node):
                        proxyNodes.append(node)
    return proxyNodes

def reconnectVrayProperties():
    if cmds.objExists("vraySettings"):
        for vs in cmds.ls(type="VRayObjectProperties"):
            if not cmds.listConnections("%s.outConnect" % vs):
                logger.debug("Connecting %s to vraySettings" % vs)
                cmds.connectAttr("%s.outConnect" % vs, "vraySettings.vray_nodes_connect", na=True, f=True)

def instanceScene():
    logger.info('Running InstanceScene')
    proxyNodes = getAllProxyNodes()
    assets = {}
    for proxyNode in proxyNodes:
        info = getReferenceInfo(proxyNode, skipTarget=True)
        if not info['asset_name'] in assets.keys():
            assets[info['asset_name']] = {}

        if str(info['customAttributes']) in assets[info['asset_name']].keys():
            assets[info['asset_name']][str(info['customAttributes'])].append(info)
        else:
            assets[info['asset_name']] = {str(info['customAttributes']): [info]}

        # assets[info['asset_name']][str(info['customAttributes'])]['node'] = proxyNode

    for key, asset in assets.iteritems():

        for key, attrGroup in asset.iteritems():
            if len(attrGroup) > 1:
                # Add first in list as target for every proxy node in list
                for i, info in enumerate(attrGroup):
                    attrGroup[i]['target'] = attrGroup[0]['node']

                del attrGroup[0]

                for info in attrGroup:
                    #print(info['node'] + ' -> ' + info['target'])
                    instanceProxy(info['node'], info, skipProxyCheck=True, skipSourceCheck=True)

# Old function, came incredibly slow in big scenes
# # Instances every possible proxy in an entire scene
# def instanceScene():
#     logger.info('Running instanceScene')
#     proxyNodes = getAllProxyNodes()
#     for proxyNode in proxyNodes:
#         logger.info('Instancing: ' + str(proxyNode))
#         instanceProxy(proxyNode)


# Creates a Ingest reference based on a dictionary
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

    print('\nsuperRoot: ' + str(superRoot))
    print('xform: ' + str(info['xform']) + '\n')
    cmds.xform(superRoot, matrix=info['xform'])
    if 'customAttributes' in info.keys():
        for attribute, value in info['customAttributes'].iteritems():
            if not cmds.getAttr(superRoot + '.' + attribute, lock=True):
                try:
                    cmds.setAttr(superRoot + '.' + attribute, value)
                except:
                    try:
                        cmds.setAttr(superRoot + '.' + attribute, value, type='string')
                    except:
                        pass
    if info['parent']:
        if cmds.objExists(info['parent']):
            cmds.parent(geo_group, info['parent'])
    if cmds.objExists('|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl'):
        cmds.parent(ctrl_group, '|Root_Group|Ctrl_Group|SuperRoot_Ctrl_Group|SuperRoot_Ctrl|Root_Ctrl_Group|Root_Ctrl')
    if cmds.objExists('|Root_Group|Rig_Group'):
        cmds.parent(rig_group, '|Root_Group|Rig_Group')

    return superRoot


# Creates a proxy reference based on a dictionary
def createProxy(info):
    if "_Ingest" in info['path']:
        ref_node = cmds.file(info['path'].replace('_Ingest', '_Proxy'), reference=True, namespace=info['asset_name'])
    elif "_Render" in info['path']:
        ref_node = cmds.file(info['path'].replace('_Render', '_Proxy'), reference=True, namespace=info['asset_name'])
    else:
        ref_node = cmds.file(info['path'], reference=True, namespace=info['asset_name'])

    for referenced_node in cmds.referenceQuery(ref_node, nodes=True):
        if referenced_node.split(':')[-1] == 'Proxy':
            proxyNode = referenced_node

    cmds.xform(proxyNode, matrix=info['xform'])
    for attribute, value in info['customAttributes'].iteritems():
        if not cmds.getAttr(proxyNode + '.' + attribute, lock=True):
            try:
                cmds.setAttr(proxyNode + '.' + attribute, value)
            except:
                pass
    if info['parent']:
        cmds.parent(proxyNode, info['parent'])

    return proxyNode


# Creates a render reference based on a dictionary
def createRender(info):
    ref_node = cmds.file(info['path'], reference=True, namespace=info['asset_name'])

    for referenced_node in cmds.referenceQuery(ref_node, dagPath=True, nodes=True):
        if not cmds.listRelatives(referenced_node, parent=True):
            if cmds.objectType(referenced_node) == 'transform':
                referenced_node = cmds.ls(referenced_node, long=True)[0]
                if referenced_node.split('|')[-1].split(':')[-1] == 'Root_Group':
                    root_group = referenced_node

    if root_group:
        for node in cmds.listRelatives(root_group, allDescendents=True, type='transform'):
            node = cmds.ls(node, long=True)[0]
            if node.split('|')[-1].split(':')[-1] == 'SuperRoot_Ctrl':
                super_root = node

        if 'parent' in info.keys():
            if info['parent']:
                try:
                    cmds.parent(root_group, info['parent'])
                except:
                    logger.info("Cannot parent under " + info['parent'])



    if super_root:
        cmds.xform(super_root, ws=True, matrix=info['xform'])
        if 'customAttributes' in info.keys():
            if info['customAttributes']:
                for attribute, value in info['customAttributes'].iteritems():
                    if cmds.attributeQuery(attribute, node=super_root, keyable=True):
                        cmds.setAttr(super_root + '.' + attribute, value)
        return super_root
    elif root_group:
        return root_group
    else:
        return None


        #         referenced_node = cmds.ls(referenced_node, long=True)[0]
        #         if referenced_node.split('|')[-1].split(':')[-1] == 'SuperRoot_Ctrl':
        #             superRoot = referenced_node

    #print(superRoot)
    # ref_node = cmds.file(info['path'].replace('_Ingest', '_Proxy'), reference=True, namespace=info['asset_name'])
    # for referenced_node in cmds.referenceQuery(ref_node, nodes=True):
    #     if referenced_node.split(':')[-1] == 'Proxy':
    #         proxyNode = referenced_node
    #
    # cmds.xform(proxyNode, matrix=info['xform'])
    # for attribute, value in info['customAttributes'].iteritems():
    #     cmds.setAttr(proxyNode + '.' + attribute, value)
    # if info['parent']:
    #     cmds.parent(proxyNode, info['parent'])
    #
    # return proxyNode


# Removes a reference or instance
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


# Sorts all referenced in selected hierarchy by type
# Example of return: {'Instance': ['|node01', '|node02], 'Proxy': ['|node03'], 'Ingest': ['|node04', |group01|node05']}
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


# Removes all references selected or children of selected groups
# TODO: Check if Proxy has instances, and if yes, delete them first.
def removeReferences():
    selection = cmds.ls(sl=True, long=True)
    for i, selected in enumerate(selection):
        if cmds.objectType(selection[i]):
            selection[i] = cmds.referenceQuery(selection[i], nodes=True, dagPath=True)[0]
    sorted = referenceSortByType(selection, {})

    # Check if Proxy has instances and add them to remove list.
    if 'Proxy' in sorted.keys():
        sources = getInstanceSources()
        for node in sorted['Proxy']:
            if node in sources.keys():
                for instance in sources[node]:
                    if 'Instance' in sorted.keys():
                        sorted['Instance'].append(instance)
                    else:
                        sorted['Instance'] = [instance]

    # It is crucial to delete instances before the instanced sources
    if 'Instance' in sorted.keys():
        for node in sorted['Instance']:
            if cmds.objExists(node):
                removeReference(node)

    for type, nodes in sorted.iteritems():
        if type != 'Instance':
            for node in nodes:
                if cmds.objExists(node):
                    removeReference(node)


def RemoveUnloadedRefs():  # Removes unload refs. Does not work recursively.
    refs = cmds.file(q=True, r=True)
    for c_ref in refs:
        is_load = cmds.referenceQuery(c_ref, isLoaded=True)
        if not is_load:
            ref_file = cmds.referenceQuery(c_ref, f=True)
            # cmds.file(ref_file, rr=True, mergeNamespaceWithRoot=True)
            cmds.file(ref_file, rr=True)

def loadChildRefs():
    """
    Goes through and loads the children ref of all loaded references.
    """
    refs = cmds.file(q=True, r=True)
    for c_ref in refs:
        is_load = cmds.referenceQuery(c_ref, isLoaded=True)
        if is_load:
            child_refs = cmds.referenceQuery(c_ref, child=True, filename=True)
            if child_refs:
                for c in child_refs:
                    if not cmds.referenceQuery(c, isLoaded=True):
                        cmds.file(c, lr=True)

def RemoveRefs(remove_list):  # Remove refs by given list.
    for ref in remove_list:
        if cmds.objExists(ref):
            logger.info("Found %s! Trying to remove" % ref)
            ref_file = cmds.referenceQuery(ref, f=True)
            cmds.file(ref_file, rr=True, mergeNamespaceWithRoot=True)


def RemoveRefsFromAssetPublish(remove_list):
    ref_files = cmds.file(q=True, r=True)
    for ref in ref_files:
        for remove in remove_list:
            if remove in ref:
                # cmds.file(ref, rr=True, mergeNamespaceWithRoot=True)
                cmds.file(ref, rr=True, f=True)


def FindRefsInGroup(cur_group="Full"):
    my_childs = cmds.listRelatives("Full", children=True, ad=True)
    my_refs = cmds.ls(my_childs, rn=True)
    list_refs = []
    for cur_ref in my_refs:
        cur_refnode = cmds.referenceQuery(cur_ref, tr=True, rfn=True)
        cur_ref_path = cmds.referenceQuery(cur_refnode, filename=True)
        if not cur_ref_path in list_refs:
            list_refs.append(cur_ref_path)
    return list_refs


def ImportRefs(import_unloaded=False, remove_ns=False):  # Import refs. Recursively.
    refs = cmds.file(q=True, r=True)
    for c_ref in refs:
        ns = cmds.file(c_ref, q=True, ns=True)
        if not cmds.referenceQuery(c_ref, il=True):  # If ref is unloaded
            if import_unloaded:  # load ref if imported_unloaded is true
                cmds.file(c_ref, lr=True)
            else:  # Else remove it
                logger.warning("Removing unloaded Ref: %s" % c_ref)
                cmds.file(c_ref, rr=True)
                continue  # TODO Check if namespaces still hangs around?
        logger.info("Importing Ref: %s" % c_ref)
        cmds.file(c_ref, ir=True)  # Import reference
    if remove_ns:  # Added from Asset Publish. Used to help with sub-assets in assets.
        if cmds.namespace(exists=ns):  # Check if namespace already exists
            cmds.namespace(rm=ns, mnr=True)  # Try to merge it to avoid complications
    if cmds.file(q=True, r=True) != []:  # Recursivly check for more refs until none is left.
        ImportRefs(import_unloaded, remove_ns)
    reconnectVrayProperties() # Run a reconnect to


def ChangeRefType(change_from="Anim.mb", change_to="Render.mb"):  # Animation Publish: Flip ref to render from anim. Special Cases can be included.
    refs = cmds.file(q=True, r=True)
    for ref_path in refs:
        if change_from in ref_path:
            # find reference node
            logger.debug("Now on %s" % ref_path)
            ref_node = cmds.referenceQuery(ref_path, referenceNode=True)
            new_path = "%s%s" % (ref_path.split(change_from)[0],change_to)
            if os.path.exists(new_path):
                logger.debug("For ref: %s -> loading new path: %s" %(ref_node,new_path))
                try:
                    cmds.file(new_path, loadReference=ref_node)
                except Exception as e:
                    print(e)
            else:
                logger.info("Can't find %s to replace Anim-Ref" % new_path)


# Duplicates a reference regardless of type (ingest, proxy, instance)
def duplicateReference(node):
    type = getReferenceType(node)
    info = getReferenceInfo(node)

    if type and info:
        if type == 'Instance':
            proxy = createProxy(info)
            return instanceProxy(proxy)

        elif type == 'Proxy':
            return createProxy(info)

        elif type =='Ingest':
            return createIngest(info)

    return None


# Finds all references in hierarchy and sends them on to duplicate function
# while collecting a list of nodes to return for selection.
def handleDuplicateReference(selection, _list=[]):
    return_list = []
    if selection:
        for node in selection:
            type = getReferenceType(node)
            if type:
                node = getMainNode(node)
                if node not in _list:
                    _list.append(node)
                    output = duplicateReference(node)
                    if output:
                        if output not in return_list:
                            return_list.append(output)
            elif cmds.nodeType(node) == 'transform' and not cmds.listRelatives(node, shapes=True):
                parent = cmds.listRelatives(node, parent=True)
                if parent:
                    parent = parent[0]
                output = handleDuplicateReference(cmds.listRelatives(node, children=True, fullPath=True), _list)
                for node in output:
                    if node not in return_list:
                        return_list.append(node)
    return return_list


# Duplicates all references
def duplicateReferences():
    selection = cmds.ls(sl=True, long=True)
    output = handleDuplicateReference(selection, [])
    cmds.select(deselect=True)
    for node in output:
        cmds.select(node, add=True)


# Converts a reference from one type to another (types: Ingest, Proxy, Instance)
def convertReference(node, type):
    # Making sure we are using longname
    node = cmds.ls(node, long=True)[0]

    # Getting the current type of the reference
    currentType = getReferenceType(node)

    info = getReferenceInfo(node)

    if type == 'Ingest' and currentType != 'Ingest':
        selectTarget = createIngest(info)
        if currentType != 'Instance':
            cmds.file(info['ref_path'], removeReference=True)
        if currentType == 'Instance':
            cmds.delete(node)
    elif type == 'Proxy': # and currentType != 'Proxy':
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


# Finds the reference nodes and sends them on to convert function
# and returns a list of nodes to select (Proxy-transform/superRoot nodes)
def handleConvertReference(selection, type):
    return_list = []
    for node in selection:
        output = None
        if cmds.objExists(node):
            if getReferenceType(node):
                output = convertReference(node, type)
            elif cmds.nodeType(node) == 'transform' and not cmds.listRelatives(node, shapes=True):
                output = handleConvertReference(cmds.listRelatives(node, children=True), type)

        if output:
            return_list.append(output)
    return return_list


# Converts a reference from one type to another (Types: Ingest, Proxy, Instance)
def convertReferences(type):
    selection = cmds.ls(sl=True, long=True)
    output = handleConvertReference(selection, type)
    cmds.select(deselect=True)
    for item in output:
        cmds.select(item, add=True)


# Converts a reference from one type to another (types: Ingest, Proxy, Instance)
def convertDirtyRef(node):
    # Making sure we are using longname
    node = cmds.ls(node, long=True)[0]

    info = getDirtyRefInfo(node)

    selectTarget = createRender(info)

    cmds.lockNode(node, lock=False)
    cmds.setAttr(node + '.visibility', 0)

    if selectTarget:
        if cmds.objExists(selectTarget):
            cmds.select(selectTarget)
        return selectTarget
    else:
        return None


def handleConvertDirtyRef(selection):
    return_list = []
    for node in selection:
        output = None
        if cmds.objExists(node):
            node = dirtyRefFindRootGroup(node)
            print(node)
            if cmds.attributeQuery('assetName', node=node, exists=True):
                convertDirtyRef(node)

    # return_list = []
    # for node in selection:
    #     output = None
    #     if cmds.objExists(node):
    #         if getReferenceType(node):
    #             output = convertReference(node, type)
    #         elif cmds.nodeType(node) == 'transform' and not cmds.listRelatives(node, shapes=True):
    #             output = handleConvertReference(cmds.listRelatives(node, children=True), type)
    #
    #     if output:
    #         return_list.append(output)
    # return return_list


def convertDirtyRefs():
    selection = cmds.ls(sl=True, long=True)
    handleConvertDirtyRef(selection)
    #output = handleConvertDirtyRef(selection)
    #cmds.select(deselect=True)
    #for item in output:
    #    cmds.select(item, add=True)


def dirtyRefFindRootGroup(node):
    if node.split('|')[-1].split(':')[-1] not in ['Root_Group', 'Top_Group']:
        parent = cmds.listRelatives(node, parent=True, fullPath=True)
        if parent:
            parent = parent[0]
            output = dirtyRefFindRootGroup(parent)
            if output:
                if output.split('|')[-1].split(':')[-1] in ['Root_Group', 'Top_Group']:
                    return output
    else:
        return node

def getDirtyRefInfo(node):
    ref_dict = {}
    ref_dict['type'] = 'Dirty'

    ref_dict['asset_name'] = cmds.getAttr(node + '.' + 'assetName')
    ref_dict['asset_type'] = cmds.getAttr(node + '.' + 'assetType')
    if ref_dict['asset_type'] == 'SetDress':
        ref_dict['asset_type'] = 'Setdress'
    ref_dict['asset_category'] = cmds.getAttr(node + '.' + 'assetCategory')
    if ref_dict['asset_category'] in ['Grounds', 'Bushs', 'Trees']:
        ref_dict['asset_category'] = 'Forest'
    ref_dict['path'] = CC.getByKey_ref_paths('Render', **ref_dict)

    for child in cmds.listRelatives(node, allDescendents=True, type='transform', fullPath=True):
        if child.split('|')[-1].split(':')[-1] == 'SuperRoot_Ctrl':
            ref_dict['SuperRoot'] = child

    if 'SuperRoot' not in ref_dict.keys():
        ref_dict['xform'] = cmds.xform(node, query=True, ws=True, matrix=True)
    else:
        ref_dict['xform'] = cmds.xform(ref_dict['SuperRoot'], query=True, ws=True, matrix=True)

    if node.split(':')[-1] == 'SuperRoot_Ctrl':
        for item in cmds.referenceQuery(node, nodes=True):
            if item.split(':')[-1] == 'Geo_Group':
                parent = cmds.listRelatives(item, parent=True, f=True)
        else:
            logger.warning('Could not find Geo_Group in Ingest reference')
    else:
        parent = cmds.listRelatives(node, parent=True, f=True)
    if parent:
        ref_dict['parent'] = parent[0]
    else:
        ref_dict['parent'] = None

    if 'SuperRoot' in ref_dict.keys():
        if ref_dict['SuperRoot']:
            attributes = cmds.listAttr(ref_dict['SuperRoot'], userDefined=True)
        else:
            attributes = cmds.listAttr(node, userDefined=True)
    else:
        attributes = cmds.listAttr(node, userDefined=True)

    attr_dict = {}
    if attributes != None:
        for attribute in attributes:
            if 'SuperRoot' in ref_dict.keys():
                if ref_dict['SuperRoot']:
                    attr_dict[attribute] = cmds.getAttr(ref_dict['SuperRoot'] + '.' + attribute)
                else:
                    attr_dict[attribute] = cmds.getAttr(node + '.' + attribute)
            else:
                attr_dict[attribute] = cmds.getAttr(node + '.' + attribute)
    ref_dict['customAttributes'] = attr_dict

    # ref_dict['target'] = None
    # targetList = []
    # instanceSources = getInstanceSources()
    # for source in instanceSources.keys():
    #     source_path = cmds.referenceQuery(source, filename=True).split('{')[0]
    #     if not ref_dict['target']:
    #         if source_path == ref_dict['path']:
    #             attributes = cmds.listAttr(source, userDefined=True)
    #             attr_dict = {}
    #             if attributes != None:
    #                 for attribute in attributes:
    #                     attr_dict[attribute] = cmds.getAttr(source + '.' + attribute)
    #             if ref_dict['customAttributes'] == attr_dict:
    #                 ref_dict['target'] = source
    #
    # if not ref_dict['target']:
    #     paths = cmds.file(query=True, reference=True)
    #     for path in paths:
    #         if ref_dict['path'] == path.split('{')[0]:
    #             if not ref_dict['ref_path'] == path:
    #                 referenced_nodes = cmds.referenceQuery(path, nodes=True)
    #                 for referenced_node in referenced_nodes:
    #                     if not ref_dict['target']:
    #                         if referenced_node.split(':')[-1] == 'Proxy':
    #                             attributes = cmds.listAttr(referenced_node, userDefined=True)
    #                             attr_dict = {}
    #                             if attributes != None:
    #                                 for attribute in attributes:
    #                                     attr_dict[attribute] = cmds.getAttr(referenced_node + '.' + attribute)
    #                             if ref_dict['customAttributes'] == attr_dict:
    #                                 ref_dict['target'] = referenced_node
    return ref_dict


def lockSet(lock=True):
    print('Running lockSet(lock=%s)' % str(lock))
    refs = cmds.file(query=True, list=True, reference=True)
    refNodes = []
    targetList = []
    for ref in refs:
        if ref.endswith('.ma') or ref.endswith('.mb'):
            if '/Set/' in ref:
                for node in cmds.referenceQuery(ref, nodes=True, dp=True):
                    if cmds.objExists(node):
                        if cmds.objectType(node) in ['mesh', 'gpuCache']:
                            if node not in targetList:
                                targetList.append(node)

                            parent = cmds.listRelatives(node, parent=True, fullPath=True)[0]
                            if parent not in targetList:
                                targetList.append(parent)

                        elif cmds.objectType(node) in ['transform'] and cmds.listRelatives(node, children=True,
                                                                                           type='gpuCache'):
                            if node not in targetList:
                                targetList.append(node)

    for node in targetList:
        try:
            if lock:
                cmds.setAttr(node + '.overrideEnabled', 0)
            else:
                cmds.setAttr(node + '.overrideEnabled', 1)
        except:
            pass