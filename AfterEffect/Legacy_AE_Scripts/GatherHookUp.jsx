#target.aftereffects
//should ask for act, seq, start and end shot. Then import tifs and audio of those shots and place them in 
//order in a comp. Is hard coded to GetSanta.

var base_project_path = "P:/930383_KiwiStrit3/Production/Film/"

function FindShots(E,SQ){
	//Check for folders with shot numbers between the start and end number. return a list of those numbers.
    //    "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E01/E01_SQ020/_Preview/"
	var cur_folder_path =base_project_path + E + "/" + E +"_" + SQ + "/_Preview/";
	var folder_object = new Folder(cur_folder_path);
	var cur_folder_content = folder_object.getFiles();
	var number_list = [];
	if(cur_folder_content){
		var sorted_content = cur_folder_content.sort();
		for(var f =0; f<sorted_content.length;f++){
            cur_content = sorted_content[f];
            //cur_path = cur_folder_path + cur_content.toString()
            if(cur_content.toString().indexOf(".mov") > -1){
                number_list.push(cur_content);
                }
			}
		return number_list;
    }else{
        return null;
        }
}

function FindShotsInSequence(E,SQ){
	//Check for folders with shot numbers between the start and end number. return a list of those numbers.
    //    "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E01/E01_SQ020/_Preview/"
	var cur_folder_path =base_project_path + E + "/" + E +"_" + SQ + "/";
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


function FindSQ(E){
    var cur_folder_path =base_project_path + E + "/";
	var folder_object = new Folder(cur_folder_path);
	var cur_folder_content = folder_object.getFiles();
    return_list = [];
    if(cur_folder_content){
		var sorted_content = cur_folder_content.sort();
		for(var f =0; f<sorted_content.length;f++){
			cur_content = sorted_content[f];
			if(cur_content instanceof Folder){ //check if the content object is a folder
				if(cur_content.toString().indexOf("SQ") > -1){
                    return_list.push(cur_content);
                    }
                }
            }
        
        }
    return return_list;
    }
	
function CreateComp(comp_name, comp_length){
	var compW = 1920;
	var compH = 1080;
	var compL =   2;
	var compRate = 25;
	
	var cur_comp = app.project.items.addComp(comp_name,compW,compH,1,comp_length,compRate);
	
	return cur_comp;
	}

function CloseProject(){
	//app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
	if(app.project.close(CloseOptions.PROMPT_TO_SAVE_CHANGES)){
		app.newProject();
		}
	}

function ImportFootage(my_path,sequence_boolean){
	my_footage = new File(my_path);
	import_options = new ImportOptions(my_footage);
	import_options.sequence = sequence_boolean;
    if(my_footage.exists){
        try{
            project_item = app.project.importFile(import_options);
            project_item.mainSource.conformFrameRate = 25.00;
        return project_item
        }
        catch(err){
            alert("Got this error for " + my_path + ": " + err);
            return null
            }
       }else{
           return null;
           }
}

function Pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

function AddTimecode(cur_comp){
	comp_height = cur_comp.height;
    
	name_layer = cur_comp.layers.addText();
	frame_layer = cur_comp.layers.addText()

	name_layer.name = "TimeCode_Name";
	name_layer.transform.position.setValue([100,50]);
	name_layer.transform.scale.setValue([100,100]);


	name_expression ="\
	layer_name = '';\
	for (i = 1; i <= thisComp.numLayers; i++){  \
			my_layer = thisComp.layer(i); \
		if (my_layer.name !='TimeCode_Frame' && my_layer.name !='TimeCode_Name' && my_layer.active) {; \
		if (time >= my_layer.inPoint && time < my_layer.outPoint){ \
			layer_name = my_layer.name; \
			break; \
		}\
		}else{\
		layer_name = 'No Active Layer'}\
		} 'Name : ' + layer_name";

	name_layer.sourceText.expression = name_expression;

	frame_y = comp_height - 50;
	frame_layer.name = 'TimeCode_Frame';
	frame_layer.transform.position.setValue([100,frame_y]);
	frame_layer.transform.scale.setValue([100,100]);

	frame_expression = "\
	function Pad(n, width, z) {\
		z = z || '0';\
		n = n + '';\
		return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;\
	}\
	\
	layer_frame_number = 0;\
	for (i = 1; i <= thisComp.numLayers; i++){  \
			my_layer = thisComp.layer(i); \
		if (! (my_layer.name !='TimeCode_Name' && my_layer.name !='TimeCode_Frame' && my_layer.active)) continue; \
		if (time >= my_layer.inPoint && time < my_layer.outPoint){ \
			layer_duration = Math.round(my_layer.source.duration*25);\
			layer_frame_number = Math.round(((time - my_layer.inPoint)/thisComp.frameDuration)+1); \
			break; \
		}\
		}'Current shot frame :  ' + Pad(layer_frame_number,5)\
		+ '\\t\\t\\t' + 'Total shot duration  :  ' + Pad(layer_duration,5)";
	frame_layer.sourceText.expression = frame_expression;
}
function CheckOutputList(output_list){
    for(x=0;x <output_list.length;x++){
        var cur_output = output_list[x];
        //$.writeln(cur_output);
        var output_file = new File ( cur_output );
        if( output_file.exists ) {
            //$.writeln("Found: " + cur_output);
            return [cur_output,x]
            }
        }
    return null;
    }

function ImportShotFootage(file_path){
    if (CheckOutputList ([file_path]) != null){
        if(file_path.toString().indexOf(".mov") > -1){
                var anim = ImportFootage(file_path,false);
            }else{
                var anim = ImportFootage(file_path,true);
            }
        if (anim != null){
            cur_duration = anim.duration;
            return [anim,cur_duration];
            }
        }
        return null
    }

function ImportAllSequence(E, SQ){
    var cur_folder_path =base_project_path + E + "/" + E +"_" + SQ + "/";
    var shots = FindShotsInSequence(E,SQ);

    var comp_length = 0;
    var start_time_list = [];
    var shot_missing_list = [];

    var list_of_shot_lists = [];
    
    var pick_type_list = [];
    //make pick_type_list
    if(cur_win.grp.check_group.animatic_import.value){
        pick_type_list.push(4);
        }
    if(cur_win.grp.check_group.preview_import.value){
        pick_type_list.push(3);
        }
    if(cur_win.grp.check_group.fast_render_import.value){
        pick_type_list.push(2);
        }
    if(cur_win.grp.check_group.comp_mov_import.value){
        pick_type_list.push(1);
        }
    if(cur_win.grp.check_group.comp_exr_import.value){
        pick_type_list.push(0);
        }

    pick_type_list = pick_type_list.sort();
    
    
    var seq_folder = app.project.items.addFolder(E + "_" + SQ + "_Footage");
    for (x=0;x<pick_type_list.length;x++){
        var temp_list = [];
        list_of_shot_lists.push(temp_list);
        }
    for(s=0;s <shots.length;s++){
        var length_to_add = 0;
        var shot = shots[s];
        var preview_file = cur_folder_path + "/_Preview/" + shot + ".mov";
        var animatic_file = cur_folder_path + shot + "/" + shot + "_Animatic.mov";
        var fast_file = cur_folder_path + shot + "/Passes/FastA/" + shot + "_FastA_.0001.exr";
        var comp_file = cur_folder_path + shot + "/05_CompOutput/" + shot + "_0001.exr";
        var comp_mov_preview= cur_folder_path + "/_Preview/" + shot + "_Comp.mov";
        
        var input_type_list = [comp_file,comp_mov_preview, fast_file, preview_file, animatic_file];
        
        var input_list = [];
        for (y=0;y<pick_type_list.length;y++){
            input_list.push(input_type_list[pick_type_list[y]]);
            }
        var cur_duration = 0;
        for(i=0;i <input_list.length;i++){ //IMPORT SHOT FOOTAGE AND PLACE IN LIST AND FOLDER
            var cur_input_list = list_of_shot_lists[i];
            cur_footage = ImportShotFootage(input_list[i]);
            if (cur_footage != null){
                cur_input_list.push(cur_footage[0]);
                cur_footage[0].parentFolder = seq_folder;
                """
                if(cur_duration <cur_footage[1]){
                    cur_duration = cur_footage[1];
                    }
                """
                cur_duration = cur_footage[1];
                //if(i==(input_list.length-1)){ //IF LOWEST LEVEL; USE AS DURATION
                   // cur_duration = cur_footage[1];
                    //comp_length = comp_length + cur_duration;
                    //start_time_list.push(cur_duration);
                //}
            }else{
                cur_input_list.push(null);
                shot_missing_list.push("Can't find footage for: " + shots[i] + ":\n" + input_list[i]);
                //if(i==(input_list.length-1)){
                   // start_time_list.push(null);
                    //}
                }
            }//input for loop

        comp_length = comp_length + cur_duration;
        if(cur_duration ==0){
            start_time_list.push(null);
            }else{
            start_time_list.push(cur_duration);
            }
        }//shot for loop
    var start_time = 0;
    var comp_name= E+"_"+SQ;
    if(comp_length != 0){
        var cur_comp = CreateComp(comp_name,comp_length);
        lowest_list = list_of_shot_lists[list_of_shot_lists.length-1];
        for(var cs = 0;cs<lowest_list.length;cs++){
                var label_count = 9;
                for(ci=list_of_shot_lists.length-1;ci >=0;ci--){
                    var list_footage =list_of_shot_lists[ci][cs];
                    if(list_footage){
                        var cur_layer = cur_comp.layers.add(list_footage);
                        var footage_height = list_footage.height;
                        var scale = (1080/footage_height) *100;
                        cur_layer.transform.scale.setValue([scale,scale]);
                        cur_layer.audioEnabled = false;
                        cur_layer.label = label_count;
                        cur_layer.moveToBeginning();
                        cur_layer.startTime = start_time;

                        }
                    label_count = label_count +1;
                    }
                start_time = start_time + start_time_list[cs];
            }
            AddTimecode (cur_comp)
            var cur_solid = cur_comp.layers.addSolid([0,0,0],"No_Tifs_Layer",1920,1080,1,comp_length)
            cur_solid.moveToEnd();
        }else{
            alert("No Frames Found!");
            }
        //return_list = shot_missing_list.concat(shot_input_list);
        return shot_missing_list.sort();
    }//function

function GetEpisode(){
	var e_input = cur_win.grp.panel_group.edit_group.et_e.text;
    
	var e_number = parseInt(e_input,10);
	var E = "E"+ Pad(e_number,2);
	return E
	}

function GetSeq(){
	var seq_input = cur_win.grp.panel_group.edit_group.et_seq.text;
	var seq_number = parseInt(seq_input,10);
	var seq = "SQ" + Pad(seq_number,3);
	return seq
	}

function ClickedOnImportSQ(){
    E= GetEpisode();
    SQ = GetSeq();
    //ImportSequence(E,SQ);
    //FindShotsInSequence (E, SQ)
    
    info_list = ImportAllSequence(E,SQ);
    //info_list = NewImportSequence(E,SQ);
    alert("INFO:\n" + info_list.join("\n"));
    }
function ClickedOnImportE(){
     E= GetEpisode();
    SQ_list = FindSQ(E);
    info_list = [];
    for(var f =0; f<SQ_list.length;f++){
        SQ_name =(SQ_list[f].toString() ).split("/");
        SQ_name = SQ_name[SQ_name.length-1].split("_")[1];
        
        temp_list = ImportAllSequence(E,SQ_name);
        info_list = info_list.concat(temp_list);
    }
    alert("INFO:\n" + info_list.join("\n"));
}


function my_UI_saveChild(uiObject,path,call_name){
    var return_list = [];
    for(var i = 0;i<uiObject.children.length;i++){
        var path = path+".children["+i+"]";
        if(uiObject.children[i].type.toLowerCase() == 'panel'||uiObject.children[i].type.toLowerCase() == 'group'||uiObject.children[i].type.toLowerCase() == 'tabbedpanel'||uiObject.children[i].type.toLowerCase() == 'tab'){
            var to_return = my_UI_saveChild(uiObject.children[i],path,call_name);
            return_list.push(to_return);
        } else if(uiObject.children[i].type.toLowerCase() == "dropdownlist"){
            if(uiObject.children[i].items.length >0){
            app.settings.saveSetting(call_name, path+".selection", uiObject.children[i].selection);
            }
        } else if(uiObject.children[i].type.toLowerCase() == "radiobutton"||uiObject.children[i].type.toLowerCase() == "checkbox"){
            app.settings.saveSetting(call_name, path+".value", uiObject.children[i].value);
            app.settings.saveSetting(call_name, path+".enabled", uiObject.children[i].enabled);
        }else if(uiObject.children[i].type.toLowerCase() == "edittext"||uiObject.children[i].type.toLowerCase() == "statictext"){
            //alert("Saving" + path+".text" + " AS: " + uiObject.children[i].text);
            app.settings.saveSetting(call_name, path+".text", uiObject.children[i].text);
            app.settings.saveSetting(call_name, path+".enabled", uiObject.children[i].enabled);
            //return_list.push(path + " " + uiObject.children[i].text + "\n");
            }
            """else{ //commented out because it doesn't add anything?
                return_list.push("NOT :" + path + " " + uiObject.children[i].type + "\n");
                }
                """
    }
    return return_list;
}
    
function my_UI_initChild(uiObject,path,call_name){
    var return_list = [];
    for(var i = 0;i<uiObject.children.length;i++){
        var path = path+".children["+i+"]";
        if(uiObject.children[i].type.toLowerCase() == 'panel'||uiObject.children[i].type.toLowerCase() == 'group'||uiObject.children[i].type.toLowerCase() == 'tabbedpanel'||uiObject.children[i].type.toLowerCase() == 'tab'){//if(uiObject.children[i].type == 'panel'||uiObject.children[i].type == 'group'){
            var to_return = my_UI_initChild(uiObject.children[i],path,call_name);
            return_list.push(to_return);
        } else if(uiObject.children[i].type.toLowerCase() == "dropdownlist"){
                if (app.settings.haveSetting(call_name, path+".selection")){
                    var selection = app.settings.getSetting(call_name, path+".selection");
                    var drop_down = uiObject.children[i];
                    for(var a=0;a< drop_down.items.length;a++){
                        if(drop_down.items[a].text == selection){
                            drop_down.items[a].selected = true;
                        }
                    }
                }
        } else if(uiObject.children[i].type.toLowerCase() == "radiobutton"||uiObject.children[i].type.toLowerCase() == "checkbox"){
            
            if (app.settings.haveSetting(call_name, path+".value")){
                uiObject.children[i].value = eval(app.settings.getSetting(call_name, path+".value"));
                
            }
            if (app.settings.haveSetting(call_name, path+".enabled")){
                uiObject.children[i].enabled = eval(app.settings.getSetting(call_name, path+".enabled"));
            }
        } else if(uiObject.children[i].type.toLowerCase() == "edittext"||uiObject.children[i].type.toLowerCase() == "statictext"){
            if (app.settings.haveSetting(call_name, path+".text")){
                uiObject.children[i].text = app.settings.getSetting(call_name, path+".text");
            }
            if (app.settings.haveSetting(call_name, path+".enabled")){
                uiObject.children[i].enabled = eval(app.settings.getSetting(call_name, path+".enabled"));
            }
            return_list.push(path + " " + uiObject.children[i].type + "\n");
            }
        """}else{
            return_list.push("NOT :" + path + " " + uiObject.children[i].type + "\n");
            }
            """
    }
}
    
function my_UI_save(winRef,current_call_name){
    var path = winRef.name;
        for(var i = 0;i<winRef.children.length;i++){
            var path = path+".children["+i+"]";
            my_UI_saveChild(winRef.children[i],path,current_call_name);
        }

}
function my_UI_init(winRef, current_call_name){
    var path = winRef.name;

        for(var i = 0;i<winRef.children.length;i++){
            var path = path+".children["+i+"]";
            my_UI_initChild(winRef.children[i],path,current_call_name);
        }

}

function buildUI(thisObj){
    var win = (thisObj instanceof Panel) ? thisObj : new Window("palette", "ImportEpisode", undefined,{resizeable:true});
    win.name = "GatherHookUp";
    if(win != null){
        var window_text = "Group{orientation:'column',alignment:['fill','fill'],\
        panel_group: Group{orientation: 'row',\
        static_group: Group{orientation: 'column',st_e: StaticText {text: 'E #', preferredSize: ['50','20']}, st_seq: StaticText {text: 'SQ #', preferredSize: ['50','20']} },\
        edit_group: Group{orientation: 'column',et_e: EditText{text: '01', preferredSize: ['50','20']}, et_seq: EditText{text: '020', preferredSize: ['50','20']} },},\
        check_group: Group {orientation: 'column', animatic_import: Checkbox {text: 'Import Animatic', value: true},preview_import: Checkbox {text: 'Import AnimPreview',value: true},\
        fast_render_import: Checkbox {text: 'Import Fast Render',value: true}, comp_mov_import: Checkbox {text: 'Import Comp Mov',value: true}, comp_exr_import: Checkbox {text: 'Import Comp EXR',value: true}}\
        button_group: Group {orientation: 'row', ep_button: Button{text:'Import Episode'}, sq_button: Button{text: 'Import Sequence'}\ }\
    }";
    win.grp = win.add(window_text);
    win.layout.layout(true);
    //Don't know what this does. But it needs it to run :/
    //win.layout.layout(true);
    my_UI_init(win, "GatherHookUp");
    win.grp.button_group.ep_button.onClick = ClickedOnImportE;
    win.grp.button_group.sq_button.onClick = ClickedOnImportSQ;
    
    win.grp.panel_group.edit_group.et_e.onChange = function(){
        my_UI_save(win,"GatherHookUp" );
    }
    win.grp.panel_group.edit_group.et_seq.onChange = function(){
        my_UI_save(win,"GatherHookUp" );
    }
        
    win.onClose = function(){
        alert("Saving!");
        my_UI_save(win,"GatherHookUp" );
        }    
     return win;
     }
}
var cur_win = buildUI(this);

"""
var E = "E01";
var SQ = "SQ030";
NewImportSequence(E,SQ);
"""
