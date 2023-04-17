#target.aftereffects;

//set render queue and output path
function SetupRenderQueue(render_comp, out_folder, out_name, out_module){
	var renderSetting = "Best Settings";
	var outputModule = out_module; //"DPX_RGBA";
	var renderPath = out_folder;	
	var filename = out_name;
	var output_path = renderPath + filename;
	
	//create folder if it doesn't exists
	comp_folder = new Folder(renderPath);
	if(!comp_folder.exists){comp_folder.create();}
		
	while(app.project.renderQueue.numItems >= 1) {
			app.project.renderQueue.item(1).remove();
		}

	var render_item = app.project.renderQueue.items.add(render_comp);
	

	
	var outputMO = render_item.outputModules[1];
	var out_found = false;
	for (var i=0; i<outputMO.templates.length; i++){
        //alert(outputMO.templates[i]);
		if (outputMO.templates[i].indexOf(outputModule)==0){
			out_found = true
			}
		}
	if(out_found){
		outputMO.applyTemplate(outputModule); 
		render_item.applyTemplate(renderSetting);
		outputMO.file = new File(output_path);
		}else{
		alert("render template NOT FOUND");
		}

}

//Find Render Comp
function FindOutputComp(comp_name){
	var to_return = false;
	var project_content = app.project.items;
	for(var p =project_content.length;p>=1;p--){
		var cur_content = project_content[p];
		if(cur_content instanceof CompItem){
			if(cur_content.name == comp_name){
				to_return = cur_content;
				}
			}
		}
	return to_return;
	}

function create_output_module(){
	var render_comp = FindOutputComp('.RENDER')
    var render_item = app.project.renderQueue.items.add(render_comp);
	var output_module = render_item.outputModules[1];
	var omItem1_settable_str = app.project.renderQueue.item(1).outputModule(1).getSettings( GetSettingsFormat.STRING_SETTABLE );	
	//app.project.renderQueue.item(2).outputModule(1).setSettings( omItem1_settable_str );
	alert(omItem1_settable_str)
}

function run(){
    create_output_module();
}