function GetInfo(){
	var project = GetProject();
	var user = GetUser(project);
	return [project, user];
}


function GetProject(){
	var project_name = System.getenv("BOM_PROJECT_NAME");
	if(project_name){
		MessageLog.trace(project_name);
	}else{
		project_name = PickProject();
	}	
	return project_name
}


function GetUser(project){
	var user = System.getenv("BOM_USER");
	if(user){
		MessageLog.trace(user);
	}else{
		user = PickUser(project);
	}
	return user;
}


function PickProject(){
	var myDialog = new Dialog();
	myDialog.title = "Pick Project";
	myDialog.width = 300;
	var userInput = new ComboBox();
	userInput.minWidth = 300;
	userInput.label = "Pick Current Project";
	userInput.editable = true;
	userInput.itemList = ["Boerste_Season2", "MiasMagic2","Hoj"];
	myDialog.add( userInput );
	if ( myDialog.exec() ){
  		MessageLog.trace(userInput.currentItem);
	}
	else{
		MessageLog.trace("Cancelled");
	}
	return userInput.currentItem;
}


function FindUserFromProject(config_info){
	var user_dict = config_info.users;
	key_list = Object.keys(user_dict);
	var return_users = [];
	for(key in key_list) {
		return_users = return_users.concat(user_dict[key_list[key]]);
	}
	return_users.sort();	
	return return_users
}


function PickUser(project){
	var config = loadConfigJson(project);
	var project_users = FindUserFromProject(config);
	var cur_user = preferences.getString("ProjectUser","")
	var start_index = 0;
	if(project_users.indexOf(cur_user)>-1){
        var start_index = project_users.indexOf(cur_user)
	}
	var myDialog = new Dialog();
	myDialog.title = "Pick User";
	myDialog.width = 300;
	var userInput = new ComboBox();
	userInput.minWidth = 300;
	userInput.label = "Pick Current User";
	userInput.editable = true;
	userInput.itemList = project_users;
	userInput.currentItemPos = start_index
	myDialog.add( userInput );

	if ( myDialog.exec() ){
  		var picked =  userInput.currentItem;
  		preferences.setString("ProjectUser",picked)
	}
	else{
		var picked = null
	}
	return picked;
}


function loadConfigJson(){
    project_name = GetProject();
    var config_file = System.getenv("BOM_PIPE_PATH") + "/Configs/Config_" + project_name + ".json";
    var myFile = new PermanentFile(config_file);
    myFile.open(1);
    var jsonFileContent = myFile.read();
    myFile.close();
    //MessageLog.trace(jsonFileContent);
    // Restore the read selection in Harmony.
    var project_config = JSON.parse(jsonFileContent);
    //MessageLog.trace(project_config.project_name)
    //FindUserFromProject(project_config);
    return project_config;
}


function GetProjectSettings(){
    try{
	var config = loadConfigJson();
	return config.project_settings;
	}
	catch(err){
	return null
	}
}

function GetProjectPaths(){
	try{
	var config = loadConfigJson();
	return config.project_paths;
	}
	catch(err){
	return null
	}
}

exports.GetProjectSettings = GetProjectSettings;
exports.loadConfigJson = loadConfigJson;
exports.GetUser = GetUser;
