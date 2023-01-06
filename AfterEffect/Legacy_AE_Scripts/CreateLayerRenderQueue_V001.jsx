#target.aftereffects


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

function PickFolder(){
    var old_input = new Folder(import_UI.base_panel.path_et.text);
    var inputFolder =  new Folder(import_UI.base_panel.path_et.text).selectDlg("Please select the folder");
    if(inputFolder != null){
        import_UI.base_panel.path_et.text = inputFolder;
        setting_save("ImportMultiFolder", "win.children[0].children[1].text", import_UI.base_panel.path_et.text);
        }
    }
function RQClear(){
    // clear renderQueue
    while(app.project.renderQueue.numItems >= 1) {
        app.project.renderQueue.item(1).remove();
    }   
}
function layer_check_name(nameRef){
    try{
        if(nameRef.indexOf("timecode")!=-1||nameRef.indexOf("lyd")!=-1||nameRef.indexOf("guide")!=-1||nameRef.indexOf("ignore")!=-1){
            return false;
        }else{
            return true;
        }
    }catch(e){
        alert(page_this+":"+e.line+":"+e.message);
    }
}
function checkForReady(){
    //check if module name shot_render exists    
    //alert list of shot output paths
    var cur_comp = app.project.activeItem;
    var layer_outputs = null;
    var prod_folder = import_UI.base_panel.path_et.text;
    var output_path = import_UI.base_panel.output_path_et.text;
    var module_name = "shot_render";
    var layersRef = null;
    var epName = GetEpisode();
    var seqName = GetSeq();
    if(cur_comp!=null){
            var layersRef = cur_comp.selectedLayers;
            }
    if(layersRef){
        var layer_outputs = "OUTPUT NAMES:\n";
        for (var i = 0;i < layersRef.length ;i++){
            if(!layer_check_name(layersRef[i].name)||layersRef[i].inPoint>cur_comp.duration||layersRef[i].outPoint<0){
                }else{
                    //set work area to layer length
                    var shotName =  layersRef[i].name;
                    var newName =  layersRef[i].name;
                    var inPoint = layersRef[i].inPoint;
                    
                    if(inPoint<0){
                        inPoint = 0;
                    }
                    var outPoint = layersRef[i].outPoint;
                    
                    if(outPoint>cur_comp.duration){
                        outPoint=cur_comp.duration;
                    }
                    var layerDuration = outPoint-inPoint;
                    var file_name = output_path;
                    file_name = file_name.replace(/epVAR/g,epName);
                    file_name = file_name.replace(/seqVAR/g,seqName);
                    file_name = file_name.replace(/shotVAR/g,newName);

                    
                    //shotFolder.create();
                    //render shot sound
                   
                        //outputMO.ApplyTemplate("H.264");
                    
                    var render_path  ='/' +file_name;
                    layer_outputs = layer_outputs + "\n" + (render_path);
                    }
                }
             var shotFolder =new Folder(prod_folder +'/' +file_name);
            shotFolder =new Folder(shotFolder.path);
            if(!shotFolder.exists){
                alert("Please make the Output folder!");
                alert(shotFolder.fullName);
                }
        renderItem = app.project.renderQueue.items.add(cur_comp);
        var outputMO = renderItem.outputModules[1];
        if(outputMO.templates.toString().indexOf(module_name)==-1){
            alert("Please make output-template called 'shot_render' to use for rendering!");
            }
        RQClear();
        cur_comp.openInViewer()
    }else{alert("Select your layers please!");
            }

   if(layer_outputs){
    alert(layer_outputs);
       }
}

function createRenderQueues(){
    try{
    RQClear();
    var rendermax = 70;
    var rendercount = 0;
    var epName = GetEpisode();
    var seqName = GetSeq();
    var prod_folder = import_UI.base_panel.path_et.text;
    var output_path = import_UI.base_panel.output_path_et.text;
    var module_name = "shot_render";
    var cur_comp = app.project.activeItem;
    var cur_layers = null;
    if(cur_comp!=null){
        layersRef = cur_comp.selectedLayers;
        };
    if(layersRef){
        for (var i = 0;i < layersRef.length ;i++){
            
                if(!layer_check_name(layersRef[i].name)||layersRef[i].inPoint>cur_comp.duration||layersRef[i].outPoint<0){
                }else{
                
                    //set work area to layer length
                    var shotName =  layersRef[i].name;
                    var newName =  layersRef[i].name;
                    var inPoint = layersRef[i].inPoint;
                    
                    if(inPoint<0){
                        inPoint = 0;
                    }
                    var outPoint = layersRef[i].outPoint;
                    
                    if(outPoint>cur_comp.duration){
                        outPoint=cur_comp.duration;
                    }
                    var layerDuration = outPoint-inPoint;
                    var file_name = output_path;
                    file_name = file_name.replace(/epVAR/g,epName);
                    file_name = file_name.replace(/seqVAR/g,seqName);
                    file_name = file_name.replace(/shotVAR/g,newName);
                    var shotFolder =prod_folder;
                    //render shot sound
                    renderItem = app.project.renderQueue.items.add(cur_comp);
                    renderItem.timeSpanStart = inPoint;
                    renderItem.timeSpanDuration = layerDuration;
                    var outputMO = renderItem.outputModules[1];
                    
                    outputMO.applyTemplate(module_name);
                        //outputMO.ApplyTemplate("H.264");
                    
                    var render_path  = new File(prod_folder+'/' +file_name );
                    outputMO.file = render_path;
                    rendercount++;
                    if(outputMO.file.exists){
                            outputMO.file.remove();
                    }
                    if(rendercount > rendermax){
                        //app.project.renderQueue.render(); // commented this out for lack of good output modules, so user can render in Encoder instead
                        rendercount = 0;
                        //RQClear();
                    }
                }
            
        }

        if(rendercount > 0){
            //app.project.renderQueue.render(); // commented this out for lack of good output modules, so user can render in Encoder instead
            rendercount = 0;
        }

    }
    } catch(e){
                alert(e.line+":"+e.message);
            }
    //compRef.openInViewer() //Opens back up the old comp flow
//app.project.renderQueue.queueInAME(false); //Submit til media encoder queue items. Uses the last used preset/format by encoder.
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
	var my_source = "window {text: 'Create RQ from Layers', alignChildren: 'left' , alignment: ['top','fill'],preferredSize: [400,150],\
			base_panel: Panel {text: 'Pick Start Folder and Build Output-Path:', \
				alignment:['fill','top'], alignChildren: 'left',\
				path_et: EditText{text:'P:/930494_BorsteOgBondegaarden/Production/Film', preferredSize: [400,22]},\
				browse_button: Button{ text: 'Browse'}, \
                output_st: StaticText {text:'Output-Path: (replaces VARs at build-time)',preferredSize: [215,22], justify:'right' }, \
                output_path_et: EditText{text:'epVAR/epVAR_seqVAR/_CompOutput/epVAR_seqVAR_shotVAR', preferredSize: [400,22]},\
                },\
			shot_panel: Panel {text: 'Set Episode# and Sequence#', \
				alignment:['fill','left'], alignChildren: 'left', orientation: 'row',\
                    ep_st: StaticText {text:'epVAR:',preferredSize: [50,22], justify:'right' }, \
                    ep_et: EditText {text:'01',preferredSize: [30,22] }, \
                    sq_st: StaticText {text:'seqVAR:',preferredSize: [80,22], justify:'right' }, \
                    sq_et: EditText {text:'010',preferredSize: [50,22] }, \
                    shot_st: StaticText {text:'shotVAR = Layer Name',preferredSize: [150,22], justify:'right' }, \
			},\
			action_panel: Panel {text: 'Click build RQ for currently selected layers : ', alignChildren: 'left' ,\
				button_group: Group{ orientation:'row', create_render_button: Button{ text: 'Create RenderQueues'}\
                check_render_button: Button{ text: 'Check if Ready'}},\
			},\
		}";
		
	var my_window = new Window(my_source);
    my_window.action_panel.button_group.create_render_button.onClick = createRenderQueues;
    my_window.action_panel.button_group.check_render_button.onClick = checkForReady;
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




