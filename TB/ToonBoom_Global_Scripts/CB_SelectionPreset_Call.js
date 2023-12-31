function call_CB_SelectionPreset(){


    const subselection_obj = new Object()
    subselection_obj.get_selection =function(){
        var obj_list = []
        cur_nodes = selection.selectedNodes()
        for(x in cur_nodes){
            var cur_node = cur_nodes[x];
            var newSelection = new Object;
            newSelection.node = cur_node//selection.selectedNode(0);
            newSelection.subobjects = selection.subSelectionForNode(cur_node)//newSelection.node);
            obj_list.push(newSelection)

            }
            return obj_list
    }
        subselection_obj.get_subsel_from_node =function(cur_node){
//            return_list = []
            var subs = selection.subSelectionForNode(cur_node);
            if(!subs){return []
                }
            return subs//newSelection.node);
        }
    subselection_obj.set_subselection =function(cur_node,subobjects){

        selection.addNodeToSelection(cur_node);
//        MessageLog.trace(subobjects)
        if(subobjects){
            subobjects = JSON.parse(subobjects)
            selection.addSubSelectionForNode(cur_node, subobjects);
        }
    }


    var script_name = "CB_SelectionPreset.py";

    var server_script_path = System.getenv("BOM_PIPE_PATH")

    if(server_script_path){
        MessageLog.trace("Found script at global path. Running now: " + script_name)
        var myPythonObject = PythonManager.createPyObject(server_script_path +"/TB/ToonBoom_Global_Python/" + script_name);
    }else{
        var local_folder = specialFolders.userScripts
        var script_path = local_folder + "/" + script_name
        MessageLog.trace("Checking local path: " + script_path)
        var file = new File( script_path );
        if ( file.exists ){
            MessageLog.trace("Found script at local path. Running now: " + script_path)
            var myPythonObject = PythonManager.createPyObject(script_path);
            }else{
                MessageLog.trace("Can't find python file to load. Stopping Execution of: " + script_name)
                return null
            }
        }

//    var myPythonObject = PythonManager.createPyObject(System.getenv("BOM_PIPE_PATH")+"/TB/CB_SelectionPreset.py");
    myPythonObject.setObject("js_select",subselection_obj);
    myPythonObject.setObject("js_frame",frame)
    myPythonObject.py.run();
}
