 #include "json2.js";

function config_ui(){
	var ui_script = "window { \
        text: 'Select Project', \
        alignChildren: 'center', \
        alignment: ['top','fill'], \
        preferredSize: [300, 75], \
        main_group: Group { \
            orientation: 'column', \
            dropdown_list: DropDownList{ \
                preferredSize: [270, 30] \
                },\
            apply_button: Button{ \
                preferredSize: [270, 30]\
                text: 'Apply' \
                },\
        } \
    }";
		
	var ui = new Window(ui_script);
	// my_window.queue_panel.buttonQ_group.runQ_button.onClick = Run;
    populate_dropdown(ui.main_group.dropdown)
    ui.main_group.apply_button.onClick = function() {
        var project = ui.main_group.dropdown_list.selected
        alert(project)
        ui.close()
    }

	return ui;
}

function populate_dropdown(dd){
    dd.removeAll();
    // var config_folder = Folder('T:/_Pipeline/cobopipe_v02-001/Configs');
    // var files = config_folder.getFiles();
    // var config_files = [];
    // for(i in files){
    //     if(files[i].fsName.substr(-5, 5) == '.json'){
    //         if()
    //     }
    // }
}

function get_config(){
	var project_name = $.getenv( "BOM_PROJECT_NAME" )
	if(project_name == null){
		var config_folder = Folder('T:/_Pipeline/cobopipe_v02-001/Configs');
		var files = config_folder.getFiles();
		var config_files = [];
		for(i in files){
			if(files[i].fsName.substr(-5, 5) == '.json'){
				config_files.push(files[i])
			}
		}
	}
}

function get_config_options(){
    var config_folder = Folder('T:/_Pipeline/cobopipe_v02-001/Configs');
    var files = config_folder.getFiles();
    var config_files = [];
    for(i in files){
        if(files[i].fsName.substr(-5, 5) == '.json'){
            filename = files[i].fsName.split('\\')[files[i].fsName.split('\\').length-1]
            if(filename.substr(0, 7) == 'Config_'){
                filename = filename.replace('Config_', '').replace('.json', '')
                config_files.push({'name': filename, 'file': files[i]})
            }
        }
    }
    var archived_projects = loadJson('T:/_Pipeline/cobopipe_v02-001/Configs/archivesProjects.json');
    alert('hi')
    alert(archived_projects)
    // for(i in config_files){
    //     alert(config_files[i].name)
    // }
}

function loadJson(path){
    var scriptFile = File(path);
    scriptFile.open('r');
    var data = scriptFile.read();
    scriptFile.close();
    return data;
    // return JSON.parse(data);
}

// var ui = config_ui();
// ui.show();
get_config_options();