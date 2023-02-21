function Export(file_path){
    
    var cur_selection = app.project.selection;
    if(cur_selection){
        log(cur_selection)
        var list_of_ids = ReturnIdList(cur_selection);
        python_proc  = "C:\\Users\\cg\\PycharmProjects\\cobopipe_v02-001\\AfterEffect\\ExportAsProject_Python.py"
        add_args = python_proc + " " + scene_name + " " + String(list_of_ids);
         $.writeln(add_args)
        result = system.callSystem("python " + add_args)
        $.writeln(result)
        //var new_project = new File(file_path);
//        app.project.reduceProject(cur_comp);
//        app.project.save(new_project);
        }
    }

function ReturnIdList(list){
    var return_list = []
    for(var l =0;l <list.length;l++){
        return_list.push(list[l].id)
        }
    return return_list
    }

var cur_win = (function(thisObj){
    var isPanel = thisObj instanceof Panel; // true or false
    var dialog = isPanel  ? thisObj : new Window("window", "ExportAsProject");

    dialog.alignChildren = 'left'
    dialog.alignment = ['top','fill']

    dialog.grp = dialog.add("Group{orientation:'column',alignment:['fill','fill'],\
    panel_group: Group{orientation: 'Column',\
                    file_panel: Panel {text: 'Pick Save Location:', \
                    alignment:['fill','top'], alignChildren: 'left',\
                    file_info_st: StaticText {text:'File Location:',preferredSize: [215,22], justify:'left' }, \
                    file_et: EditText{text:'', preferredSize: [200,22]},\
                    browse_button: Button{ text: 'Browse to file'}, \
                    },\
    bttn_panel: Panel{text: 'Actions',orientation: 'row', alignChildren:['fill','top']\
    run_button: Button{text:'Run'}, refresh_bttn: Button{text: 'Refresh'}\
    help_button: Button{text:'?'},\
    }}}\
    ")
    
     dialog.grp.panel_group.file_panel.browse_button.onClick=function(){
        var start_folder = "P:/930462_HOJ_Project/Production/AE_Export.aep";
        var save_file = new File(start_folder).saveDlg("Save As", "AEP:*.aep;*.aep,All files:*.*", false);
        if(save_file != null){
            dialog.grp.panel_group.file_panel.file_et.text = save_file.fullName;
            return;
            }
    }
    
    dialog.grp.panel_group.bttn_panel.run_button.onClick = function(){
        alert("Running something something")
    }
    dialog.grp.panel_group.bttn_panel.refresh_bttn.onClick = function(){
        folder_path = ""
    }
    dialog.grp.panel_group.bttn_panel.help_button.onClick = function(){
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