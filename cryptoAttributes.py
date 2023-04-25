import maya.cmds as cmds
import maya.mel as mel
import file_util
import Maya_Functions.vray_util_functions as vrayUtil

from getConfig import getConfigClass
CC = getConfigClass()

from Log.CoboLoggers import getLogger
logger = getLogger()


def cryptoAttrCheck():
    logger.info('Running Crypotmatte Attribute Check')
    if CC.project_name in ['MiasMagic2']:
        if isShadingScene():
            logger.info('Cryptomatte Attribute Check: This is shading file')
            addAssetName(overwrite=True)
            addMatteID(overwrite=True)
            addOID(overwrite=True)
        elif isLightingScene():
            logger.info('Cryptomatte Attribute Check: This is lighting file')
            addSceneID(overwrite=True)
            addAssetName()
            addMatteID()
            addOID(overwrite=False)


def addMatteID(overwrite=False):
    object_ids = getCryptoTables()['OID']
    assets = getAssets()
    for asset in assets:
        if asset['asset_name'] in object_ids.keys():
            logger.info('Applying OID User Attribute')
            mel.eval('vray addAttributesFromGroup "' + asset['root'] + '" "vray_objectID" 1')
            userAttributes = getUserAttributes(asset['root'])
            logger.info('>>>>>> userAttributes: ' + str(userAttributes))
            if overwrite:
                cmds.setAttr(asset['root'] + '.vrayObjectID', object_ids[asset['asset_name']])
            if overwrite or 'OID' not in userAttributes.keys():
                addAttribute(asset['root'], 'OID', object_ids[asset['asset_name']])


def addAssetName(overwrite=False):
    logger.info('Applying Asset Name User Attribute')
    assets = getAssets()
    for asset in assets:
        if asset['asset_type'] in ['Char', 'Prop']:
            userAttributes = getUserAttributes(asset['root'])
            if overwrite or 'asset_name' not in userAttributes.keys():
                addAttribute(asset['root'], 'asset_name', asset['asset_name'])


def addSceneID(overwrite=False):
    logger.info('Applying Scene ID User Attribute')
    assets = getAssets()
    try:
        for asset in assets:
            if asset['asset_type'] in ['Char', 'Prop']:
                if asset['scene_id']:
                    userAttributes = getUserAttributes(asset['root'])
                    if overwrite or 'scene_id' not in userAttributes.keys():
                        addAttribute(asset['root'], 'scene_id', asset['scene_id'])
    except Exception as e:
        logger.info(e)


def addOID(overwrite=False):
    logger.info('Applying OID to Object ID Attribute')
    object_ids = getCryptoTables()['OID']
    assets = getAssets()
    try:
        for asset in assets:
            if asset['asset_type'] in ['Char', 'Prop', 'Setdress']:
                if asset['asset_name'] in object_ids.keys():
                    currentOID = getOID(asset['root'])
                    specifiedOID = object_ids[asset['asset_name']]
                    if overwrite or currentOID == 0:
                        cmds.setAttr(asset['root'] + '.vrayObjectID', specifiedOID)
    except Exception as e:
        logger.info(e)

def addAttribute(node, attribute, value):
    userAttributes = getUserAttributes(node)
    userAttributes[attribute] = str(value)
    userAttributesString = ''
    for userAttribute, value in userAttributes.items():
        userAttributesString = userAttributesString + userAttribute + '=' + str(value) + ';'
    if userAttributesString:
        userAttributesString = userAttributesString[:-1]
    cmds.setAttr(node + '.vrayUserAttributes', userAttributesString, type='string')


def removeAttribute(node, attribute):
    userAttributes = getUserAttributes(node)
    if attribute in userAttributes.keys():
        userAttributesString = ''
        for userAttribute, value in userAttributes.items():
            if not userAttribute == attribute:
                userAttributesString = userAttributesString + userAttribute + '=' + value + ';'
        if userAttributesString:
            userAttributesString = userAttributesString[:-1]
        cmds.setAttr(node + '.vrayUserAttributes', userAttributesString, type='string')



def getUserAttributes(node):
    if not cmds.attributeQuery('vrayUserAttributes', node=node, exists=True):
        vrayUtil.createVrayAttribute(node, 'vray_user_attributes')
    userAttributeString = cmds.getAttr(node + '.vrayUserAttributes')
    if userAttributeString:
        if userAttributeString.endswith(';'):
            userAttributeString = userAttributeString[:-1]
    userAttributes = {}
    if not userAttributeString == '':
        if userAttributeString:
            for declaration in userAttributeString.split(';'):
                if declaration:
                    userAttributes[declaration.split('=')[0]] = declaration.split('=')[1]
    return userAttributes


def getOID(node):
    if not cmds.attributeQuery('vrayObjectID', node=node, exists=True):
        vrayUtil.createVrayAttribute(node, 'vray_objectID')
    return cmds.getAttr(node + '.vrayObjectID')


def getAssets():
    assets = []
    nodes = cmds.ls(type='transform', long=True)
    for node in nodes:
        if node:
            name = node.split('|')[-1].split(':')[-1]
            if name == 'Root_Group':
                if cmds.attributeQuery('assetName', node=node, exists=True) or cmds.attributeQuery('asset_name', node=node, exists=True):
                    asset = {'root': node}
                    if cmds.attributeQuery('assetName', node=node, exists=True):
                        asset['asset_name'] = cmds.getAttr(node + '.assetName')
                    elif cmds.attributeQuery('asset_name', node=node, exists=True):
                        asset['asset_name'] = cmds.getAttr(node + '.asset_name')
                    if cmds.attributeQuery('assetCategory', node=node, exists=True):
                        asset['asset_category'] = cmds.getAttr(node + '.assetCategory')
                    elif cmds.attributeQuery('asset_category', node=node, exists=True):
                        asset['asset_category'] = cmds.getAttr(node + '.asset_category')
                    if cmds.attributeQuery('assetType', node=node, exists=True):
                        asset['asset_type'] = cmds.getAttr(node + '.assetType')
                    elif cmds.attributeQuery('asset_type', node=node, exists=True):
                        asset['asset_type'] = cmds.getAttr(node + '.asset_type')
                    try:
                        asset['scene_id'] = node.split('|')[-1].split(':')[-2]
                    except:
                        asset['scene_id'] = None
                    assets.append(asset)
    return assets


def getCryptoTables():
    cryptoTables = file_util.load_json(CC.get_cryptomatte_list())
    return cryptoTables


def saveCryptoTables(cryptoTables):
    file_util.save_json(CC.get_cryptomatte_list(), cryptoTables)
    return True


def isShadingScene():
    currentFile = cmds.file(query=True, list=True)[0]
    if CC.get_base_path() in currentFile:
        if CC.get_asset_top_path() in currentFile:
            dictionary = CC.util.ComparePartOfPath(currentFile, CC.get_asset_work_file())
            if dictionary['asset_step'] == 'Shading' and dictionary['asset_type'] == 'Char':
                return True
            elif dictionary['asset_step'] == 'Base' and dictionary['asset_type'] != 'Char':
                return True
    return False


def isLightingScene():
    currentFile = cmds.file(query=True, list=True)[0]
    if CC.get_film_path() in currentFile:
        if currentFile:
            if currentFile.endswith('_Light.ma'):
                return True
    return False