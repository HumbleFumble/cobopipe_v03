#target AfterEffects
//#include T:/_Pipeline/cobopipe_v02-001/AfterEffect/include/config_functions.js
#include C:/Users/cg/PycharmProjects/cobopipe_v02-001/AfterEffect/includes/config_functions.jsx
//TODO Place footage it can't replace in the old-footage folder, instead of deleting it.
cc = getConfig()
var base_project_path = dict_replace(cc.project_paths,cc.project_paths["film_path"])
var template_path = base_project_path + "/_Comp_Templates/_AE_CharTemplates";


function GetCurrentSelectedFootage(){
    var cur_selection = app.project.selection;
    if(cur_selection != ""){
        for(var s=(cur_selection.length-1); s>=0;s--){
            if(cur_selection[s] instanceof FootageItem){
                }else{
                    to_remove = cur_selection.splice(s,1);
                    }
            }
        return cur_selection
        }else{
    return false
    }
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
    var used_footage_list =[]
    var old_footage_folder = null;
    if(footage_folder){
        for(f=1;f<=footage_folder.numItems;f++){
            temp_name = footage_folder.items[f].name;
            used_footage_list.push(footage_folder.items[f]);
            if(temp_name.indexOf("{")>-1){
                push_name = temp_name.split("{")[0];
                }
            if(temp_name.indexOf("[")>-1){
                push_name = temp_name.split("[")[0];
                }
            footage_list.push(push_name);
        }
        
        for(x=orig_folder.numItems;x>=1;x--){
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
                used_footage_list.splice(find_index,1)
                }
        }
    }
    if(used_footage_list.length >0){
        if(!old_footage_folder){
            old_footage_folder = FindFolderByName("Old_Footage")
            }
            for(var y=(used_footage_list.length-1 );y>=0;y--){
               used_footage_list[y].parentFolder = old_footage_folder
               to_alert = to_alert + "Couldn't find " + used_footage_list[y].name + " used anywhere. Placed it in Old_Footage folder."
                }
        }
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


function FindFolderByName(name){
    var project_content = app.project.items;
    var my_folder = "";
    for(var p =project_content.length;p>=1;p--){
        var cur_content = project_content[p];
        if(cur_content instanceof FolderItem){
            var _name = cur_content.name;
            if(_name == name){
                my_folder = cur_content;
                return cur_content
            }
        }
    }
    return project_content.addFolder(name);
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

function ImportMulti(){
    var footage_selection = GetCurrentSelectedFootage();
    if(footage_selection && footage_selection!=""){
        var footage_folder = FindFolderByName("Footage")
        var f_list = FindInFolder(template_path);
        for(var i=0;i<footage_selection.length;i++){
          var cur_footage = footage_selection[i];
          var cur_name = cur_footage.name.split("_")[0]
          $.writeln(cur_name);
          if(CheckForMatch(cur_name,f_list)){
                var selection_path = template_path +"/" + String(cur_name) + "_CharTemplate.aep"
                var imported_folder = ImportProject(selection_path)
                ReplaceMoveDelete(imported_folder,footage_folder)
            }
          }
        }
    }
function CheckForMatch(name, list){
     for(var j=0;j<list.length;j++){
            if(name == list[j]){
                $.writeln("Found " + name);
                return true
                }
            }
        return false
    }
function RefreshDropDown(folder_path){
    var dd = cur_win.grp.panel_group.drop_group.drop_down
    var footage_selection = GetCurrentSelectedFootage();
    if(footage_selection && footage_selection!=""){
        var cur_selection = footage_selection[0].name.split("_")[0];
    }else{
        var cur_selection = String(dd.selection);
    }
    var f_list = FindInFolder(folder_path);
    dd.removeAll();
    for(var x = 0;x<f_list.length;x ++){
        dd.add("item",f_list[x])
    }

    if(dd.find(cur_selection) &&  cur_selection!=null){
            dd.selection=dd.find(cur_selection)
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
    drop_group: Group{orientation: 'row',\
    drop_down: DropDownList { alignment:['fill','top'],preferredSize: ['200','20'] }, help_button: Button{text:'?',preferredSize: ['20','27']}\
    },\
    bttn_group: Group{orientation: 'column', alignChildren:['fill','top']\
    refresh_bttn: Button{text: 'Refresh'},import_single_button: Button{text:'Import from DropDown'}, \
    import_multi_button: Button{text:'Import from Footage Selected'}\
    }}}\
    ")
    var footage_folder = FindFolderByName("Footage")

    dialog.grp.panel_group.bttn_group.import_single_button.onClick = function(){
        if(dialog.grp.panel_group.drop_group.drop_down.selection){
            var selection_path = template_path +"/" + String(dialog.grp.panel_group.drop_group.drop_down.selection) + "_CharTemplate.aep"
            var imported_folder = ImportProject(selection_path)
            ReplaceMoveDelete(imported_folder,footage_folder)
            }
    }
    dialog.grp.panel_group.bttn_group.import_multi_button.onClick = function(){
        ImportMulti()
    }
    dialog.grp.panel_group.bttn_group.refresh_bttn.onClick = function(){

        RefreshDropDown(template_path)
    }
    dialog.grp.panel_group.drop_group.help_button.onClick = function(){
        alert("This is a UI for importing premade Character Templates\
        \nbased on either the selection of footage in the project view OR the set name in the drop-down.\
        \nSelect only 1 footage item and run refresh to update the drop-down with the template based on that name.\
        \nIf the naming is weird or you need to be more picky, use the drop-down to set the goal template and hit import.\
        \n Otherwise select all the base footage passes you want and hit import from footage.\
        \nTry to only select the footage with the simple character name and not extra passes.\
        \nThe template import only replaces footage/passes from the template that it can match to footage found in the current scene.")
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
