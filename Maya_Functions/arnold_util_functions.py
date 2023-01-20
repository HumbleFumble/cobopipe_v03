import os
import maya.cmds as cmds
import Maya_Functions.file_util_functions as fileUtil

IMAGER_TYPES = ('aiImagerLightMixer', 'aiImagerColorCorrect', 'aiImagerColorCurves',
                'aiImagerDenoiserNoice', 'aiImagerDenoiserOidn', 'aiImagerDenoiserOptix',
                'aiImagerExposure', 'aiImagerLensEffects', 'aiImagerTonemap', 'aiImagerWhiteBalance')

def load_imager_preset(path):
    if not os.path.exists(path): return
    clear_imagers(IMAGER_TYPES)
    for index, imager in enumerate(fileUtil.loadJson(path)):
        build_imager(imager, index)

def save_imager_preset(path):
    fileUtil.saveJson(path, get_imager_data(IMAGER_TYPES))

def build_imager(imager, index):
    node_name = cmds.createNode(imager['type'], name=imager['name'])
    for key, data in imager['attributes'].items():
        attribute_name = f"{node_name}.{key}"
        if data['type'] in ['TdataCompound']: continue
        print(f"{data['type']:<10}{attribute_name:<55} {data['value']}")
        
        if data['value'] == None: continue
        elif data['type'] in ['string']:
            cmds.setAttr(attribute_name, data['value'], type=data['type'])
        elif data['type'] in ['float3']:
            cmds.setAttr(attribute_name, *data['value'][0], type=data['type'])
        else:
            cmds.setAttr(attribute_name, data['value'])
    cmds.connectAttr(f"{node_name}.message", f"defaultArnoldRenderOptions.imagers[{index}]")

def get_imager_data(types=IMAGER_TYPES):
    imagers_output = []
    for imager in cmds.listConnections('defaultArnoldRenderOptions.imagers'):
        if not cmds.nodeType(imager) in IMAGER_TYPES: print('\n\nFUUUUUUUUUUUUUUUUUUUUUUUCK\n\n')
        imager_dictionary = {'name': imager,
                            'type': cmds.nodeType(imager),
                            'attributes': {}}

        attribute_name_list = []
        for attribute in cmds.listAttr(imager):
            if len(attribute.split('.')) == 1: # Removing double attributes like aiImagerLightMixer1.layerTint.layerTintR
                attribute_name = f"{imager}.{attribute}"
                multi_indices = cmds.getAttr(attribute_name, multiIndices=True)
                if not multi_indices: 
                    attribute_name_list.append(attribute)
                else:
                    for index in multi_indices:
                        for sub_attribute in cmds.listAttr(f"{attribute_name}[{index}]"):
                            attribute_name_list.append(sub_attribute)
                            
        for attribute in attribute_name_list:
            attribute_name = f"{imager}.{attribute}"
            attribute_type = cmds.getAttr(attribute_name, type=True)
            if attribute_type == 'message': continue # message type attributes does not contain any value
            attribute_value = cmds.getAttr(attribute_name)
            imager_dictionary['attributes'][attribute] = {'type':   attribute_type,
                                                          'value':  attribute_value}
            
        imagers_output.append(imager_dictionary)
    return imagers_output

def clear_imagers(types=IMAGER_TYPES):
    cmds.delete(cmds.listConnections('defaultArnoldRenderOptions.imagers'))

#save_imager_preset("C:/Users/mha/Desktop/imager_test.json")
#load_imager_preset("C:/Users/mha/Desktop/imager_test.json")