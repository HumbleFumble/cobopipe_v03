#target.aftereffects

function Run(){
	//Try to find episode and shot number from scene name
	//var base_path = "P:/_WFH_Projekter/930448_MSP_academy/Film/";
	//var watchfolder_path = "P:/_WFH_Projekter/930448_MSP_academy/Film/WatchFolder/";
    
    var split_path = app.project.file.path.split("/Comp");
    var base_path = split_path[0];
    
    
	var comp_name = ".RENDER";
	var output_module = "Comp_Render";
	//split filename to find episode and shot number
    var shot_name = base_path.split("/");
    shot_name = shot_name[shot_name.length-1];

    render_path = base_path + "/_CompOutput/";
    render_path_folder = new Folder(render_path);
    var file_name = shot_name + "_CompOutput";
    alert("render_path: " + render_path + "\nFilename:" + file_name);
	//var file_name = shot  + "_[####]"; //USE FOR FRAME STACKS
    
	//var episode_name = "E"+ Pad(scene,3);
	//var shot_name = Pad(cur_shot,3);
	var render_comp = FindOutputComp(comp_name);

    
	if(render_comp){
		SetupRenderQueue(render_comp, render_path, file_name, output_module);
		}else{
			alert("Can't find '.RENDER' comp to render");
			}
}

function Pad(n, width, z) {
  z = z || '0';
  n = n + '';
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
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

function my_window(){
	var my_source = "window {text: 'Submit Deadline Job', alignChildren: 'left' , alignment: ['top','fill'],preferredSize: [400,150],\
			shot_panel: Panel {text: 'INFO:', \
				alignment:['fill','top'], alignChildren: 'left',\
				st2: StaticText{text: 'This script saves your file, so make sure you are okay with that before running it' ,},\
				st3: StaticText{text: 'Make sure you have an output module called Comp_Render, as this scripts assigns it to render' ,},\
				}\
			queue_panel: Panel {text: 'Click to send .Render to renderQueue : ', alignChildren: 'left' ,\
				buttonQ_group: Group{ orientation:'row', runQ_button: Button{ text: 'Run'},},\
			} \
		}";
		
	var my_window = new Window(my_source);
	my_window.queue_panel.buttonQ_group.runQ_button.onClick = Run;

	return my_window;
}
import_UI = my_window();
import_UI.show();
//LoadWindow(import_UI);
