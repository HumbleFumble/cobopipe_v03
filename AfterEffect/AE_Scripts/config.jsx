 #include "json2.js";

function config_prompt(){
    // alert('config_prompt 01')
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
    // alert('config_prompt 02')
	var ui = new Window(ui_script);
    // alert('config_prompt 03')
    populate_dropdown(ui.main_group.dropdown_list, true)
    // alert('config_prompt 04')
    ui.main_group.dropdown_list.selection = 0;
    // alert('config_prompt 05')
    ui.main_group.checkbox.value = true;
    // alert('config_prompt 06')
    ui.main_group.checkbox.onClick = function() {
        // alert('config_prompt 07')
        populate_dropdown(ui.main_group.dropdown_list, ui.main_group.checkbox.value);
        // alert('config_prompt 08')
        ui.main_group.dropdown_list.selection = 0;
        // alert('config_prompt 09')
    }
    // alert('config_prompt 10')
    ui.main_group.apply_button.onClick = function() {
        // alert('config_prompt 11')
        var project = ui.main_group.dropdown_list.selection;
        // alert('config_prompt 12')
        var project_list = get_config_options(false);
        // alert('config_prompt 13')
        for(var i in project_list){
            // alert('config_prompt 14')
            if(project.toString() === project_list[i]){
                // alert('config_prompt 15')
                ui.close(i);
            }
        }
    }
    // alert('config_prompt 16')
    return ui;
}

function populate_dropdown(dropdown, hide_archived){
    // alert('populate_dropdown 01')
    dropdown.removeAll();
    // alert('populate_dropdown 02')
    var projects = get_config_options(hide_archived);
    // alert('populate_dropdown 03')
    for(var i in projects){
        dropdown.add("item", projects[i]);
    }
    // alert('populate_dropdown 04')
}

function get_config(){
    // alert('get_config 01')
	var project = get_project();
    // alert('get_config 02')
    var config_path = 'T:/_Pipeline/cobopipe_v02-001/Configs/Config_' + project + '.json';
    // alert('get_config 03')
    return loadJson(config_path);
    // alert('get_config 04')
}

function get_project(){
    // alert('get_project 01')
    var project = $.getenv( "BOM_PROJECT_NAME" );
    // alert('get_project 02')
	if(project == null){
        // alert('get_project 03')
		var ui = config_prompt();
        // alert('get_project 04')
        var index = ui.show();
        // alert('get_project 05')
        var project_list = get_config_options(false);
        // alert('get_project 06')
        return project_list[index];
	} else {
        // alert('get_project 07')
        return project;
    }
}

function get_config_options(hide_archived){
    // alert('get_config_options 01')
    var config_folder = Folder('T:/_Pipeline/cobopipe_v02-001/Configs');
    // alert('get_config_options 02')
    var files = config_folder.getFiles();
    // alert('get_config_options 03')
    var projects = [];
    // alert('get_config_options 04')

    for(var i in files){
        if(files[i].fsName.substr(-5, 5) == '.json'){
            filename = files[i].fsName.split('\\')[files[i].fsName.split('\\').length-1];
            if(filename.substr(0, 7) == 'Config_'){
                filename = filename.replace('Config_', '').replace('.json', '');
                projects.push(filename);
            }
        }
    }
    // alert('get_config_options 05')
    
    var archived_projects = loadJson('T:/_Pipeline/cobopipe_v02-001/Configs/archivesProjects.json');
    // alert('get_config_options 06')
    if(hide_archived == true){
        // alert('get_config_options 07')
        var non_archived_projects = [];
        // alert('get_config_options 08')
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
        // alert('get_config_options 09')
        return non_archived_projects;
    } else {
        // alert('get_config_options 10')
        return projects;
    }
}

function loadJson(path){
    // alert('loadJson 01')
    var scriptFile = File(path);
    // alert('loadJson 02')
    scriptFile.open('r');
    // alert('loadJson 03')
    var data = scriptFile.read();
    // alert('loadJson 04')
    scriptFile.close();
    // alert('loadJson 05')
    return JSON.parse(data);
}