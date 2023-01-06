function CreateAnimPreview(){
	//var cur_scene = scene.currentScene();
	var cur_scene = scene.currentVersionName();
	var cur_full_path = scene.currentProjectPath();
	if(cur_scene.indexOf("_V")!= -1){
		shot = cur_scene.split("_V")[0];
	}else{
		shot = cur_scene;
	}
	var seq_path = cur_full_path.split("/" + shot + "/")[0]
	var folder_path = seq_path + "/_Preview/" ;
	var shot_name = shot + ".mov";
	var final_path = folder_path + shot_name;
	/* //Need to export a certain display node, then select it.
	var dis_module = selection.selectedNodes()[0];
	var dis_name = node.getName(dis_module);
	//exporter.exportToQuicktime(dis_name, "-1","-1",true,"1920","1080",final_path,dis_module,false,"1");
	*/
	exporter.exportToQuicktime("", "-1","-1",true,"1280","720",final_path,"",false,"1");
}