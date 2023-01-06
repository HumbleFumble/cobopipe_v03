function SetupRenderInfo(){
	MessageLog.trace("Listing Render Nodes: ");
	GroupTravel("Top", "WRITE");
}

function GroupTravel(groupName,my_type) 
  {
    var nNodes = node.numberOfSubNodes(groupName);

    for( var i = 0; i < nNodes; i++)
    {
      var nodeName =  node.subNode( groupName, i );
      var type = node.type( nodeName );

       if (type == my_type ){
	SetWrite(nodeName);
	}

      if ( type == "GROUP" ){
       GroupTravel( nodeName, my_type );
      }
    }
  }

function SetWrite(cur_write){
	MessageLog.trace(node.getName(cur_write));
	var scene_path = scene.currentProjectPath();
	var scene_path_split =scene_path.split("/");
	scene_path_split.pop();
	scene_path = scene_path_split.join("/") + "/Passes/";
	var scene_name = scene.currentScene().split("_")[0];
	
	var write_name = node.getName(cur_write);
	if(write_name.search("RENDER_")>-1){
		var filename = write_name.split("RENDER_")[1];
		var final_path = scene_path + filename;
		node.setTextAttr(cur_write, "DRAWING_TYPE", 0, "PNG4"); //specify HERE the drawing type
   		node.setTextAttr(cur_write, "LEADING_ZEROS", 0, "2"); //specify HERE the number of leading zeros
   		node.setTextAttr(cur_write, "DRAWING_NAME", 0, final_path);
	}else{
	MessageLog.trace("Not a render node, disabling");
	node.setEnable(cur_write, false);
	}
}
