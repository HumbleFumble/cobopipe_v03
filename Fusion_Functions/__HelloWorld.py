# This is the typical file structure of a fusion tool


class HelloWorld(object):

    __fusion = None
    def __init__(self, fusion):
        self.__fusion = fusion
        self.__comp = self.__fusion.GetCurrentComp()
        #self.resetFrameRender()
        # self.CryptoPreRender()
        # user_info = self.askUserInfo()
        # self.renderSelection()
        # self.profiler()
        self.submitWindow()


    def submitWindow(self):
        # from Fusion_Functions.getProjectAndUserInfo import askUserInfo
        # ask_input = askUserInfo(self.__comp)
        # if ask_input:
        #     project, user = ask_input
        from Maya_Functions.file_util_functions import saveJson, loadJson
        fusion_user_data = "C:/Temp/fusion_user_data.json"
        cur_data = loadJson(fusion_user_data)
        submit_default = 0
        check_local_default = 0
        if cur_data:
            print(cur_data)
            if "submitDrop" in cur_data.keys():
                submit_default = cur_data["submitDrop"]
            if "checkbox_local" in cur_data.keys():
                check_local_default = cur_data["checkbox_local"]
        submit_dropdown = {1: "submitDrop", "Name": "Render:", 2: "Dropdown", "Options": ["Comp + Preview","Comp Only","Preview Only"], "Default": submit_default}
        check_box_local = {1: "checkbox_local", "Name": "Render Locally", 2: "Checkbox",
                            "Default": check_local_default}
        dialog = {1: submit_dropdown,2:check_box_local}
        ret = self.__comp.AskUser("Submit Options:", dialog)
        if ret:
            print(ret.values())
            submit_type = int(ret.values()[0])
            render_local = int(ret.values()[1])
            cur_data["submitDrop"] = submit_type
            cur_data["checkbox_local"] = render_local
            saveJson(fusion_user_data,cur_data)
            return [submit_type,render_local]
        return False

    def greetings(self):
        print("\nHello World!")
        print("From filepath: '" + __file__ + "'\n")

    def printFusionReference(self):
        print("fusion module reference:")
        print(self.__fusion)
        print("")

    def printLoaderSavers(self):
        print("Savers & Loaders:")
        print(self.__comp.GetToolList(False, "Loader").values())
        print(self.__comp.GetToolList(False, "Saver").values())
        print("")

    def renderSelection(self, selected_savers=None):
        all_savers = self.__comp.GetToolList(False,"Saver").values()
        if not selected_savers:
            selected_savers = self.__comp.GetToolList(True,"Saver").values()
        #Get state of savers:
        save_dict = {}
        print("ALL: %s" % all_savers)
        print("Selected: %s" % selected_savers)
        for sel_saver in selected_savers:
            print(sel_saver.GetAttrs()["TOOLS_Name"])
            save_dict[sel_saver.GetAttrs()["TOOLS_Name"]] =""
        for saver in all_savers:
            cur_name = saver.GetAttrs()["TOOLS_Name"]
            print(saver)
            if cur_name in save_dict.keys():
                save_dict[cur_name] = saver.GetAttrs()["TOOLB_PassThrough"]
                saver.SetAttrs({"TOOLB_PassThrough": False})
            else:
                save_dict[cur_name] = saver.GetAttrs()["TOOLB_PassThrough"]
                saver.SetAttrs({"TOOLB_PassThrough":True})

            #RENDERING
        self.__comp.Lock()
        self.__comp.Render(True)
        for key_saver in save_dict.keys():
            cur_tool = self.__comp.FindTool(key_saver)
            cur_tool.SetAttrs({"TOOLB_PassThrough":save_dict[key_saver]})
        self.__comp.Unlock()




            # print(saver.SetAttrs({"TOOLB_PassThrough":})
        # self.__comp.Render()

    def CryptoPreRender(self):
        # TO DO: Turn on Render when savers are made? Also turn off all other savers when rendering.

        import os
        selected_crypto = self.__comp.GetToolList(True,"Fuse.Cryptomatte").values()
        print(selected_crypto)
        flow = self.__comp.CurrentFrame.FlowView
        all_savers = []
        reload_loaders = []
        for sel in selected_crypto:
            sel_attrs = sel.GetAttrs()
            # print(sel_attrs.Input)
            crypto_loader_name = sel_attrs["TOOLS_Name"]
            print("Working on: %s" % crypto_loader_name)
            x,y = flow.GetPosTable(sel).values()
            output = sel.FindMainInput(1).GetConnectedOutput()
            in_node = output.GetTool()
            print("Found Crypto Input: %s" % in_node.GetAttrs()["TOOLS_Name"])
            crypto_folder, crypto_file = os.path.split(in_node.Clip[0])
            out_nodes = sel.FindMainOutput(1).GetConnectedInputs()
            self.__comp.Lock()
            new_saver = self.__comp.AddTool("Saver",1,1)
            flow.SetPos(new_saver,float(x+1.0),float(y))
            footage_filename = "%s/%s/%s_PreRender_0001.png" % (crypto_folder,crypto_loader_name,crypto_loader_name)
            new_saver.Clip = footage_filename
            #Connect to Crypto-Matte
            new_saver.SetAttrs({"TOOLS_Name":"%s_Saver" % crypto_loader_name})
            all_savers.append(new_saver)
            saver_input = new_saver.FindMainInput(1)
            saver_input.ConnectTo(sel.Output)

            new_loader = self.__comp.AddTool("Loader",1,1)
            flow.SetPos(new_loader, float(x), float(y-1))
            loader_output = new_loader.FindMainOutput(1)
            new_loader.SetAttrs({"TOOLS_Name": "%s_PreRender" % crypto_loader_name})
            print(out_nodes.values())
            for out_node in out_nodes.values():
                # print("Connecting %s to %s:" % (cur_out_node["TOOLS_Name"]))
                print(out_node.GetAttrs())
                if not "INPS_ID" in out_node.GetAttrs().keys():
                    continue
                cur_input_name = out_node.GetAttrs()["INPS_ID"]
                cur_out_node = out_node.GetTool()
                cur_input = cur_out_node[cur_input_name]
                # cur_input = cur_out_node.FindMainInput(1)
                cur_input.ConnectTo(loader_output)
            new_loader.Clip = footage_filename

            self.__comp.Unlock()
        self.renderSelection(selected_savers=all_savers)
        for cur_loader in reload_loaders:
            cur_loader.Clip = cur_loader.Clip


    def workWithLoaders(self):
        loaders = self.__comp.GetToolList(True, "Loader").values()
        test_dict = loaders[0].GetAttrs()
        print(loaders[0])
        l = loaders[0]
        print(l.Clip[0])
        print("HEYEYEY")
        #Working with the channel that should be selected
        print(l.Clip1.OpenEXRFormat.Part[0])
        exr_dict = l.Clip1.OpenEXRFormat.Part.GetAttrs()

        channel_dict = l.Clip1.OpenEXRFormat.Part.GetAttrs()["INPIDT_ComboControl_ID"]
        cur_part = l.Clip1.OpenEXRFormat.Part[0]
        mid_oid_dict = {"MID":{},"OID":{}}

        for combo_name in channel_dict.values():
            # combo_name = channel_dict[combo_id]
            mid_info = self.returnRangeInfo(combo_name,"MID")
            oid_info = self.returnRangeInfo(combo_name,"OID")
            if mid_info:
                mid_oid_dict["MID"][int(mid_info)] = combo_name
            if oid_info:
                mid_oid_dict["OID"][int(oid_info)] = combo_name
        for cur_type in ["MID","OID"]:
            cur_range = self.returnRangeInfo(cur_part,cur_type)
            if cur_range:
                if cur_range in mid_oid_dict[cur_type].keys():
                    l.Clip1.OpenEXRFormat.Part = mid_oid_dict[cur_type][cur_range]
                else:
                    print("Can't find RenderElement %s_%s..." % (cur_type,cur_range))

    def returnRangeInfo(self,name,ID_type):
        if ID_type in name:
            range = name.split("_")[1]
            if "-" in range:
                range = range.split("-")[0]
            # print("For %s - range is: %s" % (name,int(range)))
            return int(range)
        return None

    def returnConfig(self):
        from getConfig import getConfigClass
        CC = getConfigClass(project_name="MiasMagic2")
        print(CC.project_name)

    def profiler(self):
        all_tools = self.__comp.GetToolList().values()
        time_dict = {}
        for cur_tool in all_tools:
            cur_attrs = cur_tool.GetAttrs()
            if not cur_attrs["TOOLB_PassThrough"]:
                time_dict[cur_attrs["TOOLS_Name"]] = cur_attrs["TOOLN_LastFrameTime"]
        sorted_keys = sorted(time_dict.items(), key=lambda x: x[1])
        for cur in sorted_keys:
            cur_time = cur[1]
            if cur_time > 0:
                print("{:>50}:{:>25.2f}".format(cur[0],cur_time))

    def resetFrameRender(self):
        print("Reseting timers")
        all_tools = self.__comp.GetToolList().values()
        print(all_tools[0].GetAttrs())
        for cur_tool in all_tools:
            cur_tool.SetAttrs({"TOOLN_LastFrameTime":0})

    def askUserInfo(self):
        from Fusion_Functions.getProjectAndUserInfo import askUserInfo
        print(askUserInfo(self.__comp))
        # from Maya_Functions.file_util_functions import saveJson, loadJson
        # import os
        # project_name = None
        # if "BOM_PROJECT_NAME" in os.environ:
        #     if not os.environ["BOM_PROJECT_NAME"] == "":
        #          project_name = os.environ["BOM_PROJECT_NAME"]
        #
        # fusion_user_data = "C:/Temp/fusion_user_data.json"
        # cur_data = loadJson(fusion_user_data)
        # project_options = ["MiasMagic2","CowOnTheRun","KiwiStrit3"]
        # user_options = ["Bernardo","Christian", "Jesper","Johanna","Kaare","Mads"]
        #
        # project_default = 0
        # user_default = 0
        # if cur_data:
        #     if cur_data["user"] in user_options:
        #         user_default = user_options.index(cur_data["user"])
        #     if cur_data["project"] in user_options:
        #         project_default = user_options.index(cur_data["project"])
        # else:
        #     cur_data = {}
        # # gui
        # project_dropdown = {1: "projDrop", "Name": "Project", 2: "Dropdown", "Options": project_options, "Default": project_default}
        # user_dropdown = {1: "userDrop", "Name": "User", 2: "Dropdown", "Options": user_options, "Default": user_default}
        # if not project_name:
        #     dialog = {1: project_dropdown,2:user_dropdown}
        #     ret = self.__comp.AskUser("Choose project and user:", dialog)
        #     if ret:
        #         project_return = project_options[int(ret.values()[0])]
        #         user_return = project_options[int(ret.values()[1])]
        #         cur_data["project"] = project_return
        #         cur_data["user"] = user_return
        #         os.environ["BOM_PROJECT_NAME"] = project_return
        #     else:
        #         return False
        # else:
        #     dialog = {1:user_dropdown}
        #     ret = self.__comp.AskUser("Choose project and user:", dialog)
        #     if ret:
        #         user_return = project_options[int(ret.values()[0])]
        #         cur_data["project"] = project_name
        #         cur_data["user"] = user_return
        #     else:
        #         return False
        # saveJson(fusion_user_data,cur_data)
        # return [cur_data["project"],cur_data["user"]]


        # return _pass_options[int(pass_status[0])]
