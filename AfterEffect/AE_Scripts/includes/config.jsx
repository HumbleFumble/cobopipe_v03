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
    dropdown.removeAll();
    var projects = get_config_options(hide_archived);
    for(var i in projects){
        dropdown.add("item", projects[i]);
    }
}

function get_config(){
	var project = get_project();
    var pipeline_path = get_pipeline_path();
    var config_path = pipeline_path + '/Configs/Config_' + project + '.json';
    return loadJson(config_path);
}

function get_project(){
    var project = $.getenv( "BOM_PROJECT_NAME" );
	if(project == null){
		var ui = config_prompt();
        var index = ui.show();
        var project_list = get_config_options(false);
        var project = project_list[index];
        $.setenv( "BOM_PROJECT_NAME", project);
        return project_list[index];
	} else {
        return project;
    }
}

function get_pipeline_path(){
    var path = $.getenv("BOM_PIPE_PATH")
    if(!path){
        path = "T:/_Pipeline/cobopipe_v02-001"
    }
    return path
}

function get_config_options(hide_archived){
    var pipeline_path = get_pipeline_path();
    var config_folder = Folder(pipeline_path + '/Configs');
    var files = config_folder.getFiles();
    var projects = [];

    for(var i in files){
        if(files[i].fsName != undefined){
            if(files[i].fsName.substr(-5, 5) == '.json'){
                filename = files[i].fsName.split('\\')[files[i].fsName.split('\\').length-1];
                if(filename.substr(0, 7) == 'Config_'){
                    filename = filename.replace('Config_', '').replace('.json', '');
                    projects.push(filename);
                }
            }
        }
    }
    
    var archived_projects = loadJson(pipeline_path + '/Configs/archivesProjects.json');
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

function log(msg){
$.writeln(msg)
}

function unpack_config(object){
    var update_object = {};

    for(key in object){
        if(typeof object[key] === 'object' && !(object[key] instanceof Array) && object[key] != null){
            var output = unpack_config(object[key]);
            for(output_key in output){
                if(!(output_key in update_object)){
                    update_object[output_key] = output[output_key]
                }
            }
        } else {
            update_object[key] = object[key]
        }
    }
    return update_object;
}

function pack_config(ref_object, object){

    for(key in ref_object){
        if(typeof ref_object[key] === 'object' && !(ref_object[key] instanceof Array) && ref_object[key] != null){
            var output = pack_config(ref_object[key], object);
            for(output_key in output){
                if(output_key in ref_object){
                    ref_object[key] = output[output_key]
                }
            }
        } else {
            ref_object[key] = object[key] 
        }


    }
    
    return ref_object;
}

function process_config(object){
    var update_object = unpack_config(object)

    var number_of_updates = 1
    while(number_of_updates > 0){
        number_of_updates = 0
        for(key in update_object){
            if(typeof update_object[key] === 'string'){
                if(update_object[key].indexOf('<') > -1){
                    var start_index = update_object[key].indexOf('<') + 1 
                    var end_index = update_object[key].indexOf('>') - 1
                    var replace_key = update_object[key].substr(start_index, end_index)

                    if(replace_key in update_object){
                        update_object[key] = update_object[key].replace("<" + replace_key + ">", update_object[replace_key])
                        number_of_updates = ++number_of_updates
                    }
                }
            }
        }
    }

    return pack_config(object, update_object)
}


function reg_replace(path){
    //returns a list of strings found between < >, including the < >
    //log("replace" + path);
    var t = new RegExp('\<(.*?)\>','g')
    var m = path.match(t,path)
    if(!m){
        return []
        }
    return m
}

function clean_key_func(key){
     key = key.replace("<","")
     key = key.replace(">","")
    return key
    }

function process_path(path,info_dict){
    var no_keys = [];
    var key_list = reg_replace(path)
    for(i=0;i<key_list.length;i++){
         var c_key = key_list[i]
         var clean_key = clean_key_func(c_key)
         if(clean_key in info_dict){
             path = path.replace(c_key,info_dict[clean_key])
             }
         else{
             no_keys.push(c_key)
             }
         }
     var more_keys = reg_replace(path);
     if(more_keys.length!=no_keys.length){
         path = process_path(info_dict,path)
     }
     return path
    }