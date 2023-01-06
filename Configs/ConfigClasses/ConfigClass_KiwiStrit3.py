
from Log.CoboLoggers import getLogger
logger = getLogger()
class ConfigClass():
    def __init__(self):
        self.project_name="KiwiStrit3"
        self.base_path="P:/930383_KiwiStrit3/Production"
        self.asset_top_path="<base_path>/Assets/3D_Assets"
        self.asset_base_path="<asset_top_path>/<asset_type>/<asset_category>/<asset_name>"
        self.asset_work_folder="<asset_base_path>/01_Work/Maya"
        self.asset_ref_folder="<asset_base_path>/02_Ref"
        self.asset_design_folder="<asset_base_path>/04_Design"
        self.asset_work_file="<asset_work_folder>/<asset_name>_<asset_step>.ma"
        self.update_log_path="C:/Temp/Update_Log.txt"
        self.maya_env=""
        self.film_path="<base_path>/Film"
        self.episode_path="<film_path>/<episode_name>"
        self.seq_path="<episode_path>/<episode_name>_<seq_name>"
        self.shot_path="<seq_path>/<episode_name>_<seq_name>_<shot_name>"
        self.shot_anim_path="<shot_path>/01_Animation/<episode_name>_<seq_name>_<shot_name>_Animation.ma"
        self.shot_light_file="<shot_path>/02_Light/<episode_name>_<seq_name>_<shot_name>_Light.ma"
        self.sequence_preview_folder="<seq_path>/_Preview"
        self.sequence_previs_file="<seq_path>/<episode_name>_<seq_name>_PREVIS/01_Maya/<episode_name>_<seq_name>_PREVIS.ma"
        self.shot_anim_preview_file="<sequence_preview_folder>/<episode_name>_<seq_name>_<shot_name>.mov"
        self.shot_animatic_file="<shot_path>/<episode_name>_<seq_name>_<shot_name>_Animatic.mov"
        self.shot_render_path="<shot_path>/04_Publish/<episode_name>_<seq_name>_<shot_name>_<render_prefix>_Render.ma"
        self.shot_crypto_render_file="<shot_path>/04_Publish/<episode_name>_<seq_name>_<shot_name>_<render_prefix>_Crypto_Render.ma"
        self.shot_passes_folder="<shot_path>/passes/<render_prefix>/<episode_name>_<seq_name>_<shot_name>_<render_prefix>"
        self.shot_comp_folder="<shot_path>/03_Comp/"
        self.shot_ae_precomp_file="<shot_comp_folder>/<episode_name>_<seq_name>_<shot_name>_Precomp.aep"
        self.shot_comp_output_folder="<shot_path>/05_CompOutput"
        self.shot_comp_output_file="<shot_comp_output_folder>/<episode_name>_<seq_name>_<shot_name>_0001.exr"
        self.shot_comp_preview_file="<sequence_preview_folder>/<episode_name>_<seq_name>_<shot_name>_Comp.mov"
        self.shot_yeti_cache_path="<shot_path>/04_Publish/YetiCache/"
        self.template_path="<base_path>/Pipeline/Template"
        self.template_asset_path="<template_path>/<asset_type>_Template_Folder/"
        self.tb_scene_template_file="<base_path>/Pipeline/Template/_TBSceneTemplate/BaseFile/BaseFile.xstage"
        self.ae_precomp_template_file="<base_path>/Pipeline/Template/_AECompTemplate/ae_precomp_template.aep"
        self.render_presets="<base_path>/Pipeline/RenderSettings_Presets/"
        self.render_preset_config="<base_path>/Pipeline/render_preset_config.json"
        self.OID_set_rules="<base_path>/Pipeline/OID_set_rules.json"
        self.light_export_folder="<base_path>/Assets/Light_Setups/LightHelper_Export/"
        self.contact_sheet_category_file="<base_path>/Pipeline/contact_sheet_category.json"
        self.module_path=""
        self.shared_files_path="<base_path>/SharedFiles/"
        self.python_path="T:/_Pipeline/cobopipe_v01-001/"
        self.OCIO="<base_path>/Pipeline/ACES/config.ocio"
        self.project_shelf_json="<base_path>/Pipeline/Maya_Shelves/build_shelf_dict.json"
        self.publish_report_folder="<base_path>/Pipeline/PublishReports"
        self.asset_publish_path="<publish_report_folder>/Assets"
        self.shot_publish_path="<publish_report_folder>/Film"
        self.asset_publish_report_file="<asset_publish_path>/<asset_type>/<asset_category>/<asset_name>.json"
        self.shot_publish_report_file="<shot_publish_path>/<episode_name>/<episode_name>_<seq_name>/<episode_name>_<seq_name>_<shot_name>.json"
        self.episode_info_file="<episode_path>/<episode_name>_BrowserInfo.json"
        
        self.Anim="<asset_ref_folder>/<asset_name>_Anim.mb"
        self.Render="<asset_ref_folder>/<asset_name>_Render.mb"
        self.Model="<asset_ref_folder>/<asset_name>_Model_Ref.mb"
        self.Rig="<asset_ref_folder>/<asset_name>_Rig_Ref.mb"
        self.Blendshape="<asset_ref_folder>/<asset_name>_<asset_step>_Ref.mb"
        self.GPU="<asset_ref_folder>/<asset_name>_GPU.abc"
        self.VrayProxy="<asset_ref_folder>/<asset_name>_VrayProxy.vrmesh"
        self.YetiGroom="<asset_ref_folder>/YetiGroom/<asset_name>_<yeti_node>_Groom.grm"
        self.YetiAlembicCache="<asset_ref_folder>/YetiGroom/<asset_name>_<yeti_node>_AlembicCache.abc"
        self.AnimScene="<shot_path>/04_Publish/<episode_name>_<seq_name>_<shot_name>_AnimRef.mb"
        
        self.episode_regex="^(e)\d{2}"
        self.seq_regex="(_sq)\d{3}"
        self.shot_regex="(_sh)\d{3}"
        
        self.environment_vars={'PYTHONPATH': '<python_path>', 'TOONBOOM_GLOBAL_SCRIPT_LOCATION': '<python_path>/ToonBoom/ToonBoom_Global_Scripts', 'BOM_USER': ''}
        
        self.local_vars=['TOONBOOM_GLOBAL_SCRIPT_LOCATION', 'PYTHONPATH']
        
        self.users={'Animation': ['Anne', 'Edgars', 'Jamie', 'Julie', 'Marco', 'Natasha', 'Ripu', 'Tamara', 'Thomas', 'Tue'], 'Render': ['Alexandra', 'Christian', 'Johanna', 'Kaare', 'Mads', 'Sara']}
        
        self.ref_order={'Char': ['Model', 'Rig', 'Shading'], 'Set': ['Base'], 'Setdress': ['Base'], 'Prop': ['Base'], 'RigModule': ['Base']}
        
        self.ref_steps={'Prop': {'Base': ['Anim', 'Render']}, 'Char': {'Model': ['Model'], 'Blendshape': ['Blendshape'], 'Rig': ['Anim', 'Rig'], 'Shading': ['Render']}, 'Setdress': {'Base': ['Render']}, 'Set': {'Base': ['Anim', 'Render']}, 'RigModule': {'Base': ['Rig']}}
        
        self.project_settings={'fps': '25fps', 'colorManagementEnabledByDefault': 1}
        
        self.project_style={'animation_style': ['Maya', 'Toonboom'], 'comp_style': ['Fusion', 'AE'], 'default_animation_style': 'Maya', 'default_comp_style': 'Fusion'}
        
        
        import getConfig
        self.old = None
        self.util = getConfig.getJsonConfigUtil("KiwiStrit3")


    def getByKey_ref_paths(self,call_key=None,**kwords):
        
        if call_key == 'Anim':
            return self.get_Anim(**kwords)
        if call_key == 'AnimScene':
            return self.get_AnimScene(**kwords)
        if call_key == 'Blendshape':
            return self.get_Blendshape(**kwords)
        if call_key == 'GPU':
            return self.get_GPU(**kwords)
        if call_key == 'Model':
            return self.get_Model(**kwords)
        if call_key == 'Render':
            return self.get_Render(**kwords)
        if call_key == 'Rig':
            return self.get_Rig(**kwords)
        if call_key == 'VrayProxy':
            return self.get_VrayProxy(**kwords)
        if call_key == 'YetiAlembicCache':
            return self.get_YetiAlembicCache(**kwords)
        if call_key == 'YetiGroom':
            return self.get_YetiGroom(**kwords)
        logger.debug("No such key found! This function only takes: ['Anim', 'Render', 'Model', 'Rig', 'Blendshape', 'GPU', 'VrayProxy', 'YetiGroom', 'YetiAlembicCache', 'AnimScene']")
        return False
        
    def getByKey_thumbnail_paths(self,call_key=None,**kwords):
        
        if call_key == 'asset_thumbnail_path':
            return self.get_asset_thumbnail_path(**kwords)
        if call_key == 'folder_icon_path':
            return self.get_folder_icon_path(**kwords)
        if call_key == 'no_thumb_icon_path':
            return self.get_no_thumb_icon_path(**kwords)
        if call_key == 'shot_anim_thumbnail_path':
            return self.get_shot_anim_thumbnail_path(**kwords)
        if call_key == 'shot_animatic_thumbnail_path':
            return self.get_shot_animatic_thumbnail_path(**kwords)
        if call_key == 'shot_comp_thumbnail_path':
            return self.get_shot_comp_thumbnail_path(**kwords)
        if call_key == 'shot_render_thumbnail_path':
            return self.get_shot_render_thumbnail_path(**kwords)
        logger.debug("No such key found! This function only takes: ['asset_thumbnail_path', 'folder_icon_path', 'no_thumb_icon_path', 'shot_animatic_thumbnail_path', 'shot_anim_thumbnail_path', 'shot_render_thumbnail_path', 'shot_comp_thumbnail_path']")
        return False
        

    def get_OCIO(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/ACES/config.ocio"
        return to_return


    def get_OID_set_rules(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/OID_set_rules.json"
        return to_return


    def get_ae_precomp_template_file(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/Template/_AECompTemplate/ae_precomp_template.aep"
        return to_return


    def get_asset_base_path(self,asset_type=None,asset_category=None,asset_name=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to asset_base_path: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to asset_base_path: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to asset_base_path: Argument Missing: asset_name")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_asset_design_folder(self,asset_type=None,asset_category=None,asset_name=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to asset_design_folder: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to asset_design_folder: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to asset_design_folder: Argument Missing: asset_name")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/04_Design".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_asset_publish_path(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/PublishReports/Assets"
        return to_return


    def get_asset_publish_report_file(self,asset_type=None,asset_category=None,asset_name=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to asset_publish_report_file: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to asset_publish_report_file: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to asset_publish_report_file: Argument Missing: asset_name")

        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/PublishReports/Assets/{asset_type}/{asset_category}/{asset_name}.json".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_asset_ref_folder(self,asset_type=None,asset_category=None,asset_name=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to asset_ref_folder: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to asset_ref_folder: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to asset_ref_folder: Argument Missing: asset_name")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_asset_top_path(self):
        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets"
        return to_return


    def get_asset_work_file(self,asset_type=None,asset_category=None,asset_name=None,asset_step=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to asset_work_file: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to asset_work_file: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to asset_work_file: Argument Missing: asset_name")
        if asset_step==None:
            asset_step="<asset_step>"
            logger.debug("Building path to asset_work_file: Argument Missing: asset_step")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/01_Work/Maya/{asset_name}_{asset_step}.ma".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,asset_step=asset_step,)
        return to_return


    def get_asset_work_folder(self,asset_type=None,asset_category=None,asset_name=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to asset_work_folder: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to asset_work_folder: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to asset_work_folder: Argument Missing: asset_name")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/01_Work/Maya".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_base_path(self):
        to_return = "P:/930383_KiwiStrit3/Production"
        return to_return


    def get_contact_sheet_category_file(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/contact_sheet_category.json"
        return to_return


    def get_episode_info_file(self,episode_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to episode_info_file: Argument Missing: episode_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_BrowserInfo.json".format(episode_name=episode_name,)
        return to_return


    def get_episode_path(self,episode_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to episode_path: Argument Missing: episode_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}".format(episode_name=episode_name,)
        return to_return


    def get_film_path(self):
        to_return = "P:/930383_KiwiStrit3/Production/Film"
        return to_return


    def get_light_export_folder(self):
        to_return = "P:/930383_KiwiStrit3/Production/Assets/Light_Setups/LightHelper_Export/"
        return to_return


    def get_maya_env(self):
        to_return = ""
        return to_return


    def get_module_path(self):
        to_return = ""
        return to_return


    def get_project_shelf_json(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/Maya_Shelves/build_shelf_dict.json"
        return to_return


    def get_publish_report_folder(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/PublishReports"
        return to_return


    def get_python_path(self):
        to_return = "T:/_Pipeline/cobopipe_v01-001/"
        return to_return


    def get_render_preset_config(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/render_preset_config.json"
        return to_return


    def get_render_presets(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/RenderSettings_Presets/"
        return to_return


    def get_seq_path(self,episode_name=None,seq_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to seq_path: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to seq_path: Argument Missing: seq_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}".format(episode_name=episode_name,seq_name=seq_name,)
        return to_return


    def get_sequence_preview_folder(self,episode_name=None,seq_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to sequence_preview_folder: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to sequence_preview_folder: Argument Missing: seq_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/_Preview".format(episode_name=episode_name,seq_name=seq_name,)
        return to_return


    def get_sequence_previs_file(self,episode_name=None,seq_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to sequence_previs_file: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to sequence_previs_file: Argument Missing: seq_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_PREVIS/01_Maya/{episode_name}_{seq_name}_PREVIS.ma".format(episode_name=episode_name,seq_name=seq_name,)
        return to_return


    def get_shared_files_path(self):
        to_return = "P:/930383_KiwiStrit3/Production/SharedFiles/"
        return to_return


    def get_shot_ae_precomp_file(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_ae_precomp_file: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_ae_precomp_file: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_ae_precomp_file: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/03_Comp//{episode_name}_{seq_name}_{shot_name}_Precomp.aep".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_anim_path(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_anim_path: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_anim_path: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_anim_path: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/01_Animation/{episode_name}_{seq_name}_{shot_name}_Animation.ma".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_anim_preview_file(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_anim_preview_file: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_anim_preview_file: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_anim_preview_file: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/_Preview/{episode_name}_{seq_name}_{shot_name}.mov".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_animatic_file(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_animatic_file: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_animatic_file: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_animatic_file: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/{episode_name}_{seq_name}_{shot_name}_Animatic.mov".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_comp_folder(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_comp_folder: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_comp_folder: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_comp_folder: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/03_Comp/".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_comp_output_file(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_comp_output_file: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_comp_output_file: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_comp_output_file: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/05_CompOutput/{episode_name}_{seq_name}_{shot_name}_0001.exr".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_comp_output_folder(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_comp_output_folder: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_comp_output_folder: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_comp_output_folder: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/05_CompOutput".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_comp_preview_file(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_comp_preview_file: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_comp_preview_file: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_comp_preview_file: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/_Preview/{episode_name}_{seq_name}_{shot_name}_Comp.mov".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_crypto_render_file(self,episode_name=None,seq_name=None,shot_name=None,render_prefix=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_crypto_render_file: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_crypto_render_file: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_crypto_render_file: Argument Missing: shot_name")
        if render_prefix==None:
            render_prefix="<render_prefix>"
            logger.debug("Building path to shot_crypto_render_file: Argument Missing: render_prefix")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/04_Publish/{episode_name}_{seq_name}_{shot_name}_{render_prefix}_Crypto_Render.ma".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,render_prefix=render_prefix,)
        return to_return


    def get_shot_light_file(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_light_file: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_light_file: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_light_file: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/02_Light/{episode_name}_{seq_name}_{shot_name}_Light.ma".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_passes_folder(self,episode_name=None,seq_name=None,shot_name=None,render_prefix=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_passes_folder: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_passes_folder: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_passes_folder: Argument Missing: shot_name")
        if render_prefix==None:
            render_prefix="<render_prefix>"
            logger.debug("Building path to shot_passes_folder: Argument Missing: render_prefix")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/passes/{render_prefix}/{episode_name}_{seq_name}_{shot_name}_{render_prefix}".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,render_prefix=render_prefix,)
        return to_return


    def get_shot_path(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_path: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_path: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_path: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_publish_path(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/PublishReports/Film"
        return to_return


    def get_shot_publish_report_file(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_publish_report_file: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_publish_report_file: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_publish_report_file: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/PublishReports/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}.json".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_render_path(self,episode_name=None,seq_name=None,shot_name=None,render_prefix=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_render_path: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_render_path: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_render_path: Argument Missing: shot_name")
        if render_prefix==None:
            render_prefix="<render_prefix>"
            logger.debug("Building path to shot_render_path: Argument Missing: render_prefix")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/04_Publish/{episode_name}_{seq_name}_{shot_name}_{render_prefix}_Render.ma".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,render_prefix=render_prefix,)
        return to_return


    def get_shot_yeti_cache_path(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_yeti_cache_path: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_yeti_cache_path: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_yeti_cache_path: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/04_Publish/YetiCache/".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_tb_scene_template_file(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/Template/_TBSceneTemplate/BaseFile/BaseFile.xstage"
        return to_return


    def get_template_asset_path(self,asset_type=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to template_asset_path: Argument Missing: asset_type")

        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/Template/{asset_type}_Template_Folder/".format(asset_type=asset_type,)
        return to_return


    def get_template_path(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/Template"
        return to_return


    def get_update_log_path(self):
        to_return = "C:/Temp/Update_Log.txt"
        return to_return


    def get_Anim(self,asset_type=None,asset_category=None,asset_name=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to Anim: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to Anim: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to Anim: Argument Missing: asset_name")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_Anim.mb".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_AnimScene(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to AnimScene: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to AnimScene: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to AnimScene: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/04_Publish/{episode_name}_{seq_name}_{shot_name}_AnimRef.mb".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_Blendshape(self,asset_type=None,asset_category=None,asset_name=None,asset_step=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to Blendshape: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to Blendshape: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to Blendshape: Argument Missing: asset_name")
        if asset_step==None:
            asset_step="<asset_step>"
            logger.debug("Building path to Blendshape: Argument Missing: asset_step")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_{asset_step}_Ref.mb".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,asset_step=asset_step,)
        return to_return


    def get_GPU(self,asset_type=None,asset_category=None,asset_name=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to GPU: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to GPU: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to GPU: Argument Missing: asset_name")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_GPU.abc".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_Model(self,asset_type=None,asset_category=None,asset_name=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to Model: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to Model: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to Model: Argument Missing: asset_name")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_Model_Ref.mb".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_Render(self,asset_type=None,asset_category=None,asset_name=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to Render: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to Render: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to Render: Argument Missing: asset_name")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_Render.mb".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_Rig(self,asset_type=None,asset_category=None,asset_name=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to Rig: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to Rig: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to Rig: Argument Missing: asset_name")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_Rig_Ref.mb".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_VrayProxy(self,asset_type=None,asset_category=None,asset_name=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to VrayProxy: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to VrayProxy: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to VrayProxy: Argument Missing: asset_name")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_VrayProxy.vrmesh".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_YetiAlembicCache(self,asset_type=None,asset_category=None,asset_name=None,yeti_node=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to YetiAlembicCache: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to YetiAlembicCache: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to YetiAlembicCache: Argument Missing: asset_name")
        if yeti_node==None:
            yeti_node="<yeti_node>"
            logger.debug("Building path to YetiAlembicCache: Argument Missing: yeti_node")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/YetiGroom/{asset_name}_{yeti_node}_AlembicCache.abc".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,yeti_node=yeti_node,)
        return to_return


    def get_YetiGroom(self,asset_type=None,asset_category=None,asset_name=None,yeti_node=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to YetiGroom: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to YetiGroom: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to YetiGroom: Argument Missing: asset_name")
        if yeti_node==None:
            yeti_node="<yeti_node>"
            logger.debug("Building path to YetiGroom: Argument Missing: yeti_node")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/YetiGroom/{asset_name}_{yeti_node}_Groom.grm".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,yeti_node=yeti_node,)
        return to_return


    def get_asset_thumbnail_path(self,asset_type=None,asset_category=None,asset_name=None,**kwargs):
        if asset_type==None:
            asset_type="<asset_type>"
            logger.debug("Building path to asset_thumbnail_path: Argument Missing: asset_type")
        if asset_category==None:
            asset_category="<asset_category>"
            logger.debug("Building path to asset_thumbnail_path: Argument Missing: asset_category")
        if asset_name==None:
            asset_name="<asset_name>"
            logger.debug("Building path to asset_thumbnail_path: Argument Missing: asset_name")

        to_return = "P:/930383_KiwiStrit3/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/04_Design/Thumbnail/{asset_name}_thumbnail.png".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_folder_icon_path(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/Resource/icon/folder.png"
        return to_return


    def get_no_thumb_icon_path(self):
        to_return = "P:/930383_KiwiStrit3/Production/Pipeline/Resource/icon/No_Thumbnail.png"
        return to_return


    def get_shot_anim_thumbnail_path(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_anim_thumbnail_path: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_anim_thumbnail_path: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_anim_thumbnail_path: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/Thumbnails/{episode_name}_{seq_name}_{shot_name}_anim_thumbnail.jpg".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_animatic_thumbnail_path(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_animatic_thumbnail_path: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_animatic_thumbnail_path: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_animatic_thumbnail_path: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/Thumbnails/{episode_name}_{seq_name}_{shot_name}_animatic_thumbnail.jpg".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_comp_thumbnail_path(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_comp_thumbnail_path: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_comp_thumbnail_path: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_comp_thumbnail_path: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/Thumbnails/{episode_name}_{seq_name}_{shot_name}_comp_thumbnail.jpg".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_render_thumbnail_path(self,episode_name=None,seq_name=None,shot_name=None,**kwargs):
        if episode_name==None:
            episode_name="<episode_name>"
            logger.debug("Building path to shot_render_thumbnail_path: Argument Missing: episode_name")
        if seq_name==None:
            seq_name="<seq_name>"
            logger.debug("Building path to shot_render_thumbnail_path: Argument Missing: seq_name")
        if shot_name==None:
            shot_name="<shot_name>"
            logger.debug("Building path to shot_render_thumbnail_path: Argument Missing: shot_name")

        to_return = "P:/930383_KiwiStrit3/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/Thumbnails/{episode_name}_{seq_name}_{shot_name}_render_thumbnail.jpg".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return

