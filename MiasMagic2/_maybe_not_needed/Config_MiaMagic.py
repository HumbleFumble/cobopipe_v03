### #The config file for the project:
project_paths = {"base_path":"P:/_WFH_Projekter/930450_MiasMagicComicBook/Production",
                 "asset_top_path":"<base_path>/Assets/3D_Assets",
                 "asset_base_path":"<asset_top_path>/<asset_type>/<asset_category>/<asset_name>",
                 "asset_work_folder":"<asset_base_path>/01_Work/Maya",
                 "asset_ref_folder":"<asset_base_path>/02_Ref",
                 "asset_texture_folder":"<asset_base_path>/03_Texture",
                 "asset_work_path": "<asset_work_folder>/<asset_name>_<asset_step>",
                 "update_log_path":"C:/Temp/Update_Log.txt", #Just a temp path used while updating old assets
                 "maya_env":"",
                 "film_path":"<base_path>/Film",
                 "episode_path":"<film_path>/<episode_name>",
                 "seq_path":"<episode_path>/<episode_name>_<seq_name>",
                 "shot_path":"<seq_path>/<episode_name>_<seq_name>_<shot_name>",
                 "shot_anim_path":"<shot_path>/01_Animation/<episode_name>_<seq_name>_<shot_name>_Animation.ma",
                 "shot_light_file":"<shot_path>/02_Light/<episode_name>_<seq_name>_<shot_name>_Light.ma",
                 "sequence_preview_folder":"<seq_path>/_Preview",
                 "shot_anim_preview_file":"<sequence_preview_folder>/<episode_name>_<seq_name>_<shot_name>.mov",
                 "shot_animatic_file":"<shot_path>/<episode_name>_<seq_name>_<shot_name>_Animatic.mov",
                 "shot_render_path":"<shot_path>/04_Publish/<episode_name>_<seq_name>_<shot_name>_<render_prefix>_Render.ma",
                 "shot_passes_folder":"<shot_path>/passes/<render_prefix>/<episode_name>_<seq_name>_<shot_name>_<render_prefix>_",
                 "shot_comp_folder":"<shot_path>/03_Comp/",
                 "shot_comp_output_folder":"<shot_path>/05_CompOutput",
                 "shot_comp_output_file":"<shot_comp_output_folder>/<episode_name>_<seq_name>_<shot_name>_0001.exr",
                 "shot_comp_preview_file":"<sequence_preview_folder>/<episode_name>_<seq_name>_<shot_name>_Comp.mov",
                 "shot_yeti_cache_path":"<shot_path>/04_Publish/YetiCache/",
                 "template_path":"<base_path>/Pipeline/Template",
                 "render_presets":"<base_path>/Pipeline/RenderSettings_Presets/",
                 "render_preset_config":"<base_path>/Pipeline/render_preset_config.json",
                 "OID_set_rules":"<base_path>/Pipeline/OID_set_rules.json",
                 "light_export_folder":"<base_path>/Assets/Light_Setups/Light_Export_Groups/",
                 "contact_sheet_category_file":"<base_path>/Pipeline/contact_sheet_category.json",
                 "module_path":""
                 }
project_name = "MiaMagic"

thumbnail_paths = {"asset_thumbnail_path":"<asset_base_path>/04_Design/Thumbnail/<asset_name>_thumbnail.png",
                   "folder_icon_path":"<base_path>/Pipeline/Resource/icon/folder.png",
                   "no_thumb_icon_path":"<base_path>/Pipeline/Resource/icon/No_Thumbnail.png",
                   "shot_animatic_thumbnail_path":"<shot_path>/Thumbnails/<episode_name>_<seq_name>_<shot_name>_animatic_thumbnail.jpg",
                   "shot_anim_thumbnail_path":"<shot_path>/Thumbnails/<episode_name>_<seq_name>_<shot_name>_anim_thumbnail.jpg",
                   "shot_render_thumbnail_path":"<shot_path>/Thumbnails/<episode_name>_<seq_name>_<shot_name>_render_thumbnail.jpg",
                   "shot_comp_thumbnail_path":"<shot_path>/Thumbnails/<episode_name>_<seq_name>_<shot_name>_comp_thumbnail.jpg",}

ref_steps = {"Prop":{"Base":["Anim","Render"]},
             "Char":{"Model":["Model"],"Blendshape":["Blendshape"],"Rig":["Anim","Rig"],"Shading":["Render"]},
             "Setdress":{"Base":["Render"]},
             "Set":{"Base":["Anim","Render"]}}

regex_strings = {"episode":"^(e)\d{2}","seq":"(_sq)\d{3}","shot":"(_sh)\d{3}"}

ref_order = {"Char":["Model", "Rig", "Shading"], "Set":["Base"],"Setdress":["Base"],"Prop":["Base"]} #Not used so far. Meant to establish a order to which file to publish first

ref_paths = {"Anim":"<asset_ref_folder>/<asset_name>_<asset_output>.mb",
             "Render":"<asset_ref_folder>/<asset_name>_<asset_output>.mb",
             "Model":"<asset_ref_folder>/<asset_name>_<asset_step>_Ref.mb",
             "Rig":"<asset_ref_folder>/<asset_name>_<asset_step>_Ref.mb",
             "Blendshape":"<asset_ref_folder>/<asset_name>_<asset_step>_Ref.mb",
             "GPU":"<asset_ref_folder>/<asset_name>_GPU.abc",
             "VrayProxy":"<asset_ref_folder>/<asset_name>_VrayProxy.vrmesh",
             "YetiGroom":"<asset_ref_folder>/YetiGroom/<asset_name>_<yeti_node>_Groom.grm",
             "YetiAlembicCache":"<asset_ref_folder>/YetiGroom/<asset_name>_<yeti_node>_AlembicCache.abc",
             "AnimScene":"<shot_path>/04_Publish/<episode_name>_<seq_name>_<shot_name>_AnimRef.mb"
             }

user_dict = {"Animation":["Camilla"],"Render":["Christian", "Ursula","Kaare","Amalie", "Jacob"]}
remove_list = {"model":{"SizeReferenceRN"},"set":{"SkyLight","CharacterReference"}}
publish_remove_set = "RemoveInPublish"
publish_set = "PublishSet"


"""
Example usage:
Use in scripts:
import ProjectConfig as cfg
base_path = cfg.project_paths["base_path"]
"""

#Not used yet: Maybe a structure so we can parse through and build up folders?
# asset_structure = {"Assets":{"asset_category":{"asset_type":{"asset_name"}}}}
# asset_types = {"Prop":"","Set":"", "Setdress":"", "Char":""}

### TESTING PURPOSE: ###
# asset_info = {"asset_type": "Prop", "asset_category": "Device", "asset_name": "Camera", "asset_step":"Base"}
# project_paths.update(asset_info)
# prop_path = "<asset_top_path>/<asset_type>/<asset_category>/<asset_name>/01_Work/Maya/<asset_name>_<asset_step>"
# prop_ref = "<asset_path>/<type>/<category>/<asset_name>/02_Ref/Maya/<asset_name>_<asset_step>_Ref.mb"

# def CreatePathFromDict(cur_string, path_dict):
#     if "<" in cur_string:
#         create_path = ""
#         for parts in cur_string.split("<"):  # Split up string in with start of VAR <
#             if ">" in parts:  # If start part skip
#                 cur_key = parts.split(">")[0]
#                 if cur_key in path_dict:
#                     cur_var = path_dict[cur_key]
#                     if not cur_var == "":
#                         cur_var = CreatePathFromDict(cur_var, path_dict)
#                     else:
#                         cur_var = "<%s>" % parts.split(">")[0]
#                     create_path = "%s%s%s" % (create_path, cur_var, parts.split(">")[1])
#                 else:
#                     create_path = "%s<%s" % (create_path, parts)
#             else:
#                 create_path = "%s%s" % (create_path, parts)
#         return create_path
#     else:
#         return cur_string





