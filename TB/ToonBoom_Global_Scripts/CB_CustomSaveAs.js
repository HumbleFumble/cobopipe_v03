function find_path(){
	//var cur_scene = scene.currentScene();
	var cur_scene = scene.currentVersionName();
	var cur_full_path = scene.currentProjectPath();
	var path_split = cur_full_path.split("/")
	path_split.pop();
	var path_split = path_split.join("/");
	var new_path = "";
	var file_name = "";
	if(cur_scene.indexOf("_V")!= -1){
		file_name = NextVersion(cur_scene);
	}else{
		file_name =  cur_scene +  "_V001"
	}
	return CheckForVersions(cur_full_path, path_split, file_name);
	
}
function NextVersion(cur_scene){
	var cur_scene_split = cur_scene.split("_V");
	var next_ver = Number(cur_scene_split[1]) + 1;
	file_name  =  cur_scene_split[0] + "_V" + Pad(next_ver, 3);
	return file_name
}

function CheckForVersions(cur_folder, cur_path, cur_scene){
folder_path = cur_path + "/" + cur_scene;
file_path = cur_folder + "/" + cur_scene + ".xstage";
MessageLog.trace(cur_folder + " path: " + cur_path + " scene : " + cur_scene);
if (CheckForFiles(file_path)){
	MessageLog.trace("Found file");
	var ver_scene = NextVersion(cur_scene);
	var to_return = CheckForVersions(cur_folder,cur_path, ver_scene)
	return to_return
}else{
	if (CheckForFolder(folder_path)){
		MessageLog.trace("Found folder");
		var ver_scene = NextVersion(cur_scene);
		var to_return = CheckForVersions(cur_folder,cur_path, ver_scene)
		return to_return
	}else{
		MessageLog.trace("Did NOT find file");
		return [cur_path, cur_scene];
		}
}
}


function CheckForFiles(cur_path){
	cur_file = new File(cur_path);
	if(cur_file.exists){
		return true;
	}else{
		return false;
		}
}

function CheckForFolder(cur_path){
	cur_file = new Dir(cur_path);
	MessageLog.trace("Folder: " + cur_path);
	if(cur_file.exists){
		return true;
	}else{
		return false;
		}
}
function Pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function CustomSaveAs()
{
	var cur_path = find_path();
	
	var myDialog = new Dialog();
	myDialog.title = "Save Dialog";
	var my_text = new Label();
	my_text.text = "Save this scene as : \n" + cur_path[1];
	myDialog.add( my_text );
	cur_check = new CheckBox();
	cur_check.text = "Save in a new Folder";
	myDialog.add(cur_check);
	myDialog.okButtonText = "Click here to accept";
	myDialog.cancelButtonText = "Click here to reject";
	
	if(myDialog.exec()){		
		if (cur_check.checked ){
			save_path = cur_path[0] + "/" + cur_path[1];
			scene.saveAs(save_path);
			MessageLog.trace("SAVING: " + save_path);

			
		}else{
			save_path = cur_path[1];
			scene.saveAsNewVersion(save_path, true);
			MessageLog.trace("SAVING: " + save_path);
		}
		
		
	}else{
		MessageLog.trace("reject");
	}
}

function save_new_version()
{
	var cur_path = find_path();
    save_path = cur_path[1];
    scene.saveAsNewVersion(save_path, true);
    MessageLog.trace("SAVING: " + save_path);
}