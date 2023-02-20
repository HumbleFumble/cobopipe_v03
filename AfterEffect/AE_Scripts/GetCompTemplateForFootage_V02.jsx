#target AfterEffects
//#include T:/_Pipeline/cobopipe_v02-001/AfterEffect/include/config_functions.js
#include C:/Users/cg/PycharmProjects/cobopipe_v02-001/AfterEffect/includes/config_functions.jsx

cc = getConfig()
var base_project_path = dict_replace(cc.project_paths,cc.project_paths["film_path"])
var template_path = base_project_path + "/_Comp_Templates/_AE_CharTemplates";


function Run(){
    var cur_item = GetCurrentSelectedFootage()
    var footage_folder = cur_item.parentFolder;
    imported_folder = ImportTemplateFromFootageName(cur_item.name);
    if(imported_folder){
        ReplaceMoveDelete(imported_folder,footage_folder);
        }
    }

function GetCurrentSelectedFootage(){
    var cur_item = app.project.selection;
    //var footage_folder = cur_item.parentFolder;
    if(cur_item){
        return cur_item[0]
        }else{
    return false
    }
}

function ImportTemplateFromFootageName(cur_name){
        precomp_folder = new Folder(template_path);
        var template_aeps = precomp_folder.getFiles('*_CharTemplate.aep');
        for(t=0;t<template_aeps.length;t++){
            cur_template_name = template_aeps[t].name.split("_")[0];

            if(cur_name.search(cur_template_name)>-1){
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
                return cur_content
            }
        }
    }
    return project_content.addFolder("Footage");
}

function FindInFolder(folder_path){
    var script_folder = new Folder(folder_path);
	var folder_files = script_folder.getFiles('*CharTemplate.aep');
	var folder_files = folder_files.sort();
	var script_files = [];
	for(var f = 0;f<folder_files.length;f ++){
		var cur_name = folder_files[f].name.split("_CharTemplate")[0];
		script_files.push(cur_name);
		}
	return script_files;
}


function RefreshDropDown(folder_path){
    var dd = cur_win.grp.panel_group.drop_down
    var footage_selection = GetCurrentSelectedFootage();
    if(!footage_selection){
        var cur_selection = dd.selection;
        }else{
            cur_selection = footage_selection.name.split("_")[0];
        }
    var f_list = FindInFolder(folder_path);
    dd.removeAll();
    for(var x = 0;x<f_list.length;x ++){
        dd.add("item",f_list[x])
    }

    if(dd.find(cur_selection) && cur_selectoion !=null){
        dd.selection=cur_selection
        }else{
            dd.selection = dd.items[0]
            }
    }


var cur_win = (function(thisObj){
    var isPanel = thisObj instanceof Panel; // true or false
    var dialog = isPanel  ? thisObj : new Window("window", "CharTemplateImport");

    dialog.alignChildren = 'left'
    dialog.alignment = ['top','fill']

    dialog.grp = dialog.add("Group{orientation:'column',alignment:['fill','fill'],\
    panel_group: Group{orientation: 'column',\
    drop_down: DropDownList { alignment:['fill','top'],preferredSize: ['200','20'] },\
    bttn_group: Group{orientation: 'row', alignChildren:['fill','top']\
    run_button: Button{text:'Run'}, refresh_bttn: Button{text: 'Refresh'}\
    help_button: Button{text:'?'},\
    }}}\
    ")
    var footage_folder = FindFootageFolder()

    dialog.grp.panel_group.bttn_group.run_button.onClick = function(){
        if(dialog.grp.panel_group.drop_down.selection){
            var selection_path = template_path +"/" + String(dialog.grp.panel_group.drop_down.selection) + "_CharTemplate.aep"
            var imported_folder = ImportProject(selection_path)
            
            ReplaceMoveDelete(imported_folder,footage_folder)
            }
    }
    dialog.grp.panel_group.bttn_group.refresh_bttn.onClick = function(){

        RefreshDropDown(template_path)
    }
    dialog.grp.panel_group.bttn_group.help_button.onClick = function(){
        alert("This is a UI for importing premade Character Templates\
        \nbased on the selection of footage in the project view.\
        \nSelect only one footage item and run the script.\
        \nClick Run to import the selected PreComp from the dropdown.")
    }

    
    if (!isPanel) {
      // if it's a window
      dialog.show();
    } else {
      // if it's a panel
      dialog.layout.layout(true);
      dialog.layout.resize();
      }

    return dialog
})(this);


RefreshDropDown(template_path)
