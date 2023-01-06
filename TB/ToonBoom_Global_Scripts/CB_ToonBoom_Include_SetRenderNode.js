function PrepareForRender(output_format,leading_zero){
	SetRenderSceneName();
	MessageLog.trace("Listing Render Nodes: ");

    const render_obj = new Object;
    var scene_path = scene.currentProjectPath();
	var scene_path_split =scene_path.split("/");
	scene_path_split.pop();
	scene_path = scene_path_split.join("/") + "/Passes/";
	var scene_name = scene.currentScene().split("_")[0];

	render_obj.scene_name = scene_name;
	render_obj.scene_path = scene_path;
	render_obj.list_of_names = [];
    render_obj.leading_zero = leading_zero
    render_obj.output_format = output_format

	GroupTravel("Top", "WRITE",render_obj);
	scene.saveAll();
}

function GroupTravel(groupName,my_type,render_obj)
  {
    var nNodes = node.numberOfSubNodes(groupName);

    for( var i = 0; i < nNodes; i++)
    {
      var nodeName =  node.subNode( groupName, i );
      var type = node.type( nodeName );

       if (type == my_type ){
	SetWrite(nodeName,render_obj);
	node.setEnable(nodeName, true);
	}

      if ( type == "GROUP" ){
       GroupTravel( nodeName, my_type,render_obj );
      }
    }
  }

function incrementName(my_node,render_obj){
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
}

function SetWrite(cur_write,render_obj){
	MessageLog.trace(node.getName(cur_write));

	var write_name = node.getName(cur_write);
	if(write_name.search("RENDER_")>-1){
		//check that its unique
	    incrementName(cur_write,render_obj)
	    //get the name again in case we changed it
	    write_name = node.getName(cur_write);
		var filename = write_name.split("RENDER_")[1];
		var final_path = render_obj.scene_path + filename + "_";
		node.setTextAttr(cur_write, "DRAWING_TYPE", 0, render_obj.output_format); //specify HERE the drawing type
   		node.setTextAttr(cur_write, "LEADING_ZEROS", 0, render_obj.leading_zero); //specify HERE the number of leading zeros
   		node.setTextAttr(cur_write, "DRAWING_NAME", 0, final_path);
	}else{
	MessageLog.trace("Not a render node, disabling");
	node.setEnable(cur_write, false);
	}
}

function NodeRender(){
    var temp = Action.perform("onActionComposite()");
}

function FindSceneName(){

	var cur_scene = scene.currentVersionName();
	var file_name = "";
	if(cur_scene.indexOf("_V")!= -1){
		var name_split = cur_scene.split("_V");
		file_name = name_split[0];
	}else{
		file_name =  cur_scene
	}
	return file_name
}

function SetRenderSceneName(){
	new_name = "RENDER_" + FindSceneName();
	node.rename("Top/RENDER_SCENE", new_name);
}
