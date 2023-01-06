
"""
Transfer assets

Update Asset browser with use of CC class instead of cfg_util
Update Asset browser so it finds nodes and pixmaps faster.
Add project name to env
"""


# optional, could be bringing in the base_path aswell in the orig dict
# old_base = CC.util.GetBasePath(test_path,CC.asset_top_path)
# if old_base:
#     test_dict["base_path"] = CC.get_base_path()
# remove_list = [(old_base,CC.get_base_path())]
# new_path = test_path
# for to_remove in remove_list:
#     new_path = new_path.replace(to_remove[0],to_remove[1])
# print(new_path)
# new_path = test_path
# build_path = ""
# for_assets_split = CC.asset_top_path.split(">")[-1]
# cur_parts = new_path.split(for_assets_split)
# build_path = "%s%s" % (cur_parts[0],for_assets_split)
# next = CC.asset_base_path.split("<asset_top>")[-1]
# next_parts = next.split("/")
# for n in new_path:
#     pass
# print(build_path)

# second_split = CC.asset_base_path
# splitter_list = [first_split,]
#
# print(test_path.split(first_split))

# print(CC.util.ComparePartOfPath(test_path,CC.get_asset_base_path()))

def changeByAssetKeys():
    footage_path = "P:/930382_KiwiStrit2/Production/Film/E08/E08_SQ010/E08_SQ010_SH050/02_Light/E08_SQ010_SH050_Light.ma"
    test_dict = {"shot_name": "SH020", "episode_name": "E02", "seq_name": "SQ030"}

    asset_path = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/SetDress/Grounds/MushroomA/02_Ref/MushroomA_Model_Ref.mb"
    from Configs.ConfigClass_MiasMagic2TestEnv import ConfigClass
    CC = ConfigClass()
    test_dict = {"asset_type":"RigModule","asset_category":"Eye","asset_name":"EyeC","asset_output":"Rig"}
    # result = replacePathByKeys(scene_path=footage_path,compare_path=CC.old.get_shot_light_file(),replace_dict=test_dict,replace=True)
    result = replacePathByKeys(scene_path=asset_path, compare_path=CC.old.get_Model(),
                               replace_dict=test_dict, replace=True)
    print(result)

    # test_path = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/Char/Module/EyeA/01_Work/Maya/EyeA_Shading"
    # test_dict = {"asset_type":"RigModule", "asset_category":"Eyes","asset_name":"EyesA"}
    # from Configs.ConfigClass_MiasMagic2TestEnv import ConfigClass
    # CC = ConfigClass()
    # print(CC.util.CreateDictFromAssetPath(test_path,CC.old.util.base_config))
    #
    # result = replacePathByKeys(scene_path=test_path,compare_path=CC.old.get_asset_base_path(),replace_dict=test_dict,replace=True)
    # print(result)



def replacePathByKeys(scene_path, compare_path,replace_dict={},replace=True): #Used for splitting a scene path up, and getting asset info from there. NOT WELL DONE :/
    """
    this is meant to take a file/folder path, a config-path to compare and find keys from, and a dict with asset-info,
    and then try to return a path where the keys related to the config string has been replace in the actual string.
    :return:
    """
    if not len(scene_path.split("/")) == len(compare_path.split("/")):  # check if the two paths are able to be compared
        print("Warning: Not equal paths. Errors can occur.\nComparing: %s and %s " % (scene_path, compare_path))
        # return False
    scene_path_dict = {} #this is where we place the asset keys we find in the scene path.
    if "." in scene_path:  # remove the extension
        scene_path = scene_path.split(".")[0]
    if "." in compare_path:
        compare_path = compare_path.split(".")[0]
    else: #compare_path.endswith("/"):
        compare_path = compare_path + "/"

    build_path = "" #the string we turn into our new path, by replacing keys from dict.
    """
    go through compare_path and split it up by keys (<>) and then remove the part before the keys from
    the scene path, so scene path is always just the "unworked" end of the string
    """
    if "<" in compare_path:
        for parts in compare_path.split("<"):
            if not parts == "":
                if ">" in parts: #check if the first part of the path is
                    parts_split = parts.split(">")
                    cur_key = parts_split[0]
                    after = parts_split[1]
                    print("SCENE:PATH %s" % scene_path)
                    if not after == "":
                        # print("ComparePartOfPath","From %s: %s : %s" % (scene_path,cur_key, scene_path.split(after)[0]))
                        cur_value = scene_path.split(after)[0]
                        print("Cur Value: %s" % cur_value)
                        print("Cur Key: %s" % cur_key)
                        if cur_key in scene_path_dict.keys():
                            print("Already found: %s" % cur_key)
                            if not scene_path_dict[cur_key] == cur_value:
                                print("ERROR same key with different values: key:%s Values %s->%s" %(cur_key,scene_path_dict[cur_key],cur_value))
                        scene_path_dict[cur_key] = cur_value

                        if cur_key in replace_dict.keys():
                            build_path = build_path + replace_dict[cur_key] + after
                        else:
                            build_path = build_path + cur_value
                        scene_path = after.join(scene_path.split(after)[1:])
                    else:
                        print("AFTER: %s" % scene_path)
                        cur_value = scene_path
                        scene_path_dict[cur_key] = cur_value
                        build_path = build_path + scene_path
                else:
                    #The first part of the path, base path and so on.
                    # print("path: %s - parts: %s" % (scene_path,parts))
                    # print(scene_path.split(parts))
                    print(parts)
                    print(scene_path)
                    build_path = build_path + parts

                    scene_path = scene_path.split(parts)[1]
    if scene_path:
        if replace: #Try to replace by keys from info-dict and replace-dict:
            print("Trying to replace in %s with keys from %s" % (scene_path,replace_dict))
            for r_key in scene_path_dict.keys():
                if r_key in replace_dict.keys():
                    scene_path = scene_path.replace(scene_path_dict[r_key], replace_dict[r_key])
        build_path = build_path + scene_path
    return build_path,scene_path_dict

# def CreateNewAsset()

def RunCmd(cmd=""):
    pass


def PublishAssetTesting():
    import getConfig
    CC = getConfig.getConfigClass("KiwiStrit3")
    from PublishAssets import PublishMaster
    asset_dict = {'asset_name': 'StickySnail', 'asset_type': "Char", 'asset_category': 'Secondary',
                  'asset_step': 'Shading'}
    pc = PublishMaster.ReadyPublish(asset_info=asset_dict, lock_geo=True)
    result = pc.StartPublishInMayaPy()
    for r_print in result:
        print("NOW PRINTING RESULT")
        print(r_print)

if __name__ == "__main__":
  changeByAssetKeys()
