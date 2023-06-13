class UtilityClass(object):
    __fusion = None
    def __init__(self, fusion):
        self.__fusion = fusion
        self.__comp = self.__fusion.GetCurrentComp()

    def FindLoaders(self, pass_name="ColorB"):
        loaders = self.__comp.GetToolList(False, "Loader").values()
        selection_set = []
        for cur_loader in loaders:
            cur_loader_path = (cur_loader.GetAttrs("TOOLST_Clip_Name")[1]).replace("\\", "/")
            # print(cur_loader_path)
            if pass_name in cur_loader_path:
                selection_set.append(cur_loader)
        # print(selection_set)
        self.__comp.SetActiveTool(selection_set[0])



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

    def CryptoPreRender(self):
        # TO DO: Turn on Render when savers are made? Also turn off all other savers when rendering.

        import os
        selected_crypto = self.__comp.GetToolList(True,"Fuse.Cryptomatte").values()
        print(selected_crypto)
        flow = self.__comp.CurrentFrame.FlowView
        if not flow:
            print("-------- PlEASE RESET/DEFAULT YOUR LAYOUT -----------")
            return False
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

    def nodeProfiler(self):
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