
#target.aftereffects
#include json2.js

//var base_project_path = "P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Film/"
cc = getConfig()
var base_project_path = dict_replace(cc.project_paths,cc.project_paths["film_path"])

function FindShots(E,SQ){
	//Check for folders with shot numbers between the start and end number. return a list of those numbers.
    //    "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/E01/E01_SQ020/_Preview/"
	var cur_folder_path =base_project_path +"/"+ E + "/" + E +"_" + SQ + "/_Preview/";
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
	var cur_folder_path =base_project_path +"/"+ E + "/" + E +"_" + SQ + "/";
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
    var cur_folder_path =base_project_path +"/"+ E + "/";
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
    for(var x=output_list.length-1;x >=0;x--){
        var cur_output = output_list[x][0];

        //$.writeln(cur_output);
        var output_file = new File ( cur_output );
        if( output_file.exists ) {
            //$.writeln("Found: " + cur_output);
            result = [cur_output,output_list[x][1]];
            return result
            }
        }
    return null;
    }
function CheckFilepath(file_path){
    var output_file = new File ( file_path );
    if( output_file.exists ) {
        return true
        }
return null;
    }
function CheckOutputObject(output_list){
    return_obj = null;
    for (var obj_key in output_list){
        var output_file = new File ( output_list[obj_key] );
        if( output_file.exists ) {
            return_obj = obj_key;
            }
        }
    return return_obj;
}

function ImportShotFootage(file_path){
    if (CheckFilepath (file_path) != null){
        if(file_path.toString().indexOf(".mov") > -1 || file_path.toString().indexOf(".wav") > -1 ){
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
    var cur_folder_path =base_project_path +"/"+ E + "/" + E +"_" + SQ + "/";
    var shots = FindShotsInSequence(E,SQ);

    var comp_length = 0;
    var start_time_list = [];
    var shot_missing_list = [];
    var start_time = 0;
    var comp_obj = new Object()
    comp_obj.name = E+"_"+SQ;
    comp_obj.duration = 0
    var label_colors = {"sound":2, "animatic":9,"anim":4,"render":4,"comp":10,"comp_mov":6,"comp_exr":7};
    var shot_list = new Object()
    var pick_list = []

    //Get checked import types
    for(cb=cur_win.grp.check_group.children.length-1;0<=cb;cb--){
        if(cur_win.grp.check_group.children[cb].value){
            name = cur_win.grp.check_group.children[cb].text;
            name = name.split("Import ")[1];
            name = name.replace(/ /g, "_");
            name = name.toLowerCase();
            pick_list.push(name)
            }
    }

    var folder_name = E + "_" + SQ + "_Footage";
    var seq_folder = FindProjectItem(folder_name,FolderItem)
    var preloaded = []
    if(!seq_folder){
        seq_folder = app.project.items.addFolder(E + "_" + SQ + "_Footage");
    }else{
        preloaded = FindFolderFootage(seq_folder)
        }

    var cfg = getConfig()
    var cfgp = cfg.project_paths
    var preview_dict = getPreviewDict(cfgp,cfg.preview_dict)
    preview_dict.sound = [dict_replace(cfgp,cfgp["shot_sound_file"])]
    for(s=0;s <shots.length;s++){
        var length_to_add = 0;
        var shot = shots[s];
        var shot_obj = new Object()
        shot_obj.episode_name = E
        shot_obj.seq_name = SQ
        shot_obj.shot_name = shot.split("_")[2]
        shot_obj.shot = shot
        shot_obj.import_list = []
        shot_obj.full_footage_list = []
        shot_obj.info = ""
        for(var p=0;p<pick_list.length;p++){
            pick = pick_list[p]
            shot_obj[pick] = []
            for(var x = (preview_dict[pick].length-1);x>=0;x--){
                 var temp_path = dict_replace(shot_obj,preview_dict[pick][x])
                  if(temp_path.indexOf("*")>-1){
                    temp_path = temp_path.replace("*","0001.tga")
                    }
                 if(CheckFilepath(temp_path)){
//                    shot_obj[pick].push(temp_path)
                       shot_obj.import_list.push([pick,temp_path])
                }
                shot_obj.full_footage_list.push([pick,temp_path])
            }
        }

        var cur_duration = 0;
        var done = false;
        for(var y=(shot_obj.import_list.length-1);y>=0;y--){
            var step =  shot_obj.import_list[y];
            if(step[0]=="sound" ||!done){
                if(step[1] in preloaded){
                    var cur_footage = preloaded[step[1]]
                }else{
                    var cur_footage = ImportShotFootage(step[1])
                    cur_footage[0].parentFolder = seq_folder;
                }
                step.push(cur_footage[0])
                step.push(cur_footage[1])
                
                if(cur_win.grp.sound_length_check.value){
                 if(step[0] =="sound" || cur_duration == 0){
                    cur_duration = cur_footage[1]
                    }
                }else{
                    if(cur_duration < cur_footage[1]){
                        cur_duration = cur_footage[1];
                    }
                }
                if(cur_win.grp.only_highest_check.value){
                    done = true
                    }
                }else{
                    shot_obj.import_list.splice(y,1)
                }
            }
        shot_obj.duration = cur_duration;
        //CHECK FOR LENGTH
        var check_d = shot_obj.duration
        var check_list = []
        for(var a=0;a<shot_obj.import_list.length; a++){
            if(shot_obj.import_list[a][3]!=check_d){
                check_list.push([shot_obj.import_list[a][0],Math.round((shot_obj.import_list[a][3]-check_d)*25)])
            }
        }
        if(check_list.length >0){
            //shot_obj.info = shot_obj.info + "\nDuration issue: " + shot_obj.shot + " sound length is: " + Math.round(shot_obj.import_list[0][3]*25)
            shot_obj.info = shot_obj.info + "\nFound duration issue in: " + shot_obj.shot
            for(var c=0;c<check_list.length;c++){
                shot_obj.info = shot_obj.info + "\n" + check_list[c][0] + " differs by: " + check_list[c][1]
                }
            }
        shot_list[shot] = shot_obj;
        if(shot_obj.info){
            shot_missing_list.push(shot_obj.info)
           }

        comp_obj.duration = comp_obj.duration + cur_duration;
    }

    if(comp_obj.duration != 0){
        var cur_comp = FindProjectItem(comp_obj.name,CompItem)
        if(cur_comp){
            comp_obj.found_comp = true
            comp_obj.comp = cur_comp
            comp_obj.current_layers = new Object()
            var cur_index = 1
            for(l=1;l<cur_comp.numLayers;l++){
                var cur_l = cur_comp.layer(l)
                if(cur_l.source){
                    if(cur_l.source instanceof FootageItem){
                        comp_obj.current_layers[cur_l.source.file.name] = cur_l
                        cur_index = cur_l.index
                        }
                    }
                }
        }else{
            cur_comp = CreateComp(comp_obj.name,comp_obj.duration);
            comp_obj.comp = cur_comp
            comp_obj.found_comp = false
            comp_obj.current_layers = new Object()
        }
    
        for(var shot_key in shot_list){
            var s = shot_list[shot_key]
            
            var imp_list = s.import_list
            
            var s_index = cur_index
            var sound_found = false
            for(var k=0;k<imp_list.length;k++){
                var n = imp_list[k]
                
                var comp_footage = n[2]
                var cur_layer = false
                if(comp_obj.found_comp){
//                    log(comp_footage.mainSource.file.name)
                    if(comp_footage.file.name in comp_obj.current_layers){
                        log("Found in comp, skipping insert: " + String(comp_footage.file.name))
                        cur_layer = comp_obj.current_layers[comp_footage.file.name]
                        cur_index = cur_layer.index
                        if(String(n[0]).toLowerCase()!="sound"){
                            sound_found = true
                            }
                        //check duration of layer, if it needs to be prolonged, extend comp duration and move in-point for every layer index above this
                    }else{
                        cur_layer = cur_comp.layers.add(comp_footage)
                        if(cur_layer.index != cur_index){
                            cur_layer.moveAfter(cur_comp.layer(cur_index))
                            }
                        if(!sound_found){
                            //TODO Here place the function to move all indexes of footage items above this, the duration of this. Extend comp duration the same length first.
                            log("Need to make room for more! Length: " + n[3])
                            sound_found = true
                            }
                        }
                }
                if(!cur_layer){
                    cur_layer = cur_comp.layers.add(comp_footage);
                    }

                if(String(n[0]).toLowerCase()!="sound"){ //if not sound
                    cur_layer.audioEnabled = false;
                    var footage_height = comp_footage.height;
                    if(String(n[0]).toLowerCase()=="render"){
                        var scale = (1080/footage_height) *110;
                    }else{
                        var scale = (1080/footage_height) *100;
                    }
                    var scale = (1080/footage_height) *100;
                    cur_layer.transform.scale.setValue([scale,scale]);
                    }
                cur_layer.label = label_colors[n[0]];
                if(!comp_obj.found_comp){
                    cur_layer.moveToBeginning();
                }
                cur_layer.startTime = start_time;
            }
            start_time = start_time + s.duration;

        }
        if(cur_win.grp.create_timecode_check.value&&!comp_obj.found_comp){
            AddTimecode (cur_comp)
            var cur_solid = cur_comp.layers.addSolid([0,0,0],"No_Footage_Layer",1920,1080,1,comp_length)
            cur_solid.moveToEnd();
        }
    }
    comp_obj.info = shot_missing_list.sort();
    cur_win.comp_obj_list.push(comp_obj)
    return shot_missing_list.sort();
    }

function GetEpisode(){
	var e_input = cur_win.grp.panel_group.edit_group.et_e.text;

	var e_number = parseInt(e_input);
	var E = "S"+ Pad(e_number,3);
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

////CONFIG INFO

function getPipePath(){
    var path = $.getenv("BOM_PIPE_PATH")
    if(!path){
        //path = "C:/Users/cg/PycharmProjects/cobopipe-v02-001" // T:/_Pipeline/cobopipe-v02-001/
        path = "T:/_Pipeline/cobopipe-v02-001"
        }

    return path
}

function GetProject(pipe_path){
	var project_name = $.getenv("BOM_PROJECT_NAME");
	if(project_name){
		return project_name
	}else{
		project_name = "Hoj"
	}
	return project_name
}

function loadConfigJson(){
    var pipe_path = getPipePath()//"C:/Users/cg/PycharmProjects/cobopipe-v02-001" //System.getenv("BOM_PIPE_PATH")
    var project_name = GetProject(pipe_path)
    var config_file = pipe_path + "/Configs/Config_" + project_name + ".json";
    var myFile = new File(config_file);
    myFile.open('r');
    var jsonFileContent = myFile.read();
    myFile.close();
    var project_config = JSON.parse(jsonFileContent);
    return project_config;
}

function log(msg){
$.writeln(msg)
}

function reg_replace(path){
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

function dict_replace(dict,path){
    var no_keys = [];
    var key_list = reg_replace(path)
    for(i=0;i<key_list.length;i++){
         var c_key = key_list[i]
         var clean_key = clean_key_func(c_key)
         if(clean_key in dict){
             path = path.replace(c_key,dict[clean_key])
             }
         else{
             no_keys.push(c_key)
             }
         }
     var more_keys = reg_replace(path);
     if(more_keys.length!=no_keys.length){
         path = dict_replace(dict,path)
     }
     return path
    }

function getPreviewDict(cfgp,f_dict){
    var preview_obj = new Object()
    for(var k in f_dict){
        preview_obj[k] = []
        var here = f_dict[k];
        for(var i=0;i<f_dict[k].length;i++){
            var tpath = dict_replace(cfgp,cfgp[f_dict[k][i]])
            preview_obj[k].push(tpath)
            }
        }
    return preview_obj
}
function getConfig(){
    cfg = loadConfigJson()
    cfgp = cfg.project_paths
    f_dict = cfg.preview_dict
    var t = getPreviewDict(cfgp,f_dict)
    return cfg
}
function return_preview_keys(cfg){
    var return_list = []
    var t = cfg.preview_dict
    for(s in t){
        return_list.push(s)
    }
    return return_list
}


function FindProjectItem(_name,_type){
        var project_content = app.project.items;
        var my_folder = "";
        for(var p =project_content.length;p>=1;p--){
            var cur_content = project_content[p];
            if(cur_content instanceof _type){
                var folder_name = cur_content.name;
                log("Found this item: " + cur_content.name);
                if(_name == folder_name){
                    return cur_content
                }
            }
        }
        return null
    }

function FindFolderFootage(folder_item){
    var project_footage = new Object();

    var project_content = folder_item.items;
    for(var p =project_content.length;p>=1;p--){
        var cur_content = project_content[p];
        if(cur_content instanceof FootageItem){
            if(cur_content.mainSource instanceof FileSource){
                var cur_name = cur_content.mainSource.file.absoluteURI.replace("/p/","P:/")//cur_content.mainSource.file.name;
                project_footage[cur_name] = [cur_content,cur_content.duration]

                }
        }
    }
    return project_footage
}



var cur_win = (function(thisObj){
    var isPanel = thisObj instanceof Panel; // true or false
    var dialog = isPanel  ? thisObj : new Window("window", "GatherHookup Direct");

    var cfg = getConfig()
    var check_box_list = return_preview_keys(cfg)

    dialog.alignChildren = 'left'
    dialog.alignment = ['top','fill']

    dialog.grp = dialog.add("Group{orientation:'column',alignment:['fill','fill'],\
    panel_group: Group{orientation: 'row',\
    static_group: Group{orientation: 'column',st_e: StaticText {text: 'S #', preferredSize: ['50','20']}, st_seq: StaticText {text: 'SQ #', preferredSize: ['50','20']} },\
    edit_group: Group{orientation: 'column',et_e: EditText{text: '01', preferredSize: ['50','20']}, et_seq: EditText{text: '020', preferredSize: ['50','20']} } }}")
    


    dialog.grp.check_group = dialog.grp.add("Group",undefined,"check_group")
    dialog.grp.check_group.orientation = "column";

    for(var i=0;i<check_box_list.length;i++){
        var c = check_box_list[i]
        dialog.grp.check_group[c + "_import"] = dialog.grp.check_group.add("Checkbox",undefined,c + "_import")
        dialog.grp.check_group[c + "_import"].text = "Import " + c
        dialog.grp.check_group[c + "_import"].value = true
        }
    dialog.grp.check_group.sound_check = dialog.grp.check_group.add("Checkbox", undefined,"sound_import")
    dialog.grp.check_group.sound_check .text = "Import Sound"
    dialog.grp.check_group.sound_check .value = true

    dialog.grp.button_group = dialog.grp.add("Group {orientation: 'row', ep_button: Button{text:'Import Episode'}, sq_button: Button{text: 'Import Sequence'}}")
    dialog.grp.only_highest_check = dialog.grp.add("Checkbox {text: 'Import Highest Step Only',value: true}")
    dialog.grp.sound_length_check = dialog.grp.add("Checkbox {text: 'Base Shot Length On Sound',value: true}")
    dialog.grp.create_timecode_check = dialog.grp.add("Checkbox {text: 'Create TimeCode',value: true}")
    dialog.grp.error_bttn = dialog.grp.add("Button{text: 'Show Error Log'}")

    dialog.name = "GatherHookUp_Direct";
    my_UI_init(dialog, dialog.name);
    dialog.comp_obj_list = []
    dialog.info_string = []

    dialog.grp.button_group.ep_button.onClick = ClickedOnImportE;
    dialog.grp.button_group.sq_button.onClick = ClickedOnImportSQ;

    dialog.grp.panel_group.edit_group.et_e.onChange = function(){
        my_UI_save(dialog,dialog.name );
    }
    dialog.grp.panel_group.edit_group.et_seq.onChange = function(){
        my_UI_save(dialog,dialog.name );
    }
    for(var c=0; c< dialog.grp.check_group.children.length;c++){
        dialog.grp.check_group.children[c].onClick = function(){
            my_UI_save(dialog,dialog.name );
        }
    }
    dialog.grp.only_highest_check.onClick = function(){
        my_UI_save(dialog,dialog.name );
    }
    dialog.grp.create_timecode_check.onClick = function(){
        my_UI_save(dialog,dialog.name );
    }
    dialog.grp.error_bttn.onClick = function(){
        var string = ""
        for(var co in dialog.comp_obj_list){
            string = string + String(dialog.comp_obj_list[co].info) + "\n"
        }
        if(string){alert(string)}
    }

    dialog.onClose = function(){
        my_UI_save(dialog,dialog.name );
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