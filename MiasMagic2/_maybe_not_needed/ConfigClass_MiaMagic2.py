
class ConfigClass():
    def __init__(self):
        self.project_name="MiaMagic2"
        self.base_path="P:/_WFH_Projekter/930450_MiasMagicComicBook/Production"
        self.asset_top_path="<base_path>/Assets/3D_Assets"
        self.asset_base_path="<asset_top_path>/<asset_type>/<asset_category>/<asset_name>"
        self.asset_work_folder="<asset_base_path>/01_Work/Maya"
        self.asset_ref_folder="<asset_base_path>/02_Ref"
        self.asset_texture_folder="<asset_base_path>/03_Texture"
        self.asset_work_path="<asset_work_folder>/<asset_name>_<asset_step>"
        self.update_log_path="C:/Temp/Update_Log.txt"
        self.maya_env=""
        self.film_path="<base_path>/Film"
        self.episode_path="<film_path>/<episode_name>"
        self.seq_path="<episode_path>/<episode_name>_<seq_name>"
        self.shot_path="<seq_path>/<episode_name>_<seq_name>_<shot_name>"
        self.shot_anim_path="<shot_path>/01_Animation/<episode_name>_<seq_name>_<shot_name>_Animation.ma"
        self.shot_light_file="<shot_path>/02_Light/<episode_name>_<seq_name>_<shot_name>_Light.ma"
        self.sequence_preview_folder="<seq_path>/_Preview"
        self.shot_anim_preview_file="<sequence_preview_folder>/<episode_name>_<seq_name>_<shot_name>.mov"
        self.shot_animatic_file="<shot_path>/<episode_name>_<seq_name>_<shot_name>_Animatic.mov"
        self.shot_render_path="<shot_path>/04_Publish/<episode_name>_<seq_name>_<shot_name>_<render_prefix>_Render.ma"
        self.shot_passes_folder="<shot_path>/passes/<render_prefix>/<episode_name>_<seq_name>_<shot_name>_<render_prefix>_"
        self.shot_comp_folder="<shot_path>/03_Comp/"
        self.shot_comp_output_folder="<shot_path>/05_CompOutput"
        self.shot_comp_output_file="<shot_comp_output_folder>/<episode_name>_<seq_name>_<shot_name>_0001.exr"
        self.shot_comp_preview_file="<sequence_preview_folder>/<episode_name>_<seq_name>_<shot_name>_Comp.mov"
        self.shot_yeti_cache_path="<shot_path>/04_Publish/YetiCache/"
        self.template_path="<base_path>/Pipeline/Template"
        self.render_presets="<base_path>/Pipeline/RenderSettings_Presets/"
        self.render_preset_config="<base_path>/Pipeline/render_preset_config.json"
        self.OID_set_rules="<base_path>/Pipeline/OID_set_rules.json"
        self.light_export_folder="<base_path>/Assets/Light_Setups/Light_Export_Groups/"
        self.contact_sheet_category_file="<base_path>/Pipeline/contact_sheet_category.json"
        self.module_path=""
        
        self.Anim="<asset_ref_folder>/<asset_name>_<asset_output>.mb"
        self.Render="<asset_ref_folder>/<asset_name>_<asset_output>.mb"
        self.Model="<asset_ref_folder>/<asset_name>_<asset_step>_Ref.mb"
        self.Rig="<asset_ref_folder>/<asset_name>_<asset_step>_Ref.mb"
        self.Blendshape="<asset_ref_folder>/<asset_name>_<asset_step>_Ref.mb"
        self.GPU="<asset_ref_folder>/<asset_name>_GPU.abc"
        self.VrayProxy="<asset_ref_folder>/<asset_name>_VrayProxy.vrmesh"
        self.YetiGroom="<asset_ref_folder>/YetiGroom/<asset_name>_<yeti_node>_Groom.grm"
        self.YetiAlembicCache="<asset_ref_folder>/YetiGroom/<asset_name>_<yeti_node>_AlembicCache.abc"
        self.AnimScene="<shot_path>/04_Publish/<episode_name>_<seq_name>_<shot_name>_AnimRef.mb"
        

    def get_base_path(self):
        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production"
        return to_return


    def get_asset_top_path(self):
        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets"
        return to_return


    def get_asset_base_path(self,asset_type=None,asset_category=None,asset_name=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_asset_work_folder(self,asset_type=None,asset_category=None,asset_name=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/01_Work/Maya".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_asset_ref_folder(self,asset_type=None,asset_category=None,asset_name=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_asset_texture_folder(self,asset_type=None,asset_category=None,asset_name=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/03_Texture".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_asset_work_path(self,asset_type=None,asset_category=None,asset_name=None,asset_step=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")
        if asset_step==None:
            raise NameError("Argument Missing: asset_step")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/01_Work/Maya/{asset_name}_{asset_step}".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,asset_step=asset_step,)
        return to_return


    def get_update_log_path(self):
        to_return = "C:/Temp/Update_Log.txt"
        return to_return


    def get_maya_env(self):
        to_return = ""
        return to_return


    def get_film_path(self):
        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film"
        return to_return


    def get_episode_path(self,episode_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}".format(episode_name=episode_name,)
        return to_return


    def get_seq_path(self,episode_name=None,seq_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}".format(episode_name=episode_name,seq_name=seq_name,)
        return to_return


    def get_shot_path(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_anim_path(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/01_Animation/{episode_name}_{seq_name}_{shot_name}_Animation.ma".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_light_file(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/02_Light/{episode_name}_{seq_name}_{shot_name}_Light.ma".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_sequence_preview_folder(self,episode_name=None,seq_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/_Preview".format(episode_name=episode_name,seq_name=seq_name,)
        return to_return


    def get_shot_anim_preview_file(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/_Preview/{episode_name}_{seq_name}_{shot_name}.mov".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_animatic_file(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/{episode_name}_{seq_name}_{shot_name}_Animatic.mov".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_render_path(self,episode_name=None,seq_name=None,shot_name=None,render_prefix=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")
        if render_prefix==None:
            raise NameError("Argument Missing: render_prefix")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/04_Publish/{episode_name}_{seq_name}_{shot_name}_{render_prefix}_Render.ma".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,render_prefix=render_prefix,)
        return to_return


    def get_shot_passes_folder(self,episode_name=None,seq_name=None,shot_name=None,render_prefix=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")
        if render_prefix==None:
            raise NameError("Argument Missing: render_prefix")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/passes/{render_prefix}/{episode_name}_{seq_name}_{shot_name}_{render_prefix}_".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,render_prefix=render_prefix,)
        return to_return


    def get_shot_comp_folder(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/03_Comp/".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_comp_output_folder(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/05_CompOutput".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_comp_output_file(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/05_CompOutput/{episode_name}_{seq_name}_{shot_name}_0001.exr".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_comp_preview_file(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/_Preview/{episode_name}_{seq_name}_{shot_name}_Comp.mov".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_yeti_cache_path(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/04_Publish/YetiCache/".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_template_path(self):
        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Pipeline/Template"
        return to_return


    def get_render_presets(self):
        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Pipeline/RenderSettings_Presets/"
        return to_return


    def get_render_preset_config(self):
        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Pipeline/render_preset_config.json"
        return to_return


    def get_OID_set_rules(self):
        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Pipeline/OID_set_rules.json"
        return to_return


    def get_light_export_folder(self):
        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/Light_Setups/Light_Export_Groups/"
        return to_return


    def get_contact_sheet_category_file(self):
        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Pipeline/contact_sheet_category.json"
        return to_return


    def get_module_path(self):
        to_return = ""
        return to_return


    def get_Anim(self,asset_type=None,asset_category=None,asset_name=None,asset_output=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")
        if asset_output==None:
            raise NameError("Argument Missing: asset_output")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_{asset_output}.mb".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,asset_output=asset_output,)
        return to_return


    def get_Render(self,asset_type=None,asset_category=None,asset_name=None,asset_output=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")
        if asset_output==None:
            raise NameError("Argument Missing: asset_output")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_{asset_output}.mb".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,asset_output=asset_output,)
        return to_return


    def get_Model(self,asset_type=None,asset_category=None,asset_name=None,asset_step=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")
        if asset_step==None:
            raise NameError("Argument Missing: asset_step")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_{asset_step}_Ref.mb".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,asset_step=asset_step,)
        return to_return


    def get_Rig(self,asset_type=None,asset_category=None,asset_name=None,asset_step=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")
        if asset_step==None:
            raise NameError("Argument Missing: asset_step")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_{asset_step}_Ref.mb".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,asset_step=asset_step,)
        return to_return


    def get_Blendshape(self,asset_type=None,asset_category=None,asset_name=None,asset_step=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")
        if asset_step==None:
            raise NameError("Argument Missing: asset_step")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_{asset_step}_Ref.mb".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,asset_step=asset_step,)
        return to_return


    def get_GPU(self,asset_type=None,asset_category=None,asset_name=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_GPU.abc".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_VrayProxy(self,asset_type=None,asset_category=None,asset_name=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/{asset_name}_VrayProxy.vrmesh".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_YetiGroom(self,asset_type=None,asset_category=None,asset_name=None,yeti_node=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")
        if yeti_node==None:
            raise NameError("Argument Missing: yeti_node")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/YetiGroom/{asset_name}_{yeti_node}_Groom.grm".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,yeti_node=yeti_node,)
        return to_return


    def get_YetiAlembicCache(self,asset_type=None,asset_category=None,asset_name=None,yeti_node=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")
        if yeti_node==None:
            raise NameError("Argument Missing: yeti_node")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/02_Ref/YetiGroom/{asset_name}_{yeti_node}_AlembicCache.abc".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,yeti_node=yeti_node,)
        return to_return


    def get_AnimScene(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/04_Publish/{episode_name}_{seq_name}_{shot_name}_AnimRef.mb".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_asset_thumbnail_path(self,asset_type=None,asset_category=None,asset_name=None,):
        if asset_type==None:
            raise NameError("Argument Missing: asset_type")
        if asset_category==None:
            raise NameError("Argument Missing: asset_category")
        if asset_name==None:
            raise NameError("Argument Missing: asset_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Assets/3D_Assets/{asset_type}/{asset_category}/{asset_name}/04_Design/Thumbnail/{asset_name}_thumbnail.png".format(asset_type=asset_type,asset_category=asset_category,asset_name=asset_name,)
        return to_return


    def get_folder_icon_path(self):
        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Pipeline/Resource/icon/folder.png"
        return to_return


    def get_no_thumb_icon_path(self):
        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Pipeline/Resource/icon/No_Thumbnail.png"
        return to_return


    def get_shot_animatic_thumbnail_path(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/Thumbnails/{episode_name}_{seq_name}_{shot_name}_animatic_thumbnail.jpg".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_anim_thumbnail_path(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/Thumbnails/{episode_name}_{seq_name}_{shot_name}_anim_thumbnail.jpg".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_render_thumbnail_path(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/Thumbnails/{episode_name}_{seq_name}_{shot_name}_render_thumbnail.jpg".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return


    def get_shot_comp_thumbnail_path(self,episode_name=None,seq_name=None,shot_name=None,):
        if episode_name==None:
            raise NameError("Argument Missing: episode_name")
        if seq_name==None:
            raise NameError("Argument Missing: seq_name")
        if shot_name==None:
            raise NameError("Argument Missing: shot_name")

        to_return = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/{episode_name}/{episode_name}_{seq_name}/{episode_name}_{seq_name}_{shot_name}/Thumbnails/{episode_name}_{seq_name}_{shot_name}_comp_thumbnail.jpg".format(episode_name=episode_name,seq_name=seq_name,shot_name=shot_name,)
        return to_return

