////////////////////////////////////////////////////////////////////
// Mr. Multiplane v. 1.5
//Copyright (c) 2009 Mads Juul. All rights reserved.
// Contact: mads.juul@copenhagenbombay.com
// only works with Adobe After Effects CS4 only tested on windows
// Based On the Script PSDto3D_add v1.0 by Paul Tuersley found on aenhancers.com
// PSDto3D_add v1.0
// Copyright (c) 2006 Paul Tuersley. All rights reserved.
// email: paul.tuersley@btinternet.com
//
// Installation 
// This Script is a ScriptUI Panel
// and MUST be put int the After Effects ScriptUI Panels Folder at startup to work
// copy this file to folder 
//C:\Program Files \Adobe\Adobe After Effects CS4\Support Files\Scripts\ScriptUI Panels
// and Start  After effects
// now a new panel is found  in the windows menu
// Select your composition and press reffresh a camera will be created if no camera in composition yet
// and now you can move your layers in 3d by dragging the sliders and the scale will be kept
//
// I take no responsebility for the use and result of this sciprt
// If you like it By me some Beers next time we Party together YEARH
// :-) Mads
///////////////////////////////////////////////////////////////////////77


function createUI(thisObj) {
	function refresh(){
		activeItem = app.project.activeItem;
			if (activeItem != null && activeItem instanceof CompItem){
				var compCenter = [activeItem.width/2, activeItem.height/2];
				var compLayers = activeItem.layers;
				var selectedLayers = activeItem.selectedLayers
				var cameraLayer = null; 
				var curLayer; 
				var curPosition; 
				var curAnchor;
				
				// If a camera exists, use its zoom value
				for (var i = 1; i <= compLayers.length; i++){
					curLayer = compLayers[i]
					if (curLayer.matchName == "ADBE Camera Layer"){
						cameraLayer = curLayer;
						//var camZoom = curLayer.property("Zoom").value;
						//camZoom = (Math.round(camZoom * 10000)) / 10000;
						break;
					}
				}
				
				// If no camera is found, create a new one
				if (cameraLayer == null){	
					var cameraLayer = activeItem.layers.addCamera("Camera 1", compCenter);
					var camZoom = cameraLayer.property("Zoom").value;
					camZoom = (Math.round(camZoom * 10000)) / 10000;
					cameraLayer.property("Position").setValue([compCenter[0],compCenter[1],-camZoom]);
					var camNull  = activeItem.layers.addNull();
					camNull.name = "Kamera_Kontrol";
					camNull.threeDLayer = true;
					cameraLayer.parent = camNull;
					
					
				}
				
				camPos = cameraLayer.property("Position").value;
				var maxval = camPos[2]*-1;
				var minval = camPos[2]*4;
				
				
				
				// If no layers are selected, setup all the layers
				if (selectedLayers.length == 0  || (selectedLayers.length == 1 && selectedLayers[0].matchName == "ADBE Camera Layer"))
				{
					delete(selectedLayers);
					selectedLayers = new Array();
					for(var i = 1; i <= compLayers.length; i++){
						if (compLayers[i].matchName != "ADBE Camera Layer" || compLayers[i].matchName != "ADBE Light Layer"){
							selectedLayers.push(compLayers[i]);
						}
					}
				}
				
				var sel = selectedLayers;
				delete(selectedLayers);
				selectedLayers = new Array();
				for(var i = 0; i < sel.length; i++){
					if (sel[i].matchName == "ADBE AV Layer"&&sel[i].nullLayer ==false){
						selectedLayers.push(sel[i]);
						if(sel[i].threeDLayer == false){
							sel[i].threeDLayer = true;
						}
					}
				}
				
				var num = selectedLayers.length;
				
				
				try{
					var children = paletteRef.grp.layer_panel.children;
					for(var j = 0;j<children.length;j++){
						paletteRef.grp.layer_panel.remove(0);	
					}
					
				} catch(e){
					alert(e.message);
				}
				
				
				var bounds = new Array(5,15,150,35);
				var sbounds = new Array(155,15,350,35);
				var pbounds = new Array(355,15,400,35);
				
				var sliders = new Array();
				var zpositions = new Array();
				zpositionsEnd = new Array();
				var oldzpositions = new Array();
				
				
				for(var rap = 0;rap < num; rap++){
					//alert(selectedLayers[rap].name);
					try{
					var g = paletteRef.grp.layer_panel.add("group");
					} catch(e){
						alert(e.message);
					}
					g.add("statictext",bounds,selectedLayers[rap].index+":"+selectedLayers[rap].name);
					bounds = bounds + new Array(0,20,0,20);
					try{
					// add slider
					var p = selectedLayers[rap].property("Position").value;
					sliders[rap] = g.add("slider",sbounds);
					sliders[rap].index = rap;
					sliders[rap].minvalue = minval;
					sliders[rap].maxvalue = maxval;
					sliders[rap].value = 100;
					sbounds = sbounds + new Array(0,20,0,20);
					} catch(e){
						alert(e.message);
					}
					
					zpositions[rap]  = g.add("button",pbounds,p[2]);
					zpositions[rap].index = rap;
					zpositionsEnd[rap] = p[2];
					pbounds = pbounds + new Array(0,20,0,20);
					
					sliders[rap].onChange = function(){
						activeItem = app.project.activeItem;
						if (activeItem != null && activeItem instanceof CompItem){
							zpositions[this.index].text = Math.round((this.value*-1)*10)/10;
							multiplan_scale(selectedLayers[this.index],cameraLayer,this.value*-1)
						} else {
							alert("Please Select A Coposition in The Project Window");
							try{
								var children = paletteRef.grp.layer_panel.children;
								for(var j = 0;j<children.length;j++){
									paletteRef.grp.layer_panel.remove(0);	
								}
								
							} catch(e){
								alert(e.message);
							}
						}
					}
					
					oldzpositions[rap] = p[2];
					sliders[rap].value = Math.round(p[2])*-1;
					zpositions[rap].text = sliders[rap].value*-1;
				
					zpositions[rap].onClick = function(){
						activeItem = app.project.activeItem;
						if (activeItem != null && activeItem instanceof CompItem){
							var input = prompt('Input Z position',this.text);
							if(input){
								sliders[this.index].value = input*-1;
								this.text = input*1;
								multiplan_scale(selectedLayers[this.index],cameraLayer, input*1)
							}
						} else {
							alert("Please Select A Coposition in The Project Window");
							try{
								var children = paletteRef.grp.layer_panel.children;
								for(var j = 0;j<children.length;j++){
									paletteRef.grp.layer_panel.remove(0);	
								}
								
							} catch(e){
								alert(e.message);
							}
						}
					}
					
					
					//paletteRef.grp.button_grp.refreshBut.add("statictext",bounds,selectedLayers[rap].index+":"+selectedLayers[rap].name);
					//bounds = bounds + new Array(0,20,0,20);
				}
				paletteRef.layout.layout(true);
				//var layer = layersSel[1];
				//alert(layer.name);
			} else {
				
				
				try{
					var children = paletteRef.grp.layer_panel.children;
					for(var j = 0;j<children.length;j++){
						paletteRef.grp.layer_panel.remove(0);	
					}
					
				} catch(e){
					alert(e.message);
				}
				
			}
	}
	var paletteRef = (thisObj instanceof Panel) ? thisObj : new Window("palette", "Mr Multiplan",undefined, {resizeable:true});	
	paletteRef.name = "princessshading";
	if (paletteRef != null) {
		//planes = multiplan_dialog.add('panel',[5,5,415,705],'Layers');
		//layergroup = planes.add('group',[5,5,410,10000]);
		resource = 
		"group { \
			orientation:'column', alignment:['fill','fill'], \
			layer_panel: Panel { \
				alignment:['fill','top'], alignChildren:['left','center'], \
				text: 'Layers',\
				margins: 15, \
			},  \
			button_grp: Group {  \
					orientation:'row', alignment:['top','left'], \
					refreshBut: Button {bounds: [10,20,50,40], text: 'Refresh'},\
			},\
		}";
		
	}
	paletteRef.grp = paletteRef.add(resource);
	
	paletteRef.grp.button_grp.refreshBut.onClick = function() {
		activeItem = app.project.activeItem;
		if (activeItem != null && activeItem instanceof CompItem){
			refresh();
		} else {
			alert("Please Select A Coposition in The Project Window");
			
			try{
				var children = paletteRef.grp.layer_panel.children;
				for(var j = 0;j<children.length;j++){
					paletteRef.grp.layer_panel.remove(0);	
				}
				
			} catch(e){
				alert(e.message);
			}
		}
	}
	
	
	paletteRef.layout.layout(true);
	refresh();
	return paletteRef;
}


var myMultiplanPanel = createUI(this);
//UI_init(myMultiplanPanel);


function multiplan_scale(layerRef,camera,position){
	try{
		
		if(layerRef.canSetCollapseTransformation==true){
			var colapsTransStart = layerRef.collapseTransformation;
			layerRef.collapseTransformation=false;
		}
		var oldParent = layerRef.parent;
		var oldPosition = layerRef.property("Position").value;
		var oldZ = oldPosition[2];
		if(layerRef.threeDLayer == false){
			layerRef.threeDLayer = true;
		}
		
		if(position == oldZ){
			return true;
		} else {
			
			//Setting Camera Zoom
			var camZoom = camera.property("Zoom").value;
			camZoom = (Math.round(camZoom * 10000)) / 10000;
		
			var compRef = layerRef.containingComp;
			var nullRef  = compRef.layers.addNull();
			nullRef.name = "control";
			nullRef.threeDLayer = true;
			var nullPosition = nullRef.property("Position").value;
			nullRef.property("Position").setValue([nullPosition[0],nullPosition[1],oldZ]);
			
			
			layerRef.parent=nullRef;
			
			
			
			var deltaZ = position - oldZ;
			
			
			if(oldZ == 0){
				//Setting Distance
				var nullPosition = nullRef.property("Position").value;
				var distance = deltaZ + camZoom;
			
				//Setting Scale
				var scaleOld = nullRef.property("Scale").value;
				var scale = scaleOld[0] * (distance / camZoom);
			
				nullRef.property("Scale").setValue([scale,scale,scale]);		
				nullRef.property("Position").setValue([nullPosition[0],nullPosition[1],deltaZ*1]);
		
			
				layerRef.parent = oldParent;
				nullRef.remove();
			} else {
				
				//resetting to 0,0,0
				var nullPosition = nullRef.property("Position").value;
				var scale = nullRef.property("Scale").value;
				var distance = nullPosition[2] + camZoom;
				scalezero = (scale[0]*camZoom)/distance
				nullRef.property("Scale").setValue([scalezero,scalezero,scalezero]);		
				nullRef.property("Position").setValue([nullPosition[0],nullPosition[1],0]);
				nullRef.remove();
				
				
				multiplan_scale(layerRef,camera,position);
				
				
			}
		}
		
		if(layerRef.canSetCollapseTransformation==true){
			layerRef.collapseTransformation = colapsTransStart;
		}
		
	} catch(e){
		alert(e.line+":"+e.message);
		return false;
	}
}


