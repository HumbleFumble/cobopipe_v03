#target.aftereffects
function Run(cur_comp){
     $.writeln(cur_comp)
		if(cur_comp==null){
			var cur_comp = app.project.selection[0];
			if(cur_comp==undefined || cur_comp.typeName != "Composition"){
				return;
				}
        }
        var comp_layers =  cur_comp.layers;
        for(var c = 1; c<=comp_layers.length; c++){
            var cur_layer = comp_layers[c];
            if(cur_layer.source instanceof CompItem){
                cur_layer.threeDLayer = true;
                Run(cur_layer.source);
                }
            else{
                cur_layer.threeDLayer = true;
            }
        }
	}

Run(null)