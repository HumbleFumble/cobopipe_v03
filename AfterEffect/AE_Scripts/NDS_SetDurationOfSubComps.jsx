#target.aftereffects

function RunSetDuration(cur_comp, cur_length,cur_framerate){
		if(cur_comp==null){
			var cur_comp = app.project.selection[0];
                
			if(cur_comp==undefined){
				return;
				}
            var cur_length = cur_comp.duration;
            var cur_framerate = cur_comp.frameDuration;
			}
		else{
			cur_comp.duration = cur_length;
            cur_comp.frameDuration = cur_framerate;
			}
		var comp_layers =  cur_comp.layers;
		for(var c = 1; c<=comp_layers.length; c++){
			var cur_layer = comp_layers[c];
			if(cur_layer.source instanceof CompItem){
				Run(cur_layer.source,cur_length,cur_framerate);
				}
			}
		SetOutPoint(cur_comp, cur_length)
	}

function SetOutPoint(my_comp, my_length){
	my_layers = my_comp.layers;
	for(var l=my_layers.length;l>=1;l--){
		set_lock = false;
		if(my_layers[l].locked == true){
			my_layers[l].locked=false;
			set_lock = true;
			}
		if((my_layers[l].outPoint-my_layers[l].inPoint) > 0.04){
            my_layers[l].outPoint = my_length;
		}else{
            alert("Skipping because its only 1 frame long: " + my_layers[l].name);
            }
		if(set_lock){
			my_layers[l].locked=true;
		}
	}
}

RunSetDuration(null,null,25)