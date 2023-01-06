#target.aftereffects

function Run(){
    
    base_path = "P:/_WFH_Projekter/930450_MiasMagicComicBook/Production/Film/";
    compRef = app.project.activeItem;
    comp_text =  compRef.name; //paletteRef.grp.compName_panel.st.text = compRef.name;
    RQClear();
    var layersRef = new Array();
    var selectedLayers = compRef.selectedLayers;
    if(selectedLayers.length>0){
        layersRef = compRef.selectedLayers;
    } else {
        for(var j = 0; j < compRef.numLayers;j++){
            layersRef[j] = compRef.layers[j+1];
        }
    }
    seq_list = []
    cur_layer = layersRef;
    ep = "";
    seq = "";
    for(i=0;i<=cur_layer.length-1;i++){
        if (cur_layer[i].name.indexOf(".mov")>=-1){
            c_ep = (cur_layer[i].name).split("_")[0];
            c_seq = (cur_layer[i].name).split("_")[1];
            c_shot = (cur_layer[i].name).split("_")[2];
            
            if (ep == c_ep && seq == c_seq){
                seq_list.push(cur_layer[i]);
            }else{
                if(seq_list.length>0){
                    getShottrackText("previs", compRef, seq_list, base_path, ep, seq);
                    createRenderQueue(compRef, seq_list, base_path);
                    }
                seq_list = [];
                 seq_list.push(cur_layer[i]);
                }
            
            ep = c_ep;
            seq = c_seq;
            if(i == cur_layer.length-1){
                if(seq_list.length>0){
                    getShottrackText("previs", compRef, seq_list, base_path, ep, seq);
                    createRenderQueue(compRef, seq_list, base_path);
                    }
                }
            //collect_folder = seq_path  + "/_Preview/";
            //alert(collect_folder);
            //getShottrackText ("column", compRef, layersRef, base_path, ep, seq);
            }
                //shot_name = ep+ "_" + seq + "_" + shot;
                //seq_path = base_path + "/" + ep + "/" + ep +"_" + seq + "/";
                //shot_path = seq_path + "/" + shot_name + "/";
        
        }
    
}


function RQClear(){
    // clear renderQueue
    while(app.project.renderQueue.numItems >= 1) {
        app.project.renderQueue.item(1).remove();
    }   
}


function createRenderQueue(compRef, cur_layers, base_path){
    try{        
        //RQClear();
        var rendermax = 70;
        var rendercount = 0;
        if(compRef!=null||base_path!==null){
            var layersRef = cur_layers;
            for (var i = 0;i < layersRef.length ;i++){ 
                    if(layersRef[i].inPoint>compRef.duration||layersRef[i].outPoint<0){
                    }else{
                        if(layersRef[i].name.indexOf(".mov")>-1){
                            ep = (layersRef[i].name).split("_")[0];
                            seq = (layersRef[i].name).split("_")[1];
                            shot = (layersRef[i].name).split("_")[2];
                            shot = shot.split(".mov")[0];
                            shot_name = ep+ "_" + seq + "_" + shot;
                            seq_path = base_path + "/" + ep + "/" + ep +"_" + seq + "/";
                            shot_path = seq_path + "/" + shot_name + "/";

                            //set work area to layer length
                            var inPoint = layersRef[i].inPoint;
                            if(inPoint<0){
                                inPoint = 0;
                            }
                            var outPoint = layersRef[i].outPoint;

                            if(outPoint>compRef.duration){
                                outPoint=compRef.duration;
                            }
                            var layerDuration = outPoint-inPoint;
                            //Create Shot Folder
                            //shot folder =
                            animatic_module = "shot_preview";
                            sound_module = "shot_sound";
                            animatic_file = shot_path + shot_name +"_Animatic.mov";
                            sound_file = shot_path + shot_name +"_Sound.wav";
                             var folder_check  = new Folder(shot_path );
                             if(folder_check.exists){
                                //alert(animatic_file);
                                //render shot sound
                                somethingToRender = true;
                                CreateRenderItem(compRef, inPoint, layerDuration, sound_module, sound_file); //create animatic
                                //CreateRenderItem(compRef, inPoint, layerDuration, sound_module, sound_file); //create sound
                            }else{
                                alert("Can't find: " + shot_path);
                            }
                        }
                }
            }
        } 
    }
    catch(e){
                alert(e.line+":"+e.message);
            }	
}

function CreateRenderItem(compRef, inPoint, layerDuration, out_module, out_file){
    renderItem = app.project.renderQueue.items.add(compRef);
    renderItem.timeSpanStart = inPoint;
    renderItem.timeSpanDuration = layerDuration;
    var outputMO = renderItem.outputModules[1];
    
    outputMO.applyTemplate(out_module);
    
    var path_out  = new File(out_file );

    outputMO.file = path_out;
    if(outputMO.file .exists){
        //test
        outputMO.file .remove()
    }
}


function getShottrackText(text_type, compRef, allLayersRef, base_path, ep, seq){	
			var theString=false;
			var joiner = ":";
			var parter = ";";
			if(text_type == "column"){
				joiner = "\t";
				parter = "\n";
				}
              if(text_type == "previs"){
				joiner = "\,";
				parter = "\n";
				}
			if(compRef!=null){
				try{
					var theString = "";
					for(var i = 0;i <= allLayersRef.length-1;i++){
                            if(i!=0){
                                theString = theString+parter;
                            }
                            shotName = allLayersRef[i].name;
                            shotName = (allLayersRef[i].name).split("_")[2];
                            shotName = shotName.split(".mov")[0];
                            theString = theString+shotName+joiner;
                    
                    
                            start = Math.round(allLayersRef[i].inPoint*25)+1;
                            if(start<1){
                                start = 1;
                            }
                            var outpoint = allLayersRef[i].outPoint;
                            if(allLayersRef[i].outPoint > compRef.duration)
                                outpoint = compRef.duration;
                            //calculating duration
                            var delta =  outpoint - allLayersRef[i].inPoint;
                            
                            var layerDur = Math.round(delta/compRef.frameDuration);  
                            theString = theString+layerDur;
					}

				} catch(e){
					alert(e.line+":"+e.message);
				}
				
			}
                  if(text_type == "previs"){
                        var c_path = base_path + "/" + ep + "/" + ep + "_PREVIS/03_Output/" + ep + "_"+ seq +"_Edit.txt";
                        var statusfile = new File(c_path);
                        statusfile.open("w");
                        statusfile.write(theString);
                        statusfile.close();
                  }else{
                      var c_path = base_path + "/" + ep + "/" + ep + "_PREVIS/03_Output/" + ep + "_"+ seq +"_Edit.txt";
                      //alert(c_path + "\n" + theString);
                      }
}


var base_path = "P:/930462_HOJ_Project/Production/Film/"
var compRef = app.project.activeItem;
cur_layers = compRef.selectedLayers;
createRenderQueue(compRef,cur_layers,base_path)