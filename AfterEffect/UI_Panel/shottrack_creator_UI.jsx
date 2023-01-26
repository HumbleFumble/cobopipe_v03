#target.aftereffects
//INCLUDES
//#include "/p/tools/adobe_scripts/includes/functions.jsx";
//#include "/p/tools/adobe_scripts/includes/afx_functions.jsx";
//INCLUDES END




function createUI(thisObj){
        current_call_name = "shottack_creator_UI";
        
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
    
    function string_addZeros(numberRef,cifferNumber){
        var numberString = numberRef.toString();
        
        returnRef =  "";
        for(var i = 0; i < cifferNumber-numberString.length;i++){
            returnRef = returnRef +"0";
        }
        returnRef = returnRef + numberString;
        
        return returnRef;
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
    
	function my_UI_save(winRef){
		var path = winRef.name;
			for(var i = 0;i<winRef.children.length;i++){
				var path = path+".children["+i+"]";
				my_UI_saveChild(winRef.children[i],path,current_call_name);
			}

	}
	function my_UI_init(winRef){
		var path = winRef.name;

			for(var i = 0;i<winRef.children.length;i++){
				var path = path+".children["+i+"]";
				my_UI_initChild(winRef.children[i],path,current_call_name);
			}

	}

	
	
	////<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Setup tab functions here  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>				////
		function layers_preCompToDur(){
			app.beginUndoGroup("Pre-Compose to Layer Duration");
			//var find_shot = paletteRef.grp.layers_panel.findShot.value;
			//var find_shot = my_win.grp.layers_panel.findShot.value;
			
			try{
			  // select the active item in the project window
			  // and make sure it's a comp
			
			  var myComp = app.project.activeItem;
			  if(myComp instanceof CompItem) {
			
			    // make sure one or more layers are selected
			
			    var myLayers = myComp.selectedLayers;
			    if(myLayers.length > 0){
					// try to select shot
					//if(myLayers.length==1&&find_shot==true){  //OLD if including "find shot"
					if(myLayers.length==1){  //OLD if including "find shot"
							var layerStart = myLayers[0];
							var startIndex = layerStart.index;
							var curIndex = startIndex-1;
							while(curIndex >0){
								var source = myComp.layer(curIndex).source;
								if(source==null||source instanceof CompItem){
									curIndex=0;
								} else {
									myLayers.push(myComp.layer(curIndex));
									curIndex--;
								}
								
							}
					}
				    
				   //make array of layer 
				 var layerMarks = markers_getTimes(myLayers);
				 
			      // set new comp's default in and out points to those of first layer
			
			      var newInPoint = myLayers[0].inPoint;
			      var newOutPoint = myLayers[0].outPoint;
			
			      // create new comp name of "comp " plus name of first layer
			
			      var newCompName = "";
			      var layerName = myLayers[0].name;
			      if(layerName.length > 26) {
				layerName = layerName.substring(0, 26);
			      }
			      newCompName += layerName;
			
			      // "precompose" expects an array of layer indices
			
			      var layerIndices = new Array();
			      for (var i = 0; i < myLayers.length; i++) {
				layerIndices[layerIndices.length] = myLayers[i].index;
			
				// make sure new comp in point is in point of earliest layer
				// and new comp out point is out point of latest layer
			
				if (myLayers[i].inPoint < newInPoint) newInPoint = myLayers[i].inPoint;
				if (myLayers[i].outPoint > newOutPoint) newOutPoint = myLayers[i].outPoint;
			      }
			
			      // create the new comp
			
			      var newComp = myComp.layers.precompose(layerIndices, newCompName, true );
			
			      // set in and out points of new comp
			
			      var preCompLayer = myComp.selectedLayers[0];
			      //preCompLayer.inPoint = newInPoint;
			      //preCompLayer.outPoint = newOutPoint;
			      
			      newCompLayers = newComp.layers;
			       
			      dur = 0;
			      var offset = newCompLayers[1].startTime-newCompLayers[1].inPoint;
			      for (var i = 0; i < newCompLayers.length; i++) {
				      var layerRef = newCompLayers[i+1];
				      layerRef.startTime =  layerRef.startTime-layerRef.inPoint+dur;
				      
				      if (layerRef.outPoint > dur) dur = layerRef.outPoint;
			      }
			      
			     newComp.duration = dur;
			      preCompLayer.startTime = newInPoint;
			      
			      //set markers on new layer
			      for(var j = 0;j < layerMarks.length;j++){
				      var markers = preCompLayer.property("Marker");
				      //alert(layerMarks[j]);
					markers.addKey(layerMarks[j]);
			      }
			      
			    }else{
			       alert("select at least one layer to precompose.");
			    }
			  }else{
			    alert("please select a composition.");
			  }
				} catch(e){
					alert(e.line+":"+e.message);
					}
			  app.endUndoGroup();
		}
		
		
		function layers_rename(){
			//rename layers to shotname*******************************************
			var digits = tab_setup.children[1].rename_panel.digits.text; //var digits = paletteRef.grp.rename_panel.digits.text;

			var step = tab_setup.children[1].rename_panel.step.text;
			var name = tab_setup.children[1].rename_panel.prefix.text;
            var epName = epName_get();
            var seqName = seqName_get();
            name = name.replace("epVAR", epName);
            name = name.replace("seqVAR", seqName);
              
			var compRef =  comp_get();
			if(compRef!=null){
				try{
				var allLayers = compRef.layers;
				
				count = 0;
				
				for(var i = 1;i <= allLayers.length;i++){
					if(allLayers[i].name.indexOf("timecode") != -1 || allLayers[i].name.indexOf("lyd") != -1|| allLayers[i].name.indexOf("guide") != -1|| allLayers[i].name.indexOf("sound") != -1||allLayers[i].name.indexOf("ignore") != -1){
					}else{
						
						if(isNaN(digits)){
							digits = 3;
						}
					
						if(isNaN(step)){
							step = 10;
						}
						
						count = ((count*1)+(step*1))*1;
						var numberRef = Pad(count,digits);
						allLayers[i].name =name+numberRef;
					}
				}
				} catch(e){
					alert(e.line+":"+e.message);
				}
				
			} else {
			}
		}
        
        function firstLayerFirst(myComp){
            try{
                var myLayers = myComp.layers;
                for(i=1;i <=myLayers.length;i++){
                     
                    
                    var myFirstLayer = myLayers[i];
                    for(j=i+1;j<=myLayers.length;j++){
                        if(myFirstLayer.inPoint <= myLayers[j].inPoint){
                        myFirstLayer = myLayers[j];
                        
                        }
                    }
                    myFirstLayer.moveToBeginning();
                
                }
                for(i=1;i <=myLayers.length;i++){
                     
                    if(myLayers[i].name.indexOf("lyd") != -1){
                        myLayers[i].moveToEnd();
                    }
                    if(myLayers[i].name.indexOf("timecode") != -1){
                        myLayers[i].moveToBeginning();
                    }
                }
            }catch(e){
                alert(page_this+":"+e.line+":"+e.message);
            }
        }
		function SetComp(){
			var comp_text = tab_setup.children[1].compName_panel.st;
			var comp_link = tab_setup.children[1].compName_panel.st;
			if(app.project.activeItem instanceof CompItem){
				
				compRef = app.project.activeItem;
				
				comp_text.text= compRef.name; //paletteRef.grp.compName_panel.st.text = compRef.name;
				comp_link.comp = compRef; //paletteRef.grp.compName_panel.st.comp = compRef;
			} else {
				comp_text.text= "Please Select A Composition";//paletteRef.grp.compName_panel.st.text = "Please Select A Composition";
				comp_link.comp= null;//paletteRef.grp.compName_panel.st.comp = null;
			}
		}
		
		function comp_get(){
			var compRef = tab_setup.children[1].compName_panel.st.comp;
			if(compRef!=null){
				return compRef;
			} else {
				alert("Please Select A Composition");
				return null;
			}
		}
		
		function markers_clearOutside(){
			var compRef = comp_get();
			if(compRef!=null){
				var layersRef = compRef.selectedLayers;
				for(var k = 0;k<layersRef.length;k++){
					var layer = layersRef[k];
									
					var markerStream = layer.property("Marker");
					if (markerStream == null){
						return;
					}
										
					var layerStart = layer.inPoint;
					var layerEnd = layer.outPoint;
					
					var keyTime;
	
					// Remove markers here -- from right to left for simplicity
					for (var l=markerStream.numKeys; l>0; l--)
					{
						keyTime = markerStream.keyTime(l);
						if ((keyTime < layerStart) || (keyTime >layerEnd)){
							markerStream.removeKey(l);
						}
					}

				}
			}
		}
		
		function markers_getTimes(layersRef){
			
			var layerMarks = new Array();
			try{
				for (var i = 0; i < layersRef.length; i++) {
					var layer = layersRef[i];
					var markerStream = layer.property("Marker");
					if (markerStream == null){
					} else {
					
						var layerStart = layer.inPoint;
						var layerEnd = layer.outPoint;
						
						var keyTime;
						
						// Remove markers here -- from right to left for simplicity
						for (var l=markerStream.numKeys; l>0; l--){
							keyTime = markerStream.keyTime(l);
							if ((keyTime >= layerStart) && (keyTime <= layerEnd)){
								layerMarks.push(keyTime);
							}
						}
					}
				}
			} catch(e){
				alert(e.line+":"+e.message);
			}
			return layerMarks;
		}
	
		function markers_reset(){
			
			try{
				var compRef = comp_get();
				
				if(compRef!=null){
					var layersRef = compRef.selectedLayers;
					for(var k = 0;k<layersRef.length;k++){
						var layer = layersRef[k];
						
						
						var markerStream = layer.property("Marker");
						if (markerStream == null){
							return;
						}

						var layerStart = layer.inPoint;
						var layerEnd = layer.outPoint;
						
						var keyTime;

						// Remove markers here -- from right to left for simplicity
						for (var l=markerStream.numKeys; l>0; l--){
							keyTime = markerStream.keyTime(l);
							if ((keyTime < layerStart) || (keyTime >=  layerEnd)){
								markerStream.removeKey(l);
							}
						}
						markerStream.addKey(layerStart);
					}	
			
				}
			} catch(e){
			alert(e.line+":"+e.message);
			}
		}
	
		function getShottrackText(text_type){	
			var cur_comp = comp_get();
            var epName = epName_get();
            var seqName = seqName_get();
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
			if(cur_comp!=null){
				try{
				//REMOVED  var shottrackSeqFolder = shottrackSeqFolder_get();
				//REMOVED if(shottrackSeqFolder!=null&&shottrackSeqFolder.exists){ 
					
					var compRef =cur_comp;
					var allLayersRef = compRef.layers;
					//make Arrays containing folder Name,duration and startFrame
					var theString = "";
					for(var i = 1;i <= allLayersRef.length;i++){
						
						if(allLayersRef[i].name.indexOf("Amplitude") != -1 ||allLayersRef[i].name.indexOf("Audio") != -1 ||allLayersRef[i].name.indexOf("timecode") != -1 || allLayersRef[i].name.indexOf("lyd") != -1|| allLayersRef[i].name.indexOf("guide") != -1|| allLayersRef[i].name.indexOf("sound") != -1|| allLayersRef[i].name.indexOf("Sound") != -1){
						}else{
							if(i!=1){
								theString = theString+parter;
							}
							//shotName = allLayersRef[i].name;	 // making the shot name include episode and sequence name.
                                //shotName = epName + "_" + seqName + "_" + allLayersRef[i].name;
                                shotName = allLayersRef[i].name;
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
					}

				} catch(e){
					alert(e.line+":"+e.message);
				}
				
			}
              if(text_type == "previs"){

                    var prod = produktionFolder_get();
                    prod = prod.toString();
                    var c_path = prod + "/" + epName + "/" + epName + "_PREVIS/03_Output/" + epName + "_"+ seqName +".txt";

                    var statusfile = new File(c_path);
                    statusfile.open("w");
                    statusfile.write(theString);
                    statusfile.close();

                  }
				return theString;
		}
	
		function orderLayers(){
			var cur_comp = comp_get();
			if(cur_comp!=null){
				try{
					firstLayerFirst(cur_comp);
				} catch(e){
					alert(e.line+":"+e.message);
				}
			} else {
				alert("Please Set Composition");
			}
		}
        function layer_tjeckName(nameRef){
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
        function Pad(n, width, z) {
				z = z || '0';
				n = n + '';
				return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
			}
        function RQClear(){
            // clear renderQueue
            while(app.project.renderQueue.numItems >= 1) {
                app.project.renderQueue.item(1).remove();
            }   
        }
		function AddTimecode(){
			var cur_comp = comp_get();
			comp_height = cur_comp.height;
              var seq = seqName_get ()
              var ep = epName_get ()
			name_layer = cur_comp.layers.addText();
			frame_layer = cur_comp.layers.addText()

			name_layer.name = "timecode_Name";
			name_layer.transform.position.setValue([100,100]);
			name_layer.transform.scale.setValue([100,100]);


			name_expression ="\
			layer_name = '';\
			for (i = 1; i <= thisComp.numLayers; i++){  \
					my_layer = thisComp.layer(i); \
				if (my_layer.name !='timecode_Frame' && my_layer.name !='timecode_Name' && my_layer.active && !my_layer.name.includes('ignore')) {; \
				if (time >= my_layer.inPoint && time < my_layer.outPoint){ \
					layer_name = my_layer.name; \
					break; \
				}\
				}else{\
				layer_name = 'No Active Layer'}\
				} 'Name : " + ep + "_" + seq + "_' + layer_name";

			name_layer.sourceText.expression = name_expression;

			frame_y = comp_height - 50;
			frame_layer.name = 'timecode_Frame';
			frame_layer.transform.position.setValue([100,frame_y]);
			frame_layer.transform.scale.setValue([80,80]);

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
				if (! (my_layer.name !='timecode_Name' && my_layer.name !='timecode_Frame' && my_layer.active && !my_layer.name.includes('ignore'))) continue; \
				if (time >= my_layer.inPoint && time < my_layer.outPoint){ \
					layer_duration = my_layer.source.duration*25;\
					layer_frame_number = Math.round(((time - my_layer.inPoint)/thisComp.frameDuration)+1); \
					break; \
				}\
				}'frame :  ' + Pad(layer_frame_number,5)";
				//+ '\\t\\t\\t' + 'Total shot duration  :  ' + Pad(layer_duration,5)";
			frame_layer.sourceText.expression = frame_expression;
		}
	
	////<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Render tab functions here  >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>				////	
		function produktionFolder_get(){
			var folder_text = tab_render.children[1].produktionfolder_panel.prod_st.text;
			var produktionFolder = new Folder(folder_text);
			if(!produktionFolder.exists){
					alert("Please Set Produktion Folder");
					return null;
			} else {
				return produktionFolder;
			}		
		}
		function add_subfolder(){
			var cur_list = tab_render.children[1].subfolder_panel.listbox;
			newFolder = prompt("Add Sequence Folder");
			if(newFolder){
				shotfolders = var_load("shotfolders");
			
				shotfolders.push(newFolder);
				shotfolders.sort();
				var_save("shotfolders",shotfolders);
				
				cur_list.removeAll();
				
				for(var i = 0; i < shotfolders.length;i++){
					cur_list.add("item",shotfolders[i]);
				}
			}
		}
		function remove_subfolder(){
			var cur_list = tab_render.children[1].subfolder_panel.listbox;
			var selection =cur_list.selection;
			
			if(selection == null){
				alert("please select a folder in the box");
			} else {
				selection = selection.toString();
				shotfolders = new Array();
				shots = var_load("shotfolders");
				for(var i = 0; i < shots.length;i++){
					if(shots[i]!= selection){
						shotfolders.push(shots[i]);
					}
				}
				shotfolders.sort();
				var_save("shotfolders",shotfolders);
				cur_list.removeAll();
			
				for(var i = 0; i < shotfolders.length;i++){
					cur_list.add("item",shotfolders[i]);
				}
			}
			
		}
        function CreateEpisodePrevizFolders(){ //HARDCODED! Create an episode folder and saves the current file inside.
            var folder_list = ["_Preview","01_AfterEffects","05_BaseMaterial","03_Output"];
            var prodFolder =produktionFolder_get();
            var ep = epName_get();

            top_folder_path = prodFolder.toString() + "/" + ep + "/" + ep + "_PREVIS";
            top_folder = new Folder(top_folder_path);
            
            if(!top_folder.exists){
                top_folder.create();
                for(i=0;i<folder_list.length;i++){
                    var next_folder = new Folder(top_folder_path + "/" + folder_list[i]);
                    next_folder.create();
                    }
                file_save_path = top_folder_path + "/" + "01_AfterEffects/" + ep +"_Previs_V001.aep";
                app.project.save(new File(file_save_path));
                alert("Done!");
                }else{
                    alert("Folder already exists!");
                    }
            }

		function folders_create(){
			var compRef =  comp_get();
			var prodFolder =produktionFolder_get();
			var seqName = seqName_get();
			if(compRef!=null&&prodFolder.exists){
				var layersRef = layers_get();
				for (var i = 0;i < layersRef.length ;i++){
					//create shot folder
					//Create Shot Folder
					var shotName = layersRef[i].name;
					var newFolders = var_load("shotfolders");
					if(newFolders){
						for(var j = 0; j < newFolders.length;j++){
									//Create Shot Folder
									var folderAr = newFolders[j].split("/");
									var curFolderPath = prodFolder.absoluteURI;
									for(var k = 0;k<folderAr.length;k++){
										folderName = folderAr[k].replace("seqVAR",seqName);
										folderName = folderName.replace("shotVAR",shotName);
										var curFolderPath = curFolderPath+"/"+folderName;
										var curFolder = new Folder(curFolderPath);
										curFolder.create();
									}
									//new Folder(shotFolder.absoluteURI +'/'+shotfolders[j]).create();
						}
					}
				}
			}
		}
	
		function seqName_get(){
			return tab_render.children[1].produktionfolder_panel.et.text;
		}
        function epName_get(){
            return tab_render.children[1].produktionfolder_panel.ep_et.text;
            }
	
		function layers_get(){
			var compRef = comp_get();
			if(compRef!=null){
				var layersRef = new Array();
				var selectedLayers = compRef.selectedLayers;
				if(selectedLayers.length>0){
					layersRef = compRef.selectedLayers;
				} else {
					
					for(var j = 0; j < compRef.numLayers;j++){
						layersRef[j] = compRef.layers[j+1];
					}
				}
			
				var returnLayers = new Array();
				for(var j = 0; j < layersRef.length;j++){
						var nameRef = layersRef[j].name;
						if(nameRef.indexOf("timecode")==-1&&nameRef.indexOf("lyd")==-1&&nameRef.indexOf("guide")==-1&&nameRef.indexOf("Audio Amplitude")==-1&&nameRef.indexOf("sound")==-1){
							returnLayers.push(layersRef[j]);
						}
					}
				
				return returnLayers;
			} else {
				return null;
			}
		}
	
		
		function init_shotfolders(){
			var cur_list = tab_render.children[1].subfolder_panel.listbox;
			//shotfolders = var_load("shotfolders");
            shotfolders = [];
			
			cur_list.removeAll();
			
			for(var i = 0; i < shotfolders.length;i++){
				cur_list.add("item",shotfolders[i]);
			}
		}
	
		function shottrackSeqFolder_get(){
			var produktionFolder = produktionFolder_get();
			if(produktionFolder!= null && produktionFolder.exists){
				var seqName = seqName_get();
				var shottrackFolder = new Folder(produktionFolder.absoluteURI + '/shottrack/');
				shottrackFolder.create();
				var shottrackSeqFolder = new Folder(shottrackFolder.absoluteURI + '/'+seqName);
				shottrackSeqFolder.create();
				return shottrackSeqFolder;
			} else {
				return null;
			}
		}
		
		function seq_guess(){
			var seq_text = tab_render.children[1].produktionfolder_panel.et;
			  if(app.project.activeItem instanceof CompItem){
				compRef = app.project.activeItem;
				seq_text.text = compRef.name;
			} else {
				seq_text.text = "Select A composition";
			}
		}
	
		function produktionFolder_set(){
			var prod_path =  tab_render.children[1].produktionfolder_panel.prod_st;
			try{
				if(app.project.file!=null){
					var projectFold = new Folder(app.project.file.path);
				} else {
					var projectFold = new Folder("/p/");
				}
				
				var output = Folder.selectDialog('Select Produktion Folder',projectFold);
				if(output){
					prod_path.text = output.absoluteURI;
					my_UI_save(my_win);
				}
			} catch(e){
				alert(e.line+"_"+e.meassage);
			}
		}
	
		function RefreshTemplates(winRef){
			var module_dropdown = winRef;
			module_dropdown.selection = null;
			module_dropdown.removeAll();
			compRef = comp_get();
			// Get the list of render settings and output module templates
			// (Need to add a dummy comp to the render queue to do this)
			if(compRef!=null){
				var rqi = app.project.renderQueue.items.add(compRef);
				var om = rqi.outputModule(1);								// Assumes at least one output module
				for (var i=0; i<om.templates.length; i++){
					if (om.templates[i].indexOf("_HIDDEN") != 0){	
						module_dropdown.add("item", om.templates[i]);
                            }
                        }

				if (om.templates.length > 0){
					//module_dropdown.selection = 0;
                        render_drop_down = my_win.children[0].children[1].children[1].renderDropDown;
                        render_panel_path = my_win.children[0].children[1].children[1].sound_panel;
                        if (render_drop_down.selection != null){
                            my_UI_initChild(render_panel_path, my_win.name , current_call_name+"_" + render_drop_down.selection.toString() );
                            }
                        }
                        
					
				rqi.remove();// Remove the temp render queue item
				compRef.openInViewer()
				}
			
		}

        function SetupShotFolder(soundPath, seqName, shotName){
            var folderAr = soundPath.split("/");
            epName = epName_get();
            var curFolderPath = produktionFolder_get().absoluteURI;
            //curFolderPath = curFolderPath+"/"+epName +"/" + epName + "_" + seqName;
            curFolderPath = curFolderPath+"/"+epName +"/" + epName + "_" + seqName+"/" + epName + "_" + seqName +"_" + shotName;
            """
            for(var j = 0;j<folderAr.length;j++){
                folderName = folderAr[j].replace(/epVAR/g,epName);
                folderName = folderName.replace(/seqVAR/g,seqName);
                folderName = folderName.replace(/shotVAR/g,shotName);
                var curFolderPath = curFolderPath+"/"+folderName;
                //alert(curFolderPath);
                }"""
            var curFolder = new Folder(curFolderPath);
            curFolder.create();

        return curFolder
        }
    
        function deleteTypeInFolder(theFolder,cur_type){
            try{
                var myFiles = theFolder.getFiles(cur_type);
                if(myFiles[0]){
                    for(j=0;j<myFiles.length;j++){
                        myFiles[j].remove();
                    }
                }
            }catch(e){
                alert(page_this+":"+e.line+":"+e.message);
            }
            
        }
        
        function renderStoryboard(){
            try{
                RQClear();
                var rendermax = 70;
                var rendercount = 0;
                var compRef =  comp_get();
                //var seqFolder = seqFolder_get();
                //var shottrackSeqFolder = shottrackSeqFolder_get();
                var prod_folder = produktionFolder_get();
            
                var soundPath = tab_render.children[1].sound_panel.soundPath.path.text;
                var epName = epName_get ();
                var seqName = seqName_get();
                //var shottrackSeqFolder = new Folder(prod_folder + soundPath)
                //var seqName = shottrackSeqFolder.name;
                
                if(compRef!=null&&prod_folder.exists){
                    var layersRef = layers_get();
                    for (var i = 0;i < layersRef.length ;i++){
                        try{
                            if(!layer_tjeckName(layersRef[i].name)||layersRef[i].inPoint>compRef.duration||layersRef[i].outPoint<0){
                            }else{
                                
                                //RENDER SHOTTRACK PNG**********************
                                var somethingToRender = false;
                                var markerTimes = new Array();
                        
                                //get time from layer Markers or layer start
                                var layerMarkers = new Array;
                                
                                var markerNum = layersRef[i].property('marker').numKeys;
                    
                                var j = 0;
                                //sorterer markers fra der er uden for lag og markers der har comments
                                for(var k = 1;k <= markerNum;k++){
                                    var time = layersRef[i].property('marker').keyTime(k);
                                    if(time< layersRef[i].inPoint|| time <0){
                                    }else if(time>=layersRef[i].outPoint-compRef.frameDuration||time>compRef.duration){
                                    }else if(layersRef[i].property('marker').valueAtTime(time,true).comment!=""){ 
                                        
                                    }else{
                                        markerTimes[j] = layersRef[i].property('marker').keyTime(k);
                                        j++;
                                    }
                                }
                            
                                
                                
                                var shotPictureName = new Array;
                        
                                for(var k = 0;k < markerTimes.length; k++){
                                    var number = string_addZeros(k+1,2);
                                    
                                    var folderPictureName = layersRef[i].name + '_'+number;
                                    
                                    //var shottrackShotFolder = new Folder(shottrackSeqFolder.absoluteURI+'/'+layersRef[i].name);
                                    //var shottrackShotFolder = new Folder(SetupShotFolder(soundPath, seqName, layersRef[i].name).absoluteURI + "/Storyboards/")
                                    var shottrackShotFolder = new Folder(prod_folder.absoluteURI + '/GoogleThumbs/' +seqName +'/');
                                    
                                    
                                    
                                    shottrackShotFolder.create();
                                    try{
                                        deleteTypeInFolder(shottrackShotFolder,"*.png");
                                    }catch(e){
                                    }
                                    
                                    somethingToRender = true;
                                    
                                    var renderItem = app.project.renderQueue.items.add(compRef);
                                    renderItem.applyTemplate('Best Settings');     
                                    renderItem.timeSpanStart = markerTimes[k];
                                    renderItem.timeSpanDuration = 1/25;
                                    var outputMO = renderItem.outputModules[1];
                                    outputMO.applyTemplate("shot_storyboard");
                                    
                                    //outputMO.file = new File(prod_folder.absoluteURI +'/GoogleThumbs/' +epName +"_"+seqName +'_'+ folderPictureName+'.[####].png');
                                    outputMO.file = new File(shottrackShotFolder.absoluteURI +'/' +epName +"_"+seqName +'_'+ folderPictureName+'.[####].png');
                                    //outputMO.file = new File(shottrackShotFolder.absoluteURI +'/'+seqName +'_'+ folderPictureName+'.[####].png');
                                    rendercount++;
                                                        
                                }
                                
                                
                        
                                //Create Shot Folder
                                //var shotFolder = new Folder(shottrackSeqFolder.absoluteURI +'/'+ layersRef[i].name);
                                //shotFolder.create();
                                
                                
                                if(rendercount > rendermax){
                                        app.project.renderQueue.render();
                                    rendercount = 0;
                                    RQClear();
                                }
                                
                            }
                        } catch(e){
                            alert(e.line+":"+e.message);
                        }
                    }
                    
                    if(rendercount > 0){
                        app.project.renderQueue.render();
                        rendercount = 0;
                        RQClear();
                    }

                }
                } catch(e){
                                alert(e.line+":"+e.message);
                            }
		}
	
		function renderSound(){
			try{
			var soundPath = tab_render.children[1].sound_panel.soundPath.path.text;
                
			var sound_module = tab_render.children[1].sound_panel.render.sound_render_panel.render_template.selection;
			var soundFile = tab_render.children[1].sound_panel.soundFile.file_name.text;
			var render_check_value = tab_render.children[1].sound_panel.render_check.render_box.value;
			
			RQClear();
			var rendermax = 70;
			var rendercount = 0;
			var compRef =  comp_get();
             var epName = epName_get();
			var seqName = seqName_get();
			var prutFolder = produktionFolder_get();
			if(compRef!=null||prutFolder!==null){
				var layersRef = layers_get();
				for (var i = 0;i < layersRef.length ;i++){
					
						if(!layer_tjeckName(layersRef[i].name)||layersRef[i].inPoint>compRef.duration||layersRef[i].outPoint<0){
						}else{
						
							//set work area to layer length
							var shotName =  layersRef[i].name;
							var newName =  layersRef[i].name;
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
							var folderAr = soundPath.split("/");
							var curFolderPath = prutFolder.absoluteURI;
							for(var j = 0;j<folderAr.length;j++){
                                    folderName = folderAr[j].replace("epVAR",epName);
								folderName = folderName.replace("seqVAR",seqName);
								folderName = folderName.replace("shotVAR",shotName);
								var curFolderPath = curFolderPath+"/"+folderName;
								var curFolder = new Folder(curFolderPath);
								curFolder.create();
							}
							var cur_soundfile = soundFile;
                                cur_soundfile = cur_soundfile.replace("epVAR",epName);
							cur_soundfile = cur_soundfile.replace("seqVAR",seqName);
							cur_soundfile = cur_soundfile.replace("shotVAR",newName);
							var shotFolder =curFolder;
							//render shot sound
							somethingToRender = true;
							
							renderItem = app.project.renderQueue.items.add(compRef);
							renderItem.timeSpanStart = inPoint;
							renderItem.timeSpanDuration = layerDuration;
							var outputMO = renderItem.outputModules[1];
							
							outputMO.applyTemplate(sound_module);
                                //outputMO.ApplyTemplate("H.264");
							
							var sound_out  = new File(shotFolder.absoluteURI+'/' +cur_soundfile );
                                if(cur_soundfile.search(".jpg")>-1){ //If image stack of jpgs try to delete them before render.
                                        try{
                                            deleteTypeInFolder(new Folder(shotFolder),"*.jpg");
                                        }catch(e){}
                                    }
                                //alert(shotFolder.absoluteURI+'/' +cur_soundfile );
                                //alert(File.decode(shotFolder.absoluteURI+'/' +cur_soundfile).toString());

							outputMO.file = sound_out;
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
					if(render_check_value){
						//RQClear(); // Don't clear render queue
						}
				}

			}
			} catch(e){
						alert(e.line+":"+e.message);
					}
			//compRef.openInViewer() //Opens back up the old comp flow
		//app.project.renderQueue.queueInAME(false); //Submit til media encoder queue items. Uses the last used preset/format by encoder.
		}
        function GetStoryOutput(){
            var soundPath = tab_render.children[1].sound_panel.soundPath.path.text;
			var sound_module = tab_render.children[1].sound_panel.render.sound_render_panel.render_template.selection;
			var soundFile = tab_render.children[1].sound_panel.soundFile.file_name.text;
			
			var text_line = tab_render.children[1].sound_panel.temp_path;
              var epName = epName_get();
			var seqName = seqName_get();
			var shotName =  "ShotName";
				
			//REPLACE VARS
             soundPath = soundPath.replace(/epVAR/g,epName);
			soundPath = soundPath.replace(/seqVAR/g,seqName);
			//soundPath = soundPath.replace("shotVAR",shotName);
			//var final_path = curFolder.absoluteURI+'/' +soundFile;
			var final_path = soundPath + "/Storyboards/";
			tab_render.children[1].storyboard_panel.story_path.text = final_path;
            }
        
		function GetOutputPath(){
			var soundPath = tab_render.children[1].sound_panel.soundPath.path.text;
			var sound_module = tab_render.children[1].sound_panel.render.sound_render_panel.render_template.selection;
			var soundFile = tab_render.children[1].sound_panel.soundFile.file_name.text;
			
			//var text_line = tab_render.children[1].sound_panel.temp_path;
            //EP NAME HERE!
            var epName = epName_get();
            var seqName = seqName_get();
			//var shotName =  "ShotName";
				
			//REPLACE VARS
            soundPath = soundPath.replace(/epVAR/g,epName);
            soundPath = soundPath.replace(/seqVAR/g,seqName);
            //soundPath = soundPath.replace("shotVAR",shotName);
            soundFile = soundFile.replace(/epVAR/g,epName);
            soundFile = soundFile.replace(/seqVAR/g,seqName);
            //soundFile = soundFile.replace("shotVAR",shotName);
            //var final_path = curFolder.absoluteURI+'/' +soundFile;
            var final_path = soundPath + "/" + soundFile;
            tab_render.children[1].sound_panel.temp_path.text = final_path;
            GetStoryOutput();
		}
	////<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< UI BUILDING STARTS HERE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>		
    var my_win = (thisObj instanceof Panel) ? thisObj : new Window("palette", "Shot_Creator_V4.0",undefined, {resizeable:true});
        my_win.name = "Shot_Creator_V4.0";
        if (my_win != null){
            var main_panel = my_win.add('tabbedpanel',undefined,undefined, {name: 'tabbed_panel'} );
            main_panel.name = "tabbed_panel";
            main_panel.preferredSize = [350,300];

            var tab_setup = main_panel.add('tab', undefined, "Shot_Setup");
            tab_setup.add('statictext', undefined, "within Shot Setup Tab");
            tab_setup.name = "Shot_Setup";

            var tab_render = main_panel.add('tab', undefined, "Render_Output");
            tab_render.name = "Render_Output";
            tab_render.add('statictext', undefined, "within Render Output");
            main_panel.selection = tab_render;

            var buttons = my_win.add('group');
            buttons.add ('button', undefined, "Save Settings", {name: 'save_ui'});
            buttons.add ('button', undefined, "Refresh", {name: 'refresh'});


            var render_panel = "group {orientation:'column',\
                                produktionfolder_panel: Panel { \
                                alignment:['fill','top'], \
                                orientation: 'column',\
                                text: 'Produktion Folder Path', \
                                alignChildren: 'left', margins: 10, properties:{name:'produktionfolder_panel'}, \
                                    set: Button {bounds: [10,20,150,40], text: 'Pick Production Path',},\
                                    prod_st: StaticText {bounds: [10,20,260,40],text: 'Please Set', },\
                                    ep_st: StaticText {bounds: [10,20,150,40],text: 'Set Episode Name: (epVAR)', },\
                                    ep_et: EditText {text: 'Bad Guess' , preferredSize: {width:200, height:-1}, },\
                                    create_ep_folder: Button {bounds: [10,20,280,40], text: 'Create Episode Previz Folder and Save file',},\
                                    seq_st: StaticText {bounds: [10,20,150,40],text: 'Set Sequence Name: (seqVAR) ', },\
                                    et: EditText {text: 'Bad Guess' , preferredSize: {width:200, height:-1}, },\
                                },\
                                storyboard_panel: Panel { \
                                alignment:['fill','top'], \
                                orientation:'column', \
                                text: 'Storyboard', \
                                alignChildren: 'left', margins: 15, \
                                    render: Button {text: 'Render!', },\
                                        story_path: StaticText {text: 'temp_path ', preferredSize:[320,-1]}\
                                },  \
                                renderDropDown: DropDownList{ alignment:['fill','top']},\
                                sound_panel: Panel { \
                                alignment:['fill','top'], \
                                text: 'Sound / Movie', \
                                alignChildren: 'left', margins: 15, \
                                    render: Group { \
                                    orientation:'row', alignment:['fill','top'], \
                                    alignChildren: 'left', margins: 0, \
                                        render: Button {text: 'Render!', },\
                                        sound_render_panel: Panel{text: 'Using : ',alignment:['fill','top'],\
                                        render_template: DropDownList{ alignment:['fill','top'], alignment:['fill','top'] },\
                                        }\
                                    },\
                                    render_check: Group {\
                                    orientation:'row', alignment:['fill','top'], \
                                    alignChildren: 'left', margins: 0, \
                                        check_text: StaticText {text: 'Clear RenderQueue after Render : ', preferredSize:[180,-1]},\
                                        render_box: Checkbox {value: true,},\
                                    },\
                                    soundPath: Group { \
                                    orientation:'row', alignment:['fill','top'], \
                                    alignChildren: 'left', margins: 0, \
                                        path_st: StaticText {text: 'Path', preferredSize:[40,-1]},\
                                        path: EditText {text: 'epVAR/epVAR_seqVAR/epVAR_seqVAR_shotVAR/',preferredSize:[300,-1]},\
                                    },\
                                    soundFile: Group { \
                                    orientation:'row', alignment:['fill','top'], \
                                    alignChildren: 'left', margins: 0, \
                                        file_st: StaticText {text: 'File ', preferredSize:[40,-1]},\
                                        file_name: EditText {text: 'epVAR_seqVAR_shotVAR_Animatic', preferredSize:[300,-1]},\
                                    },\
                                    temp_path: StaticText {text: 'temp_path ', preferredSize:[320,-1]},\
                            },  \
                                subfolder_panel: Panel {  \
                                alignment:['fill','top'], \
                                    text: 'Folder Creator', alignChildren: 'left', margins: 15, \
                                    listbox: ListBox {bounds: [10,110,260,200] },\
                                    gg: Group { \
                                    orientation:'row', \
                                        ADD: Button { preferredSize: [40,20], text: 'Add',},\
                                        REMOVE: Button {preferredSize: [60,20], text: 'Remove',},\
                                        CREATE: Button { preferredSize: [60,20], text: 'Create',},\
                                        }, \
                                }, \
                            }";
                            
            var setup_group = "group{orientation:'column',\
                                        compName_panel: Panel { \
                                        alignment:['fill','top'], \
                                        orientation:'row',\
                                        text: 'Composition', \
                                        alignChildren: 'left', \
                                        margins: 15,\
                                        spacing: 30,\
                                            st: StaticText {text: 'Please Select A Composition', },\
                                            pick: Button{text: 'Pick Current'}\
                                        },\
                                        marker_panel: Panel { \
                                        alignment:['fill','top'], \
                                        orientation:'row', \
                                        text: 'Markers', \
                                        alignChildren: 'left', margins: 15, \
                                            clearOutside: Button {text: 'Clear Outside', },\
                                            reset: Button {text: 'Reset', },\
                                        },\
                                        layers_panel: Panel { \
                                        alignment:['fill','top'], \
                                        text: 'Layers', \
                                        orientation:'row', \
                                        alignChildren: 'left', margins: 15, \
                                            orderLayers: Button {text: 'Order Layers', },\
                                            precompose: Button {text: 'Precompose', },\
                                            findShot: Checkbox {text: 'Find Shot', },\
                                        },  \
                                        rename_panel: Panel { \
                                        orientation:'row', \
                                        alignment:['fill','top'], \
                                        text: 'Rename Layers', \
                                        alignChildren: 'left', margins: 15, \
                                            pst: StaticText {text: 'Prefix:', },\
                                            prefix: EditText {bounds: [10,20,150,40],text: 'SH', },\
                                            dst: StaticText {text: 'Digits:', },\
                                            digits: EditText {bounds: [10,20,30,40],text: 3, },\
                                            sst: StaticText {text: 'step:', },\
                                            step: EditText {bounds: [10,20,40,40],text: 10, preferredSize: [50, -1]},\
                                            go: Button {bounds: [10,20,50,40], text: 'Do It!'},\
                                        },  \
                                        timecode_panel: Panel { \
                                        alignment:['fill','top'], \
                                        text: 'Create TimeCode', \
                                        orientation:'row', \
                                        alignChildren: 'left', margins: 15, \
                                            create_timecode: Button {text: 'Create!', },\
                                        },  \
                                        text_panel: Panel { \
                                        alignment:['fill','top'], \
                                        text: 'Get Shottrack Text String', \
                                        orientation:'row', \
                                        alignChildren: 'left', margins: 15, \
                                            getShottrackString: Button {text: 'Show it!', },\
                                            getGoogleString: Button {text: 'Column Style',}\
                                                 getPrevisString: Button {text: 'Previs Style',}\
                                        },  \
                                    }";
            tab_setup.add(setup_group);
            tab_render.add(render_panel);
            }
        
        //// <<<<<<<<<<<<<<<<<<< SETUP UI FUNCTIONS  >>>>>>>>>>>>>>>>>>>>>>>>>>>
            tab_setup.children[1].rename_panel.go.onClick = function() {
                layers_rename();
            }
            tab_setup.children[1].compName_panel.pick.onClick = function() {
                SetComp();
                seq_guess();
            }
            tab_setup.children[1].timecode_panel.create_timecode.onClick = function() {
                AddTimecode();
            }

            tab_render.children[1].produktionfolder_panel.set.onClick = function() {
                produktionFolder_set();
                my_UI_save(my_win);
            }
        
            //Rename Layers
            tab_setup.children[1].rename_panel.go.onClick = function() {
                layers_rename()
            }
            //AddSub Folder
            tab_render.children[1].subfolder_panel.gg.ADD.onClick = function() {
                add_subfolder();
            }
            
            //Remove Sub Folder
            tab_render.children[1].subfolder_panel.gg.REMOVE.onClick = function() {
                remove_subfolder();
            }
            
            //Create Folders
            tab_render.children[1].subfolder_panel.gg.CREATE.onClick = function() {
                folders_create();
            }	
        
            //Create text string for exel sheet or shottrack list
            tab_setup.children[1].text_panel.getShottrackString.onClick = function() {
                var string = getShottrackText();
                    var dlg = new Window('dialog', 'Shottrack Add Folder Strong');
                   dlg.frameLocation = [600,200];
                    dlg.msgPnl = dlg.add('panel',[25,15,355,130], 'Paste This Into the Add Child Box in the Shottrack');
                    dlg.msgPnl.et = dlg.msgPnl.add('EditText',[2,10,353,120],string) ;
                    dlg.show();
            }
            //Create text string for exel sheet or shottrack list
            tab_setup.children[1].text_panel.getGoogleString.onClick = function() {
                var string = getShottrackText("column");
                var dlg = new Window('dialog', 'Shottrack Add Folder Strong',undefined,{resizeable:'true'});
                dlg.frameLocation = [600,200];
                //dlg.alignment = ["fill","top"]
                //dlg.layout = new AutoLayoutManager(dlg)
                /*
                dlg.msgPnl = dlg.add('panel',[0,0,250,700], 'Paste This Into A Exel-Style Sheet');
                dlg.msgPnl.alignment = "fill"
                dlg.msgPnl.minimumSize = [250,500]

                dlg.msgPnl.et = dlg.msgPnl.add('EditText',undefined,string, {multiline:"true"});
                dlg.msgPnl.et.location = [25,15]
                */
                dlg.et = dlg.add('EditText',[15,25,250,900],string, {multiline:"true"});
                dlg.et.alignment = ["fill","top"]
                //dlg.et.preferredSize = [250,700]
                dlg.show();
            }
            tab_setup.children[1].text_panel.getPrevisString.onClick = function() {
                var string = getShottrackText("previs");
                    var dlg = new Window('dialog', 'Shottrack Add Folder Strong');
                   dlg.frameLocation = [600,200];
                    dlg.msgPnl = dlg.add('panel',[25,15,250,400], 'Paste This Into A Exel-Style Sheet');
                    dlg.msgPnl.et = dlg.msgPnl.add('EditText',[2,10,250,400],string, {multiline:"true"});
                    dlg.show();
            }
        
            //Order Layers
            tab_setup.children[1].layers_panel.orderLayers.onClick = function() {
                orderLayers();
            }
            //Precompose
            tab_setup.children[1].layers_panel.precompose.onClick = function() {
                layers_preCompToDur();
            }
            
            //renderSound
            tab_render.children[1].sound_panel.render.render.onClick = function() {
                renderSound();
            }
            //renderStoryboard
            tab_render.children[1].storyboard_panel.render.onClick = function() {
                renderStoryboard();
            }
            
            //markers
            tab_setup.children[1].marker_panel.clearOutside.onClick = function() {
                markers_clearOutside();
            }
            
            tab_setup.children[1].marker_panel.reset.onClick = function() {
                markers_reset();
            }
            //OnChange filepath
            tab_render.children[1].sound_panel.soundPath.path.onChange=function(){
                GetOutputPath();
                }
            tab_render.children[1].sound_panel.soundFile.file_name.onChange=function(){
                GetOutputPath();
                }
            tab_render.children[1].produktionfolder_panel.et.onChange=function(){
                GetOutputPath();
                }
            tab_render.children[1].produktionfolder_panel.create_ep_folder.onClick=function(){
                CreateEpisodePrevizFolders ();
                }

        my_win.layout.layout(true);
        
        //>>>>>>>>>>>>>>>>>>Setting children for the drop-down render and functions for change and activate<<<<<<<<<<<<<<<<<<<<<<
        render_drop_down = my_win.children[0].children[1].children[1].renderDropDown
        //render_drop_down = my_win.children[0].children[1].children[1].children[2]
        render_panel_path = my_win.children[0].children[1].children[1].sound_panel
        
        //INITIALIZE WINDOW
        my_UI_init(my_win);
        SetComp();
        seq_guess();

        //ADD render type drop downs and fill in render-template drop down and load saved-settings:
        render_drop_down.add ("item", "Animatic");
        render_drop_down.add ("item", "Sound");
        render_drop_down.add ("item", "Animatic_Stack");
        render_drop_down.selection = 0;
        RefreshTemplates(tab_render.children[1].sound_panel.render.sound_render_panel.render_template);
        my_UI_initChild(render_panel_path,my_win.name,current_call_name+"_" + render_drop_down.selection.toString());

        
        render_drop_down.onChange = function(){
            my_UI_initChild(render_panel_path,my_win.name,current_call_name+"_" + render_drop_down.selection.toString());
            GetOutputPath()
            }
        render_drop_down.onActivate = function(){
            my_UI_saveChild(render_panel_path,my_win.name,current_call_name+"_" + render_drop_down.selection.toString());
            }
        render_drop_down.selection = 0;

        
                                
        my_win.layout.layout(true);
        
        my_win.children[1].refresh.onClick = function(){
            //my_win.tabbed_panel.selection = "Shot Setup";
            SetComp();
            RefreshTemplates(tab_render.children[1].sound_panel.render.sound_render_panel.render_template);
            //my_UI_save(my_win);
            }
        my_win.children[1].save_ui.onClick = function(){
            my_UI_save(my_win);
            }


        

        GetOutputPath();
     
        init_shotfolders();

        my_win.onClose = function(){
                my_UI_save(my_win);
                }

        
        return my_win;
}

var cur_win = createUI(this);
