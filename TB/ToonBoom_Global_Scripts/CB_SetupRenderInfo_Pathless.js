include("CB_GetInfo.js")

function SetupRenderInfo_Pathless(){
	// MessageLog.trace("Listing Render Nodes: ");
	//prepare render_obj
	const render_obj = new Object;
    var scene_path = scene.currentProjectPath();
	var scene_path_split =scene_path.split("/");
	scene_path_split.pop();
	scene_path = scene_path_split.join("/") + "/Passes/";
	var scene_name = scene.currentScene().split("_")[0];

	render_obj.scene_name = scene_name;
	render_obj.scene_path = scene_path;
	render_obj.list_of_names = [];

	GroupTravel("Top", "WRITE", render_obj);
	NodeRender();
}

function SetupRenderInfo_NoRender(){
	// MessageLog.trace("Listing Render Nodes: ");
	//prepare render_obj
	const render_obj = new Object;
    var scene_path = scene.currentProjectPath();
	var scene_path_split = scene_path.split("/");
	scene_path_split.pop();
	scene_path = scene_path_split.join("/") + "/Passes/";
	var scene_name = scene.currentScene().split("_")[0];

	render_obj.scene_name = scene_name;
	render_obj.scene_path = scene_path;
	render_obj.list_of_names = [];

	GroupTravel("Top", "WRITE", render_obj);
	// NodeRender();
}



function GroupTravel(groupName, my_type, render_obj)
  {
    var nNodes = node.numberOfSubNodes(groupName);

    for( var i = 0; i < nNodes; i++)
    {
      var nodeName =  node.subNode( groupName, i );
      var type = node.type( nodeName );

       if (type == my_type ){
	SetWrite(nodeName,render_obj);
	}

      if ( type == "GROUP" ){
       GroupTravel( nodeName, my_type,render_obj );
      }
    }
  }

function incrementName(my_node, render_obj){
    var write_name = node.getName(my_node);
    var orig_filename = write_name.split("RENDER_")[1];
    var x = 0
    var letter_list = ["A","B","C","D","E","F","G","H"];
    var cur_name = orig_filename;
    while( render_obj.list_of_names.indexOf(cur_name) >-1 && x<8 ){
        cur_name = orig_filename + letter_list[x]
        x = x+1;
        }
    node.rename(my_node,"RENDER_" + cur_name)
    render_obj.list_of_names.push(cur_name)
    var new_node_name = "RENDER_" + cur_name
    MessageLog.trace("orig name: " + write_name + " New name: " + cur_name);
    return new_node_name
}

function SetWrite(cur_write, render_obj){
	// MessageLog.trace(node.getName(cur_write));

	var write_name = node.getName(cur_write);

	if(write_name.search("RENDER_")>-1){
	    //check that its unique
	    var write_name = incrementName(cur_write,render_obj)
	    //get the name again in case we changed it
//	    write_name = node.getName(cur_write);
//	    MessageLog.trace("Node name: " + write_name);
		var filename = write_name.split("RENDER_")[1];
		var final_path = render_obj.scene_path + filename + "_";
		var project_settings = GetProjectSettings();
		var drawing_type = project_settings.tb_output_format;
		node.setTextAttr(cur_write, "DRAWING_TYPE", 0, drawing_type); //specify HERE the drawing type
		var leading_zeros = project_settings.tb_number_padding;
		// MessageLog.trace(leading_zeros);
   	node.setTextAttr(cur_write, "LEADING_ZEROS", 0, leading_zeros); //specify HERE the number of leading zeros
   	node.setTextAttr(cur_write, "DRAWING_NAME", 0, final_path);
	}else{
	MessageLog.trace("Not a render node, disabling");
	node.setEnable(cur_write, false);
	}
}

function NodeRender(){
	var temp = Action.perform("onActionComposite()");
}