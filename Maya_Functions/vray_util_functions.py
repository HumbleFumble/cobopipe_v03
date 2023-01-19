import os
import maya.cmds as cmds
import maya.mel as mel
from Log.CoboLoggers import getLogger
logger = getLogger()

from getConfig import getConfigClass
CC = getConfigClass()


def setCurrentRenderer(renderer='vray'):
    
    cmds.setAttr("defaultRenderGlobals.currentRenderer", renderer, type="string")

def createFastRenderSkySetup():
    # my_obj = "ForLight_Sphere"
    my_objs = cmds.ls("::*ForLight_Sphere")
    if not my_objs:
        my_obj = cmds.polySphere(name="ForLight_Sphere", r=1500, sx=20, sy=20, cuv=2)[0]
        obj_shape = cmds.listRelatives(my_obj, s=True, f=True)[0]
        attr_list = ["castsShadows", "receiveShadows", "visibleInReflections", "visibleInRefractions"]
        for a in attr_list:
            cmds.setAttr("%s.%s" % (obj_shape, a), 0)
    else:
        my_obj = my_objs[0]
    if cmds.objExists(my_obj):
        sky_shader = "FastRenderSky_Mtl"
        if not cmds.objExists(sky_shader):
            sky_shader = cmds.shadingNode("VRayMtl", name="FastRenderSky_Mtl", asShader=True)
            print(sky_shader)
            cmds.setAttr("%s.color" % sky_shader, 0, 0, 0, type="double3")
        sky = cmds.ls(type="VRaySky")
        if sky:
            cmds.connectAttr("%s.outColor" % sky[0], "%s.illumColor" % sky_shader, f=True)
        cmds.select(my_obj, r=True)
        cmds.hyperShade(assign=sky_shader)
    else:
        cmds.warning("Please Create a ForLight_Sphere first, and then run again")

def CreateVraySphereOnObject(constrain=False):
    current_obj = cmds.ls(sl=True)
    if current_obj:
        current_obj = current_obj[0]
        cur_namespace = ":".join(current_obj.split(":")[0:-1])
        cur_name = "_".join(current_obj.split(":")[0:-1])
        geo_group = "%s:Geo_Group" % cur_namespace
        # get world loc  of current_obj
        current_placement = cmds.xform(current_obj, q=True, translation=True, ws=True)

        # cur_distance = FindBoundingBoxAndSetRadius(bounding_group=geo_group,start_loc=current_placement)
        cur_distance = 30
        cur_volume = CreateVraySphereFade(cur_name=cur_name, cur_radius=cur_distance)
        if constrain:
            cmds.parentConstraint(current_obj, cur_volume, mo=False)
    else:
        cur_volume = CreateVraySphereFade(cur_name="SceneSphere", cur_radius=30)


def CreateVraySphereFade(cur_name="Scene", cur_object=None, cur_radius=None):
    mel.eval("vrayCreateSphereFade")
    set_volume = CreateVraySphereFadeVolume()
    sphere_volume = "%s_SphereFade" % cur_name
    sphere_fades = cmds.ls("VRaySphereFade*", type="VRaySphereFade")
    if sphere_fades:
        sphere_transforms = cmds.listRelatives(sphere_fades[0], type="transform", parent=True)
        sphere_volume = cmds.rename(sphere_transforms[0], sphere_volume)
        # sphere_volume = sphere_transforms[0]
        sphere_fade = cmds.listRelatives(sphere_volume, type="VRaySphereFade")[0]
        if cur_radius:
            cmds.setAttr("%s.radius" % sphere_fade, cur_radius * 1.2)
        else:
            cmds.setAttr("%s.radius" % sphere_fade, 50)
        sphere_group = cmds.group(sphere_volume, name="%s_Group" % sphere_volume)

        cur_message = cmds.listConnections("%s.settings" % sphere_volume)
        if cur_message:
            if not set_volume in cur_message:
                # pass
                cmds.connect("%s.message" % sphere_volume, "%s.settings" % sphere_volume, f=True)
        return sphere_group
    return None


def CreateVraySphereFadeVolume(fade_volume="KS_SphereRenderVolume"):
    # fade_volume = "KS_SphereRenderVolume"
    if not cmds.objExists(fade_volume):
        fade_volumes = cmds.ls(type="VRaySphereFadeVolume")
        if fade_volumes:
            logger.info(fade_volumes)
            cmds.rename(fade_volumes[0], fade_volume)
            cmds.setAttr("%s.affectAlpha" % fade_volume, 1)
            cmds.setAttr("%s.emptyColor" % fade_volume, 0, 0, 0, type="double3")
            cmds.setAttr("%s.falloff" % fade_volume, 0.25)
            cmds.defaultNavigation(connectToExisting=True, source=fade_volume,
                                   destination='vraySettings.cam_environmentVolume', f=True)
            return fade_volume
        else:
            return False
    return fade_volume


def ApplyVraySubDiv(c_list=[], on_off=1):
    for c_obj in c_list:
        get_shape = cmds.listRelatives(c_obj, shapes=True)[0]
        mel.eval('vray addAttributesFromGroup "%s" "vray_subdivision" %s' % (get_shape, on_off))


def CreateOrAddVraySet(set_name="", add_objects=["::Geo_Group"]):
    """This functions creates a vray disps set, that are used to apply subdiv to multi objects."""
    # import maya.mel as mel
    full_name = "%s_SubDivSet" % set_name
    if not cmds.objExists(full_name):
        cmds.createNode("VRayDisplacement", n="%s" % full_name)
        mel.eval('vray addAttributesFromGroup "%s" "vray_subdivision" %s' % (full_name, 1))
    cmds.sets(add_objects, add=full_name)


def CreateVrayObjectSet(set_name="", obj_list=None, selection=True, use_force=True):
    """This functions creates a vray object set, that are used for applying shadow matte to multiple objects or setting OIDs"""
    sel = cmds.ls(sl=True)
    final_set = set_name
    if not selection:
        cmds.select(clear=True)
    if obj_list and not sel == obj_list:
        cmds.select(obj_list, r=True)
    if not cmds.objExists(set_name):
        obj = mel.eval('vray "objectProperties" "add_single" "VRayObjectProperties" "%s" "force"' % set_name)
        final_set = cmds.rename(obj, set_name)  # might need a [0]
    if obj_list:
        if use_force:
            cmds.sets(obj_list, edit=True, forceElement=set_name)
        else:
            cmds.sets(obj_list, edit=True, include=set_name)
    return final_set

def SetOIDonObjectSet(set_name="", cur_ID=None):
    cmds.setAttr("%s.objectIDEnabled" % set_name, 1)
    cmds.setAttr("%s.objectID" % set_name, cur_ID)


def SetOIDonObjs(object_list=None, cur_ID=None):
    if object_list and cur_ID:
        for c_obj in object_list:
            mel.eval('vray addAttributesFromGroup "%s" "vrayObjectID" %s' % (c_obj, 1))
            cmds.setAttr("%s.vrayObjectID" % c_obj, cur_ID)


def createVrayAttribute(node, attribute):
    mel.eval('vray addAttributesFromGroup "%s" "%s" %s' % (node, attribute, 1))


def SetVrayObjectSetToBlackMatte(set_name=None):
    if not cmds.objExists(set_name):
        CreateVrayObjectSet(set_name, None, False)
    if cmds.objExists(set_name):
        cmds.setAttr("%s.matteSurface" % set_name, 1)
        cmds.setAttr("%s.shadows" % set_name, 1) # Issue with shadows on your matte? This is the problem. Set to 0 to fix
        cmds.setAttr("%s.affectAlpha" % set_name, 1)
        cmds.setAttr("%s.alphaContribution" % set_name, -1)

def createBubbleVFXSet():
    name = "Bubble_VFX_Set"
    SetVrayObjectSetToBlackMatte(name)
    cmds.setAttr("%s.refractionVisibility" % name,0)

def migrateColorspace():
    import maya.mel as mel
    import maya.app.renderSetup.views.renderSetupPreferences as prefs
    prefs.loadUserPreset("KS_FastBrute")

    ref_list = cmds.file(q=True, r=True)
    if not "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/Set/SkyDome/Day/02_Ref/Day_Render.mb" in ref_list:
        cmds.file("P:/930383_KiwiStrit3/Production/Assets/3D_Assets/Set/SkyDome/Day/02_Ref/Day_Render.mb", r=True,
                  namespace="Day")

    # RENDER FOR PRE CHECK

    ## Migrate vray legacy scene
    ##mel.eval("vrayCreateVRaySettingsNode")
    cmds.vrend() #Renders base

    cmds.colorManagementPrefs(e=True, cme=True)
    cmds.colorManagementPrefs(cma=True)

    # Apply colormanagement default rule

    # RENDER FOR POST CHECK

def turnOverrideOnOff(search_name="",node_type=None,on_off=True):
    if node_type:
        nodes = cmds.ls("*::%s" % search_name,type=node_type)
    else:
        nodes = cmds.ls("*::%s" % search_name)
    for node in nodes:
        cmds.setAttr("%s.vrayEnableAllOverrides" % node,on_off)

def applyOverrideToAllNamed(search_name="",node_type=None,override_plug=None):
    if node_type:
        nodes = cmds.ls("*::%s" % search_name,type=node_type)
    else:
        nodes = cmds.ls("*::%s" % search_name)
    print("looked for: %s, found: %s" % (search_name,nodes))
    if not override_plug:
        if cmds.ls(sl=True):
            override_plug = cmds.ls(sl=True)[0]
        else:
            print("No override plug given, selecting found nodes instead")
            cmds.select(nodes, r=True)
            return False
    for node in nodes:
        addMaterialOverrideToNode(node=node,override_plug=override_plug)



def addMaterialOverrideToNode(node=None,override_plug=None):
    """
    add a vray material override to the given node. If override_plug is given, it will also connect it.
    :param node: The material node you want to put the override on
    :param override_plug: The material you want to override with. If not a plug/attr is given, it will assume it should be .OutColor
    :return:
    """
    cmds.vray("addAttributesFromGroup", node, "vray_specific_mtl", 1)
    if override_plug:
        if not "." in override_plug:
            override_plug = "%s.outColor" % override_plug
        cmds.connectAttr(override_plug,"%s.vraySpecificSurfaceShader" % node,f=True)


def createVrayProxy(out_path="", mesh_group='Full', previewFaces=1000, crtProxy=True,newProxyNode=True):

    out_folder, out_file = os.path.split(out_path)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    cmds.select(mesh_group, r=True)
    cmds.lockNode(mesh_group, lock=False)
    cmds.setAttr("%s.visibility" % mesh_group,1)
    logger.info('VRAY ITEMS :' + str(cmds.listRelatives(mesh_group, c=True)))
    # Changed name to VRayProxy
    result = cmds.vrayCreateProxy(node='VRayProxy', dir='%s/' % (out_folder), fname=out_file,
                                  exportType=1, createProxyNode=crtProxy, existing=False, previewFaces=previewFaces,
                                  overwrite=True, oneVoxelPerMesh=True,
                                  vertexColorsOn=True, ignoreHiddenObjects=True, previewType="clustering",newProxyNode=newProxyNode)
    # result = cmds.vrayCreateProxy(node='Full', dir='%s/' % (out_folder), fname='%s.vrmesh' % (asset_name),
    # 							  exportType=1, createProxyNode=crtProxy, existing=False, previewFaces=previewFaces,
    # 							  overwrite=True,
    # 							  vertexColorsOn=True, ignoreHiddenObjects=True, previewType="clustering")
    vrayNode = None
    if result:
        #print("RESULT: %s -> %s" % (result,out_file))
        vrayNode = result[0]
        # return vrayNode since new vray proxy node returns "world" instead of proxy name, we will try to use the name given instead
        return "VRayProxy"
    else:
        return None



def refreshProxyCache():
    import maya.mel as mel
    mel.eval("vrayClearProxiesPreviewCache")
    mel.eval("vrayClearGeomCache")


def setVrayProxyDisplay(node):
    nodes = node
    if not isinstance(node, list):
        nodes = [node]
    for i in nodes:
        if i:
            logger.info('V_NODE : %s' % i)
            vray_vis = i + ".lodVisibility"
            cmds.setAttr(vray_vis, 0)


def ReplaceVrayProxyWithMesh(refs=None):
    from Maya_Functions.general_util_functions import Align
    logger.info("Replacing vray proxies with mesh for publishing as a proxy")
    import maya.mel as mel
    if not refs:
        refs = cmds.file(q=True, r=True)
    for ref in refs:
        if "/Setdress/" in ref:  # if there is a setdress proxy
            cur_ns = cmds.referenceQuery(ref, ns=True)[1:]  # get namespace
            cmds.file(ref, ir=True)  # import the ref
            vmesh = "%s:VRayProxy_vraymesh" % cur_ns
            if cmds.objExists(vmesh):
                mel.eval('vray restoreMesh "%s"' % vmesh)
                vmesh_restored = cmds.listRelatives(cmds.ls(sl=True), parent=True, type="transform")
                vmesh_restored = cmds.rename(vmesh_restored, "%s:TempMesh" % cur_ns)
                cmds.select(vmesh_restored, r=True)
                mel.eval(
                    'polyCleanupArgList 4 { "0","1","0","0","0","0","0","0","1","1e-05","1","1e-05","0","1e-05","0","-1","0","0" }')

            else:
                logger.warning("can't find: %s" % vmesh)
                return False
            all_placements = cmds.ls("*%s:Proxy*" % cur_ns, type="transform")
            for p in all_placements:
                p_parent = cmds.listRelatives(p, parent=True, f=True)
                p_obj = cmds.duplicate(vmesh_restored, n="%s_tempMesh" % p)[0]
                Align(p, p_obj)
                cmds.setAttr("%s.visibility" % p, 0)
                if p_parent:
                    cmds.parent(p_obj, p_parent)
                cmds.delete(p)
            cmds.delete(vmesh_restored)
#TODO ADD LOGGER


def applyRenderSettings(settings, whitelist=[], blacklist=[]):
    tab = '    '
    space = ' '

    # Getting length of longest attribute to make readable print
    longestString = 0
    for render, categories in settings.items():
        for category, attributes in categories.items():
            for attribute, value in attributes.items():
                if longestString < len(attribute):
                    longestString = len(attribute)
    offset = longestString + 4

    # Run through dictionary and set attributes
    lockedAttributes = {}
    #print(tab * 0 + '\n> Applying render settings')
    for renderer, categories in settings.items():
        # print(tab * 1 + '> ' + str(renderer))
        #logger.info(tab * 1 + '> ' + str(renderer))
        for category, attributes in categories.items():
            # print(tab * 2 + '> ' + str(category))
            logger.info(tab * 2 + '> ' + str(category))

            for attribute, value in attributes.items():
                applySetting = False
                if attribute not in blacklist:
                    if whitelist:
                        if attribute in whitelist:
                            applySetting = True
                    else:
                        applySetting = True

                if applySetting:
                    type = cmds.getAttr(attribute, type=True)
                    if not type in ['message']: # These are failing, unimportant and always empty anyway
                        pStr = tab * 3
                        pStr = pStr + str(attribute)
                        pStr = pStr + (space * (offset - len(str(attribute))))
                        pStr = pStr + type
                        pStr = pStr + (space * (12 - len(type)))
                        pStr = pStr + str(value)

                        print(pStr)
                        # logger.info(pStr)

                        locked = False
                        if not cmds.getAttr(attribute, settable=True): # Checking if node is locked
                            locked = True
                            lockedAttributes[attribute] = value


                        
                        # If the attribute exist, set the value dictated by the dictionary
                        if cmds.attributeQuery(attribute.split('.')[-1], node=attribute.split('.')[0], exists=True):
                            if not locked:
                                if type in ['string']: # Need to input type for these
                                    cmds.setAttr(attribute, value, type=type)
                                elif type in ['float3']: # Need to unpack list for these
                                    cmds.setAttr(attribute, *value)
                                elif type in ['byte']:
                                    try:
                                        cmds.setAttr(attribute, value)
                                    except Exception as e:
                                        print(e)
                                        print("value: " + value)
                                        
                                else:
                                    try:
                                        cmds.setAttr(attribute, value)
                                    except Exception as e:
                                        print(e)
                                        print("value: " + value)

    # Just printing out the attributes that were skipped
    if lockedAttributes.keys():
        # print(tab * 2 + '> Skipped' + tab + '(These attributes were skipped due to being connected)')
        logger.info('These attributes were skipped due to being connected or locked')
        for attribute, value in lockedAttributes.items():
            # pStr = tab * 3
            pStr = pStr + str(attribute)
            pStr = pStr + (space * (offset - len(str(attribute))))
            pStr = pStr + type
            pStr = pStr + (space * (12 - len(type)))
            pStr = pStr + str(value)

            print(pStr)
            logger.info(pStr)


def createVRaySun():
    import maya.mel as mel
    mel.eval('vrayCreateVRaySun')


def createVRayDomeLight():
    domeLight = cmds.shadingNode('VRayLightDomeShape', asLight=True)
    cmds.setAttr(domeLight.replace('Dome', 'DomeShape') + '.invisible', 1)
    return domeLight


def clearRenderLayers():
    import maya.app.renderSetup.model.renderSetup as renderSetup
    rs = renderSetup.instance()
    rs.clearAll()
    if not cmds.getAttr('defaultRenderLayer.renderable'):
        cmds.setAttr('defaultRenderLayer.renderable', 1)


def clearRenderElements():
    renderElements = cmds.ls(type='VRayRenderElement')
    for renderElement in renderElements:
        cmds.delete(renderElement)


def createCryptomatte(name, id_type=1, enabled=True, userAttribute=None, numLevels=6):
    '''
    Creates a vrayRE_cryptomatte render elmenet

    :param name: Name of cryptomatte
    :param id_type: 1 = name, 2 = material, 3 = userAttributes
    :param enabled: If AOV should be enabled or not
    :param userAttribute: The user attribute key
    :param numLevels: Amount of objects that can share a single pixel. Default is 6.
    :return:
    '''
    import maya.mel as mel
    crypto = mel.eval('vrayAddRenderElement cryptomatteChannel')
    crypto = cmds.rename('cryptomatte_' + name)
    if not enabled:
        cmds.setAttr(crypto + '.enabled', 0)
    cmds.setAttr(crypto + '.vray_name_cryptomatte', 'crypto_' + name, type='string')
    cmds.setAttr(crypto + '.vray_idtype_cryptomatte', id_type)
    if name == "SubName":
        cmds.setAttr("%s.vray_add_root_name_cryptomatte" % crypto, 0)
    if userAttribute:
        cmds.setAttr(crypto + '.vray_userattr_cryptomatte', userAttribute, type='string')
    cmds.setAttr(crypto + '.vray_numlevels_cryptomatte', numLevels)
    return crypto


def createCryptomatteScene():
    import Maya_Functions.file_util_functions as fileUtil
    # fileUtil.OpenFile(path) # Open Maya file
    clearRenderLayers() # Remove all render layers and make sure masterLayer is renderable in batch

    skyNodes = cmds.ls(type='VRaySky') # Get all VRaySky nodes
    sunNodes = cmds.ls(type='VRayGeoSun') # Get all VRaySun nodes

    for node in skyNodes:
        if cmds.referenceQuery(node, isNodeReferenced=True): # If node is referenced, import it
            ref = cmds.referenceQuery(node, filename=True)
            cmds.file(ref, importReference=True)
        cmds.delete(node)

    for node in sunNodes:
        parent = cmds.listRelatives(node, parent=True)[0] # We need to delete the transform node
        if cmds.referenceQuery(parent, isNodeReferenced=True): # If node is referenced, import it
            ref = cmds.referenceQuery(node, filename=True)
            cmds.file(ref, importReference=True)
        cmds.delete(node)

    createVRayDomeLight() # Creating a new clean dome light

    # Removing all AOVs from scene
    for aov in cmds.ls(type="VRayRenderElement"):
        cmds.delete(aov)
    # Running again, in case something didn't get deleted ??
    for aov_set in cmds.ls(type="VRayRenderElementSet"):
        cmds.delete(aov_set)

    # Get render settings from JSON preset and apply it
    renderPresetsFolder = CC.get_render_presets()
    presetFile = 'cryptomatteOptimization.json'
    presetPath = os.path.join(renderPresetsFolder, presetFile).replace(os.sep, '/')
    settings = fileUtil.loadJson(presetPath)

    # Set all render settings excepted connected attributes
    applyRenderSettings(settings, blacklist=['defaultResolution.width',
                                             'defaultResolution.height',
                                             'defaultRenderGlobals.postMel',
                                             'defaultRenderGlobals.postRenderLayerMel',
                                             'defaultRenderGlobals.postRenderMel',
                                             'defaultRenderGlobals.preFurRenderMel',
                                             'defaultRenderGlobals.preMel',
                                             'defaultRenderGlobals.preRenderLayerMel',
                                             'defaultRenderGlobals.preRenderMel',
                                             'vraySettings.preKeyframeMel',
                                             'vraySettings.rtImageReadyMel'])
    createCryptoAOV()

def createCryptoAOV():
    import cryptoAttributes as cryptoAttr

    # createCryptomatte(name='Name', id_type=0) # Creating object name cryptomatte #Seems we don't need this AOV
    createCryptomatte(name='Material', id_type=1)  # Creating material name cryptomatte
    createCryptomatte(name='NameHierarchy', id_type=2)  # Creating name with hierarchy cryptomatte
    createCryptomatte(name='SubName', id_type=6)  # Creating sub object name cryptomatte

    # Finding all vrayUserAttribute keys being used in the scene
    uniqueKeys = []
    vrayAttributes = cmds.ls("::*.vrayUserAttributes", long=True)
    logger.info('vrayAttributes: ' + str(vrayAttributes))
    for vrayAttribute in vrayAttributes:
        logger.info('vrayAttribute: ' + str(vrayAttribute))
        attributeDictionary = cryptoAttr.getUserAttributes(vrayAttribute.replace('.vrayUserAttributes', ''))
        logger.info('attributeDictionary: ' + str(attributeDictionary))
        for key in attributeDictionary.keys():
            logger.info('key: ' + str(key))
            if key not in uniqueKeys:
                logger.info('added to unique keys: ' + str(key))
                uniqueKeys.append(key)

    # Creates a cryptomatte render element for every unique key in scene
    logger.info('uniqueKeys: ' + str(uniqueKeys))
    for key in uniqueKeys:
        logger.info('key: ' + str(key))
        if not key == "Asset_name": #Skip asset name #Seems we don't need this AOV
            createCryptomatte(name=key.capitalize(), id_type=3, userAttribute=key)
    print("DONE !")
    # Done: Remove all AOVs
    # Scrapped: Add cryptomatte AOVs based off RenderSubmitter choice
    # Scrapped: Add Cryptomattes based off JSON file
    # Done: Add cryptomattes based on vrayUserAttributes present in scene
    # TODO: Submit cryptomatte to royal render (No EXR Crop)
    

def generateOIDandMID():
    """
    check scene for OID and MID attributes and collect the values
    build aovs of those values
    :return:
    """
    logger.info("Generating OIDs and MIDs AOV from scene content")
    oid_attributes = cmds.ls("::*.vrayObjectID", long=True)
    mid_attributes = cmds.ls("::*.vrayMaterialId", long=True)
    oid_values = []
    mid_values = []
    for oa in oid_attributes:
        cur_oa_val = cmds.getAttr(oa)
        if cur_oa_val >=1:
            oid_values.append(cur_oa_val)
        else:
            logger.error("Found OID of 0 on %s" % oa)
    for ma in mid_attributes:
        cur_ma_val = cmds.getAttr(ma)
        if cur_ma_val >=1:
            mid_values.append(cur_ma_val)
        else:
            logger.error("Found MID of 0 on %s" % ma)
    for ov in sorted(oid_values):
        mul = (ov - 1) / 3
        start = 1 + 3 * mul
        end = start + 2
        oid_name = "OID_%s_%s" % (str(start).zfill(2), str(end).zfill(2))
        if not cmds.objExists(oid_name):
            logger.info("building OID_%s_%s" % (start, end))
            buildMultiMatte(mm_name=oid_name,start=start)

    for mv in sorted(mid_values):
        mul = (mv - 1) / 3
        start = 1 + 3 * mul
        end = start + 2
        mid_name = "MID_%s_%s" % (str(start).zfill(2), str(end).zfill(2))
        if not cmds.objExists(mid_name):
            logger.info("building MID_%s_%s" % (str(start).zfill(2), str(end).zfill(2)))
            buildMultiMatte(mm_name=mid_name,start=start,mid=True)

    # print("%s : makes %s -%s." % (l,start,end))
    # oid_name = "OID_%s_%s" % (start, end)


def buildMultiMatte(mm_name,start,mid=False):
    import maya.mel as mel
    obj = mel.eval("vrayAddRenderElement %s" % "MultiMatteElement")
    cmds.setAttr("%s.vray_name_multimatte" % obj, mm_name, type="string")
    cmds.setAttr("%s.vray_redid_multimatte" % obj, start)
    cmds.setAttr("%s.vray_greenid_multimatte" % obj, start + 1)
    cmds.setAttr("%s.vray_blueid_multimatte" % obj, start + 2)
    cmds.setAttr("%s.vray_usematid_multimatte" % obj, mid)

    cmds.rename(obj, mm_name)
