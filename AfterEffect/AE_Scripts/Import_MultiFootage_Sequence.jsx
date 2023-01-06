#target.aftereffects


//TODO Make Import for whole Episode
//TODO Make Shot folder
//TODO Make Update function where it adds new footage stacks found to shot

function ImportShot(){	
	my_proj = app.project;
	//base_path = "P:/930431_SprinterGalore_Animated/Pilot_2018/Scenes/_Render/Sh260/";
	folder_path = import_UI.base_panel.path_et.text;
	ep = GetEpisode();
    seq = GetSeq();
    shot = GetShot();
	base_path = folder_path +"/" +ep + "/" +  ep + "_" +seq + "/" + ep + "_" + seq + "_" + shot + "/Passes/";	
    var shot_name = ep +"_" + seq+"_" + shot;
    var output = ImportShotFootage(base_path,shot_name);
    if(output){
        alert(output);
        }
}
function ImportSeq(){
    folder_path = import_UI.base_panel.path_et.text;
	ep = GetEpisode();
    seq = GetSeq();
    
    var shot_list =  FindShotsInSequence(ep,seq);

    var output_list = [];
    for(s=0; s <shot_list.length;s++){
        shot = shot_list[s];
        shot_path = folder_path +"/" +ep + "/" +  ep + "_" +seq + "/" +shot + "/Passes/";
        shot_output = ImportShotFootage(shot_path,shot);
        if(shot_output){
            output_list.push(shot + ": " +shot_output+ "\n")
            }
        }
    alert(output_list);

    }

function ImportShotFootage(base_path,shot_name){
    var passes_folder = new Folder(base_path);
    if (passes_folder.exists){
        var footage_folder = FindFootageFolder(shot_name);
        var shot_footage_in_scene = FindSourceOfFootageUnderParent(footage_folder,".png");
        var my_footage_list = passes_folder.getFiles('*001.png');
        var new_footage = false;
        for(i=0; i <my_footage_list.length;i++){
                if(shot_footage_in_scene.toString().indexOf(my_footage_list[i].fullName)==-1){
                    var cur_file = my_footage_list[i];
                    cur_footage_item = ImportFootage(my_footage_list[i]);
                    cur_footage_item.parentFolder = footage_folder;
                    new_footage = true;
                }
            }
        }else{
            return("Can't find footage or passes folder");
        }
    if(new_footage){
        return("Found New Footage");
        }
    return false;
    }

function FindShotsInSequence(E,SQ){
	//Check for folders with shot numbers between the start and end number. return a list of those numbers.
    folder_path = import_UI.base_panel.path_et.text;
	var cur_folder_path =folder_path +"/"+ E + "/" + E +"_" + SQ + "/";
	var folder_object = new Folder(cur_folder_path);
	var cur_folder_content = folder_object.getFiles();
	var number_list = [];
	if(cur_folder_content){
		var sorted_content = cur_folder_content.sort();
		for(var f =0; f<sorted_content.length;f++){
            cur_content = sorted_content[f];
            //cur_path = cur_folder_path + cur_content.toString()
            if(cur_content.toString().indexOf(E + "_" + SQ + "_SH") > -1){
                cur_name = (cur_content.toString()).split("/");
                cur_name = cur_name[cur_name.length-1];
                number_list.push(cur_name);
                }
			}        
		return number_list;
    }else{
        
        return null;
        }
}


function ImportFootage(target_file){
        //file_path = base_path + "/" + target_file.name;
        //my_footage = new File(file_path);
        my_proj = app.project;
        var import_options = new ImportOptions(target_file);
        import_options.sequence = true;
        var project_item = my_proj.importFile(import_options);
        project_item.mainSource.conformFrameRate = 25.00;
        return project_item;
}

function FindSourceOfFootageUnderParent(cur_parent,extension){//Find the footage items in the current project that has a source that ends with 'extension'
    var item_footage_list = [];
    var parent_content = cur_parent.items;
    for(var p =parent_content.length;p>=1;p--){
        var cur_content = parent_content[p];
        if(cur_content instanceof FootageItem){
            if(cur_content.mainSource instanceof FileSource){
                var cur_name = cur_content.mainSource.file.name;
                if( cur_name.search(extension)>=0 ){
                    var old_footage = cur_content.mainSource.file.fullName;
                    var old_name = cur_content.name;
                    item_footage_list.push(old_footage);
                    }
                }
        }
    }
    return item_footage_list
}

function CheckForFolder(){
    var ep = GetEpisode();
    var seq = GetSeq();
    var shot = GetShot();
    var shot_name = ep +"_" + seq+"_" + shot;
    my_folder = FindFootageFolder(shot_name);
    alert(my_folder);
    }
function FindFootageFolder(shot_name){
    var project_content = app.project.items;
    var my_folder = "";
    var old_folder_list = [];
    var old_folder = "";
    for(var p =project_content.length;p>=1;p--){
        var cur_content = project_content[p];
        if(cur_content instanceof FolderItem){
            var _name = cur_content.name;
            if(_name == shot_name + "_Footage"){
                my_folder = cur_content;  
            }
        }
    }
    if (my_folder == ""){
        my_folder = project_content.addFolder(shot_name + "_Footage");
        }
    return my_folder;
}


function GetEpisode(){
	var ep = import_UI.shot_panel.ep_et.text;
    
	var e_number = parseInt(ep,10);
	var E = "E"+ Pad(e_number,2);
	return E
	}

function GetSeq(){
	var  seq = import_UI.shot_panel.sq_et.text;
	var seq_number = parseInt(seq,10);
	var seq = "SQ" + Pad(seq_number,3);
	return seq
	}

function GetShot(){
	var shot = import_UI.shot_panel.shot_et.text;
	var shot_number = parseInt(shot,10);
	var shot = "SH" + Pad(shot_number,3);
	return shot
	}



function Pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function SaveCompFile(){
    folder_path = import_UI.base_panel.path_et.text;
	ep = GetEpisode();
    seq = GetSeq();
    shot = GetShot();
	base_path = folder_path +"/" +ep + "/" +  ep + "_" +seq + "/" + ep + "_" + seq + "_" + shot + "/03_Comp/";
	
	var comp_folder = new Folder(base_path);
	var comp_file = new File(comp_folder.toString() + "/" + ep + "_"+ seq + "_" + shot + "_Precomp.aep");
	var my_confirm = true;
	if(comp_file.exists){
		my_confirm = confirm ("The file already exists, do you want save\nThis file as "+ shot + "_Precomp ?", true, "OverWrite Comp?");
		}
	if(my_confirm){	
		if(!comp_folder.exists){comp_folder.create();
			}
		app.project.save(comp_file);
		}
	}

function PickFolder(){
    var old_input = new Folder(import_UI.base_panel.path_et.text);
    var inputFolder =  new Folder(import_UI.base_panel.path_et.text).selectDlg("Please select the folder");
    if(inputFolder != null){
        import_UI.base_panel.path_et.text = inputFolder;
        setting_save("ImportMultiFolder", "win.children[0].children[1].text", import_UI.base_panel.path_et.text);
        }
    }


function setting_save(settingBin,settingName,settingValue){
	app.settings.saveSetting(settingBin,settingName,settingValue);
}

function setting_load(settingBin,settingName){
	if(app.settings.haveSetting(settingBin,settingName)){
	    var value =  app.settings.getSetting(settingBin,settingName);
	} else {
		var value =  false;
	}
	return value;
}



function SaveChildren(base_name, cur_win, cur_parent){
	for(var i = 0;i<cur_win.children.length;i++){
		cur_child = cur_win.children[i];
		child_parent = cur_parent +"children["+i+"].";
		
		if(cur_child.type == 'edittext'){
			cur_value_string = child_parent + "text"
			setting_save(base_name,cur_value_string, cur_child.text);
			}
		
		/* For drop down list. Not sure if it will work for how i've setup export import scripts.
		if(cur_child.type =='dropdownlist'){
			for(var a=0;a< cur_child.items.length;a++){
				if(cur_child.items[a].selected == true){
					cur_value_string = child_parent + "items["+a+"].selected"
					setting_save(base_name,cur_value_string,"on");
				} else {
					setting_save(base_name,cur_value_string,"off");
				}
			}
		*/
	
		if(cur_child.type == 'panel'){
			SaveChildren(base_name,cur_child,child_parent);
		}
		if(cur_child.type =='group'){
			SaveChildren(base_name,cur_child,child_parent);
			}
	}
}

function LoadChildren(base_name, cur_win, cur_parent){
	for(var i = 0;i<cur_win.children.length;i++){
		cur_child = cur_win.children[i];
		child_parent = cur_parent +"children["+i+"].";

		if(cur_child.type == 'edittext'){
			cur_value_string = child_parent + "text"
			cur_setting = setting_load(base_name,cur_value_string);
			if(cur_setting!="false"&&cur_setting!=false&&cur_setting!=NaN){
				cur_child.text = cur_setting;
				}
			}

		if(cur_child.type == 'panel'){
			LoadChildren(base_name,cur_child,child_parent);
		}
		if(cur_child.type =='group'){
			LoadChildren(base_name,cur_child,child_parent);
			}	
	}
}


function SaveWindow(winRef){
	var winName = winRef.text;
	setting_save(winName,"frameLocation","["+ winRef.frameLocation[0]+","+winRef.frameLocation[1]+"]");
	SaveChildren(winName,winRef,"winRef.");
}

function LoadWindow(winRef){
	var winName = winRef.text;
	try{
		//var cur_frame_location = setting_load(winName,"frameLocation"); //get framelocation of window
		//var cur_array = eval(cur_frame_location); // convert it to a array again from string
		//winRef.frameLocation=cur_array; //set framelocation of the given window
		
		LoadChildren(winName,winRef,"winRef.");
		}catch(ERROR){}
}


function my_window(){
	var my_source = "window {text: 'Import Footage', alignChildren: 'left' , alignment: ['top','fill'],preferredSize: [400,150],\
			base_panel: Panel {text: 'Project:', \
				alignment:['fill','top'], alignChildren: 'left',\
				path_et: EditText{text:'P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/', preferredSize: [400,22]},\
				browse_button: Button{ text: 'Browse'}},\
			shot_panel: Panel {text: 'Pick Shot', \
				alignment:['fill','left'], alignChildren: 'left', orientation: 'row',\
                    ep_st: StaticText {text:'E:',preferredSize: [30,22], justify:'right' }, \
                    ep_et: EditText {text:'01',preferredSize: [50,22] }, \
                    sq_st: StaticText {text:'SQ:',preferredSize: [30,22], justify:'right' }, \
                    sq_et: EditText {text:'010',preferredSize: [50,22] }, \
                    shot_st: StaticText {text:'SH:',preferredSize: [30,22], justify:'right' }, \
				shot_et: EditText {text:'010',preferredSize: [50,22] }, \
			},\
			action_panel: Panel {text: 'Click to Import : ', alignChildren: 'left' ,\
				button_group: Group{ orientation:'row', import_sequence_button: Button{ text: 'Import Sequence'},import_shot_button: Button{ text: 'Import Shot'},\
                check_folder_button: Button{ text: 'Check For folder'}},\
			} \
		}";
		
	var my_window = new Window(my_source);
    my_window.action_panel.button_group.import_sequence_button.onClick = ImportSeq;
	my_window.action_panel.button_group.import_shot_button.onClick = ImportShot;
    my_window.action_panel.button_group.check_folder_button.onClick = CheckForFolder;
    my_window.base_panel.browse_button.onClick = PickFolder;
    
	//my_window.action_panel.button_group.save_button.onClick = SaveCompFile;
    my_window.onClose = function(){
        SaveWindow(my_window);
	}

	return my_window;
}

import_UI = my_window();
LoadWindow(import_UI);

import_UI.show();
//ImportSeq();




