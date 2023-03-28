 #include "json2.js";

function config_ui(){
	var ui_script = "window { \
        text: 'Select Project', \
        alignChildren: 'center', \
        alignment: ['top','fill'], \
        preferredSize: [350, 75], \
        main_group: Group { \
            orientation: 'column', \
            dropdown_list: DropDownList{ \
                preferredSize: [335, 30] \
                }, \
            checkbox: Checkbox{ \
                text: 'Hide archived projects', \
                alignment: 'left' \
                }, \
            apply_button: Button{ \
                preferredSize: [335, 30], \
                text: 'Apply' \
                }, \
        } \
    }";
		
	var ui = new Window(ui_script);
	// my_window.queue_panel.buttonQ_group.runQ_button.onClick = Run;
    populate_dropdown(ui.main_group.dropdown_list, true)
    ui.main_group.checkbox.value = true;
    ui.main_group.apply_button.onClick = function() {
        var project = ui.main_group.dropdown_list.selected
        alert(project)
        ui.close()
    }

	return ui;
}

function populate_dropdown(dropdown, hide_archived){
    dropdown.removeAll();
    var projects = get_config_options(hide_archived);
    for(var i in projects){
        dropdown.add("item", projects[i])
    }
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

function get_config_options(hide_archived){
    var config_folder = Folder('T:/_Pipeline/cobopipe_v02-001/Configs');
    var files = config_folder.getFiles();
    var projects = [];

    for(var i in files){
        if(files[i].fsName.substr(-5, 5) == '.json'){
            filename = files[i].fsName.split('\\')[files[i].fsName.split('\\').length-1]
            if(filename.substr(0, 7) == 'Config_'){
                filename = filename.replace('Config_', '').replace('.json', '')
                projects.push(filename)
            }
        }
    }
    
    var archived_projects_object = loadJson('T:/_Pipeline/cobopipe_v02-001/Configs/archivesProjects.json');
    var archived_projects = [];
    for(var i in archived_projects_object){
        archived_projects.push(archived_projects_object[i])
    }
    if(hide_archived == true){
        var matches = [];
        for(var i in projects){
            for(var j in archived_projects){
                if(projects[i] === archived_projects[j]){
                    matches.push(projects[i])
                }
            }
        }
        for(var i in matches){
            alert('Hi')
            alert(projects.indexOf(matches[i]))
        }
        return non_archived_projects;
    } else {
        return projects;
    }
}

function loadJson(path){
    var scriptFile = File(path);
    scriptFile.open('r');
    var data = scriptFile.read();
    scriptFile.close();
    // return data;
    return JSON.parse(data);
}

var ui = config_ui();
ui.show();
// get_config_options();