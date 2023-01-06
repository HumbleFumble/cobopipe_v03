#target.aftereffects

//Makes a small UI with all the scripts in the scripts folder;
//var inputFolder = Folder.selectDialog("Please select the folder with Files to process");

function FindAndAdd(){
	//var script_folder = new Folder("P:/930371_Next_Door_Spy_Produktion/SharedFiles/Scripts/AE_Scripts/");
    var script_folder = new Folder(cur_win.grp.folder_group.et_folder.text);
	var folder_files = script_folder.getFiles('*.jsx');
	var folder_files = folder_files.sort();
	var script_files = [];
	for(var f = 0;f<folder_files.length;f ++){
		cur_object = folder_files[f];
		script_files.push(cur_object.name);
		}
	return script_files;
}

function RunScript(){
	//var script_folder = "#include P:/930371_Next_Door_Spy_Produktion/SharedFiles/Scripts/AE_Scripts/";
    var script_folder = "#include "+cur_win.grp.folder_group.et_folder.text +"/";
	var cur_script_name = cur_win.grp.script_group.script_list.selection;
	if(cur_script_name != null){
		cur_script_name = cur_script_name.toString();
		var cur_script = script_folder + cur_script_name;
		var run_script = eval(cur_script);
		}
	}

function FillList(){
	var remove = cur_win.grp.script_group.script_list.removeAll();
	var cur_script_list = FindAndAdd();
	for(var a = 0;a<cur_script_list.length;a++){
		cur_item = cur_script_list[a].toString();
		cur_win.grp.script_group.script_list.add('item',cur_item);
		}
}
function PickFolder(){
    var inputFolder = new Folder(cur_win.grp.folder_group.et_folder.text).selectDlg("Please select the folder with Files to process");
    if(inputFolder != null){
        cur_win.grp.folder_group.et_folder.text = inputFolder;
        setting_save("RunScriptUI", "win.children[0].children[0].children[0].text", cur_win.grp.folder_group.et_folder.text);
        FillList();
        }
    }

/*
var paletteRef = (thisObj instanceof Panel) ? thisObj : new Window("palette", "Run Scripts UI",undefined, {resizeable:true});	
	paletteRef.name = "Run_Scripts_UI";
	if (paletteRef != null)
	{
		
		paletteRef.grp = paletteRef.add(resourcei);
		paletteRef.layout.layout(true);
		*/
function setting_save(settingBin,settingName,settingValue){
	app.settings.saveSetting(settingBin,settingName,settingValue);
}

function setting_load(settingBin,settingName){
	if(app.settings.haveSetting(settingBin,settingName)){
	    var value =  app.settings.getSetting(settingBin,settingName);
	} else {
		var value =  true;
	}
	return value;
}


function buildUI(thisObj){
	var win = (thisObj instanceof Panel) ? thisObj : new Window("palette", "Run Scripts UI", undefined,{resizeable:true});
	if(win != null){
		var window_text = "Group{orientation:'column',alignment:['fill','fill'],\
		folder_group: Group {orientation: 'row', et_folder: EditText{text: 'T:/_Pipeline/cobopipe-v02-001/AfterEffect/AE_Scripts', preferredSize: ['175','20']}, pick_folder_button: Button{text:'Pick Folder'} }\
		script_group: Group{orientation: 'row', script_list: ListBox{text: 'testing', preferredSize:['250','350'],} }, \
		button_group: Group {orientation: 'row', run_button: Button{text:'Run'}, import_button: Button{text: 'Refresh'} }\
		}";
		
		win.grp = win.add(window_text);
		//Don't know what this does. But it needs it to run :/
		win.layout.layout(true);
		
		win.grp.script_group.script_list.onDoubleClick = RunScript;
		win.grp.button_group.run_button.onClick = RunScript;
		win.grp.button_group.import_button.onClick = FillList;
         win.grp.folder_group.pick_folder_button.onClick = PickFolder;
        var new_set = setting_load("RunScriptUI", "win.children[0].children[0].children[0].text");
        if(new_set != true){
            win.children[0].children[0].children[0].text = new_set;
            }
		return win;
	}
	
}
var cur_win = buildUI(this);
FillList();


/*
//OLD UI for running it without the ui_panel 
var window_text = "palette{text: 'Run Script', resizeable: true,\
script_group: Group{orientation: 'row', script_list: ListBox{text: 'testing', preferredSize:['250','300']} }, \
button_group: Group {orientation: 'row', import_button: Button{text: 'Refresh'} }\
}" ;

var cur_win= new Window(window_text);
//cur_win.show();
cur_win.script_group.script_list.onDoubleClick = RunScript;
cur_win.button_group.import_button.onClick = FillList;
FillList();
*/