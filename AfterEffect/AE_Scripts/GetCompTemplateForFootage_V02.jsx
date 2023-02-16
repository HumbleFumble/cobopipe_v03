#target AfterEffects
//#include T:/_Pipeline/cobopipe_v02-001/AfterEffect/include/config_functions.js
#include C:/Users/cg/PycharmProjects/cobopipe_v02-001/AfterEffect/includes/config_functions.jsx

cc = getConfig()
var base_project_path = dict_replace(cc.project_paths,cc.project_paths["film_path"])

function Run(){
    cur_item = app.project.selection[0];
    var footage_folder = cur_item.parentFolder;
    
    imported_folder = ImportTemplateFromName(cur_item.name);
    if(imported_folder){
        ReplaceMoveDelete(imported_folder,footage_folder);
        }
    }

function CreateDropDownPopup(dd_list){
    var ddWin = new Window("palette","PickTemplate",undefined);
    }

function ImportTemplateFromName(cur_name){
        var template_path = base_project_path + "/_Comp_Templates/_AE_CharTemplates";
        precomp_folder = new Folder(template_path);
        var template_aeps = precomp_folder.getFiles('*_CharTemplate.aep');
        for(t=0;t<template_aeps.length;t++){
            cur_template_name = template_aeps[t].name.split("_")[0];
            
            if(cur_name.search(cur_template_name)>-1){
                //TODO Make a drop down with all the possibe options
                var project_item = ImportProject(template_aeps[t])
                return project_item
                }
            }
        alert("Can't find any template for " + cur_name);
        return null;
        }

function ReplaceMoveDelete(cur_folder,orig_folder){
    var footage_folder = null;
    to_alert = "REPLACING:\n";
    for(var i=cur_folder.numItems;i>0;i--){
        if(cur_folder.items[i].name.toLowerCase()=="footage"){
            footage_folder = cur_folder.items[i];
            }else{
                cur_folder.items[i].parentFolder = app.project.rootFolder;
                }
        }
    var footage_list = [];
    if(footage_folder){
        for(f=1;f<=footage_folder.numItems;f++){
            temp_name = footage_folder.items[f].name;
            if(temp_name.indexOf("{")>-1){
                push_name = temp_name.split("{")[0];
                }
            if(temp_name.indexOf("[")>-1){
                push_name = temp_name.split("[")[0];
                }
            footage_list.push(push_name);
        }
        for(x=1;x<=orig_folder.numItems;x++){
            cur_name = orig_folder.items[x].name;
            log(cur_name);
            var split_name ="";
            if(cur_name.indexOf("{")>-1){
                split_name = cur_name.split("{")[0];
                }
            if(cur_name.indexOf("[")>-1){
                split_name = cur_name.split("[")[0];
                }
            find_index = footage_list.join(",").indexOf(split_name);
            if(find_index>-1){
                replace_alert = ReplaceInComps(footage_folder.items[find_index+1],orig_folder.items[x])
                to_alert = to_alert + replace_alert;
                }
        }
    }//if footage folder
    alert(to_alert);
    cur_folder.remove();
}

function ReplaceInComps(old_footage,new_footage){

    in_comps = old_footage.usedIn;
    //find footage in comps and replace it
    print_string = "";
    for(var i=0;i<in_comps.length;i++){
        for(var i_c=1;i_c <= in_comps[i].numLayers;i_c++){
            //if(cur_item[0].source == )
            cur_layer = in_comps[i].layers[i_c];
            cur_source = in_comps[i].layers[i_c].source;
            if(cur_source == old_footage){
                print_string = print_string + "FOUND: "+ in_comps[i].layers[i_c].name +" in "+ in_comps[i].name + "\n";
                cur_layer.replaceSource(new_footage,false);
                }// if statement
            }// layer in comp for-loop
        }// in comp for-loop
    return print_string
    //app.project.item(index).usedIn
} //function

function ImportProject(my_path){
	my_footage = new File(my_path);
	import_options = new ImportOptions(my_footage);
	import_options.importAs = ImportAsType.PROJECT;
	//import_options.sequence = sequence_boolean; Not used in this kind of import
	project_item = app.project.importFile(import_options);
	//project_item.mainSource.conformFrameRate = 25.00; Not needed.
	return project_item
	}


function FindFootageFolder(){
    var project_content = app.project.items;
    var my_folder = "";
    for(var p =project_content.length;p>=1;p--){
        var cur_content = project_content[p];
        if(cur_content instanceof FolderItem){
            var _name = cur_content.name;
            if(_name == "Footage"){
                my_folder = cur_content;  
            }
        }
    }
    if (my_folder != ""){
        my_folder.name = "Old_Footage";
        }
    return project_content.addFolder("Footage");
}
Run();
