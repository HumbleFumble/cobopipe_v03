#target.aftereffects
#include T:/_Pipeline/cobopipe_v02-001/AfterEffect/includes/config_functions.jsx
//include C:/Users/cg/PycharmProjects/cobopipe_v02-001/AfterEffect/includes/config_functions.jsx

cc = getConfig()
var pipepath = cc.project_paths["python_path"]
//var pipepath = "C:/Users/cg/PycharmProjects/cobopipe_v02-001/AfterEffect/"
var python_script_path = pipepath + "AfterEffect/ExportAsProject_Python.py";

function Export(orig_file_path,export_path){
    log(orig_file_path)
    log(export_path)
    var cur_selection = app.project.selection;
    if(cur_selection){
        log(cur_selection)
        var list_of_ids = ReturnIdList(cur_selection);
        var add_args = python_script_path + " " + orig_file_path + " " + export_path +" "+ String(list_of_ids);
         $.writeln(add_args)
        result = system.callSystem("python " + add_args)
        $.writeln(result)
        }
    }
function log(message){
    $.writeln(message)
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
    run_button: Button{text:'Run'},\
    help_button: Button{text:'?'},\
    }}}\
    ")
    
     dialog.grp.panel_group.file_panel.browse_button.onClick=function(){
        if(app.settings.haveSetting("ExportAsProject","StartFolder")){
            var start_folder = String(app.settings.getSetting("ExportAsProject","StartFolder")) + "/ExportAsProject.aep"
            }
        else{
            var start_folder = "P:/930462_HOJ_Project/Production/ExportAsProject.aep";
        }
        var save_file = new File(start_folder).saveDlg("Save As", "AEP:*.aep;*.aep,All files:*.*", false);
        if(save_file != null){
            app.settings.saveSetting("ExportAsProject","StartFolder", String(save_file.path));
            dialog.grp.panel_group.file_panel.file_et.text = save_file.fullName;
            return;
            }
    }

    dialog.grp.panel_group.bttn_panel.run_button.onClick = function(){
        Export(app.project.file.fullName,dialog.grp.panel_group.file_panel.file_et.text)
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