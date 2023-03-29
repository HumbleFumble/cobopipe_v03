 #include "json2.js";

function config_prompt(){
	var ui_script = "dialog { \
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
                preferredSize: [75, 30], \
                alignment: 'right', \
                text: 'Apply' \
                }, \
        } \
    }";
		
	var ui = new Window(ui_script);
    populate_dropdown(ui.main_group.dropdown_list, true)
    ui.main_group.dropdown_list.selection = 0;
    ui.main_group.checkbox.value = true;
    ui.main_group.checkbox.onClick = function() {
        populate_dropdown(ui.main_group.dropdown_list, ui.main_group.checkbox.value);
        ui.main_group.dropdown_list.selection = 0;
    }
    ui.main_group.apply_button.onClick = function() {
        var project = ui.main_group.dropdown_list.selection;
        var project_list = get_config_options(false);
        for(var i in project_list){
            if(project.toString() === project_list[i]){
                ui.close(i);
            }
        }
    }
    return ui;
}

function populate_dropdown(dropdown, hide_archived){
    // var selection = dropdown
    dropdown.removeAll();
    var projects = get_config_options(hide_archived);
    for(var i in projects){
        dropdown.add("item", projects[i]);
    }
}

function get_config(){
	var project = get_project();
    var config_path = 'T:/_Pipeline/cobopipe_v02-001/Configs/Config_' + project + '.json';
    return loadJson(config_path);
}

function get_project(){
    var project = $.getenv( "BOM_PROJECT_NAME" );
	if(project == null){
		var ui = config_prompt();
        var index = ui.show();
        var project_list = get_config_options(false);
        return project_list[index];
	} else {
        return project;
    }
}

function get_config_options(hide_archived){
    var config_folder = Folder('T:/_Pipeline/cobopipe_v02-001/Configs');
    var files = config_folder.getFiles();
    var projects = [];

    for(var i in files){
        if(files[i].fsName.substr(-5, 5) == '.json'){
            filename = files[i].fsName.split('\\')[files[i].fsName.split('\\').length-1];
            if(filename.substr(0, 7) == 'Config_'){
                filename = filename.replace('Config_', '').replace('.json', '');
                projects.push(filename);
            }
        }
    }
    
    var archived_projects = loadJson('T:/_Pipeline/cobopipe_v02-001/Configs/archivesProjects.json');

    if(hide_archived == true){
        var non_archived_projects = [];
        for(var i in projects){
            var match = false;
            for(var j in archived_projects){
                if(projects[i] === archived_projects[j]){
                    match = true;
                }
            }
            if(match == false){
                    non_archived_projects.push(projects[i]);
            }
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
    return JSON.parse(data);
}