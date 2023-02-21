function FindInFolder(folder_path){
    var script_folder = new Folder(folder_path);
	var folder_files = script_folder.getFiles('*CharacterTemplate.aep');
	var folder_files = folder_files.sort();
	var script_files = [];
	for(var f = 0;f<folder_files.length;f ++){
		cur_object = folder_files[f];
		script_files.push(cur_object.name);
		}
	return script_files;
}

function FindCurrentFootageSelected(){
    return false
    }

function RefreshDropDown(folder_path){
    var dd = cur_win.grp.panel_group.drop_down
    var footage_selection = FindCurrentFootageSelected();
    if(!footage_selection){
        var cur_selection = dd.selection;
        }
    var f_list = FindInFolder (folder_path);
    dd.removeAll()
    for(var f = 0;f<f_list.length;f ++){
        dd.add("item",f_list[f])
    }
    if(dd.find(cur_selection && cur_selectoion !=null)){
        dd.selection=cur_selection
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

    dialog.grp.panel_group.drop_down.add("item", "new");
    //$.writeln(dialog.grp.panel_group.drop_down.selection)
    //$.writeln(dialog.grp.panel_group.drop_down.find("new"))
    dialog.grp.panel_group.drop_down.selection="new"
    dialog.grp.panel_group.bttn_group.run_button.onClick = function(){
        alert("Running something something")
    }
    dialog.grp.panel_group.bttn_group.refresh_bttn.onClick = function(){
        folder_path = ""
        RefreshDropDown(folder_path)
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