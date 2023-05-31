import os
import maya.cmds as cmds
import Maya_Functions.file_util_functions as fileUtil

IMAGER_TYPES = (
    "aiImagerLightMixer",
    "aiImagerColorCorrect",
    "aiImagerColorCurves",
    "aiImagerDenoiserNoice",
    "aiImagerDenoiserOidn",
    "aiImagerDenoiserOptix",
    "aiImagerExposure",
    "aiImagerLensEffects",
    "aiImagerTonemap",
    "aiImagerWhiteBalance",
)


def get_set_arnold_driver(set=False,driver_dict=None):
    if not set:
        driver_dict = {"halfPrecision":0,
                       "exrCompression":0,
                       "preserveLayerName":0,
                       "exrTiled":0,
                       "multipart":0,
                       "autocrop":0,
                       "append":0,
                       "mergeAOVs":0}
    for k in driver_dict:
        if set:
            cmds.setAttr("defaultArnoldDriver.%s" % k, driver_dict[k])
        else:
            driver_dict[k] = cmds.getAttr("defaultArnoldDriver.%s" % k)

    return driver_dict


def load_imager_preset(path):
    if not os.path.exists(path):
        return
    clear_imagers(IMAGER_TYPES)
    for index, imager in enumerate(fileUtil.loadJson(path)):
        build_imager(imager, index)


def save_imager_preset(path):
    fileUtil.saveJson(path, get_imager_data(IMAGER_TYPES))


def build_imager(imager, index):
    node_name = cmds.createNode(imager["type"], name=imager["name"])
    for key, data in imager["attributes"].items():
        attribute_name = f"{node_name}.{key}"
        if data["type"] in ["TdataCompound"]:
            continue
        #print(f"{data['type']:<10}{attribute_name:<55} {data['value']}")

        if data["value"] == None:
            continue
        elif data["type"] in ["string"]:
            cmds.setAttr(attribute_name, data["value"], type=data["type"])
        elif data["type"] in ["float3"]:
            cmds.setAttr(attribute_name, *data["value"][0], type=data["type"])
        else:
            cmds.setAttr(attribute_name, data["value"])
    cmds.connectAttr(
        f"{node_name}.message", f"defaultArnoldRenderOptions.imagers[{index}]"
    )


def get_imager_data(types=IMAGER_TYPES):
    imagers_output = []
    for imager in cmds.listConnections("defaultArnoldRenderOptions.imagers"):
        if not cmds.nodeType(imager) in IMAGER_TYPES:
            continue
        imager_dictionary = {
            "name": imager,
            "type": cmds.nodeType(imager),
            "attributes": {},
        }

        attribute_name_list = []
        for attribute in cmds.listAttr(imager):
            if (
                len(attribute.split(".")) == 1
            ):  # Removing double attributes like aiImagerLightMixer1.layerTint.layerTintR
                attribute_name = f"{imager}.{attribute}"
                multi_indices = cmds.getAttr(attribute_name, multiIndices=True)
                if not multi_indices:
                    attribute_name_list.append(attribute)
                else:
                    for index in multi_indices:
                        for sub_attribute in cmds.listAttr(
                            f"{attribute_name}[{index}]"
                        ):
                            attribute_name_list.append(sub_attribute)

        for attribute in attribute_name_list:
            attribute_name = f"{imager}.{attribute}"
            attribute_type = cmds.getAttr(attribute_name, type=True)
            if attribute_type == "message":
                continue  # message type attributes does not contain any value
            attribute_value = cmds.getAttr(attribute_name)
            imager_dictionary["attributes"][attribute] = {
                "type": attribute_type,
                "value": attribute_value,
            }

        imagers_output.append(imager_dictionary)
    return imagers_output


def clear_imagers(types=IMAGER_TYPES):
    cmds.delete(cmds.listConnections("defaultArnoldRenderOptions.imagers"))

def add_aovs_to_noice():
    aovs = cmds.ls(type='aiAOV')
    aov_list = []
    for aov in aovs:
        if 'denoise' in cmds.listAttr(aov):
            type = cmds.getAttr(f"{aov}.type")
            if 4 < type < 7:
                if not aov.startswith('aiAOV_crypto_'):
                    cmds.setAttr(f"{aov}.denoise", True)
                    aov_list.append(aov)
            else:
                cmds.setAttr(f"{aov}.denoise", False)

    layerSelection_string = ""
    for i, aov in enumerate(aov_list):
        if i>0:
            layerSelection_string = f"{layerSelection_string} or {aov.replace('aiAOV_', '')}"
        else:
            layerSelection_string = aov.replace('aiAOV_', '')


    noice_nodes = cmds.ls(type="aiImagerDenoiserNoice")
    for node in noice_nodes:
        cmds.setAttr(node + ".layerSelection", layerSelection_string, type='string')
def import_aov_shaders(folder_path="P:/930435_Liva_og_De_Uperfekte/Teaser/Pipeline/RenderSettings_Presets/AOV_Shaders/"):
    aov_list = ["ao", "uv", "falloff", "crypto_object","crypto_material","crypto_asset"]
    for aov_name in aov_list:
        aov = cmds.ls("aiAOV_%s" % aov_name, type="aiAOV")
        if aov:
            shader_name = "aov_%s_Shader" % aov_name
            if "crypto" in aov_name:
                shader_name = "_aov_cryptomatte"
                aov_name = "cryptomatte"
            aov_shader = cmds.ls(shader_name)


            if not cmds.listConnections("%s.defaultValue" % aov[0]):

                if not aov_shader:

                    i_file = cmds.file("%s%s.ma" % (folder_path, aov_name), i=True, ignoreVersion=True,
                                       ra=False, mergeNamespacesOnClash=True, options="v=0;")
                    aov_shader = cmds.ls(shader_name)

                cmds.connectAttr("%s.outColor" % aov_shader[0], "%s.defaultValue" % aov[0], f=True)



# save_imager_preset("C:/Users/mha/Desktop/imager_test.json")
# load_imager_preset("C:/Users/mha/Desktop/imager_test.json")