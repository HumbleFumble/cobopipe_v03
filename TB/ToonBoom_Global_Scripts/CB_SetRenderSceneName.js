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


