#target.aftereffects

function Run(use_watchfolder){
	//Try to find episode and shot number from scene name
	//var base_path = "P:/_WFH_Projekter/930448_MSP_academy/Film/";
	//var watchfolder_path = "P:/_WFH_Projekter/930448_MSP_academy/Film/WatchFolder/";
    
    var split_path = app.project.file.path.split("03_Comp");
    var base_path = split_path[0];
    var watchfolder_path = base_path.split("Film")[0] + "/Film/" + "WatchFolder/";
    
    
	var comp_name = ".RENDER";
	var output_module = "Comp_Render";
	//split filename to find episode and shot number
    var filename = app.project.file.name;
    if(filename.search("_Precomp") >=0){
       var cur_name = filename.split("_Precomp");
    }else{
    	var cur_name = filename.split("_Comp");
    }
 
	var shot = cur_name[0];
	//var render_path = split_path[0] + "/05_CompOutput/";
    var sequence_folder = base_path.split("/");
    sequence_folder.pop();
    sequence_folder.pop();
    sequence_folder = sequence_folder.join("/");
    
    render_path = sequence_folder + "/_CompOutput/";
    
	var project_name = shot  + "_Comp";
    var file_name = shot + "_CompOutput";
    alert("render_path: " + render_path + "\nFilename:" + file_name);
	//var file_name = shot  + "_[####]"; //USE FOR FRAME STACKS
    
	//var episode_name = "E"+ Pad(scene,3);
	//var shot_name = Pad(cur_shot,3);
	var render_comp = FindOutputComp(comp_name);
	var check = import_UI.watch_panel.run_box.value;
	if(render_comp){
		SetupRenderQueue(render_comp, render_path, file_name, output_module);
		if(use_watchfolder){
            var watchfolder = new Folder(watchfolder_path);
            if(!watchfolder.exists){watchfolder.create();}
            CreateWatchfolderProject(project_name, watchfolder_path,check);
            }
		}else{
			alert("Can't find '.RENDER' comp to render");
			}
}
function Run_Queue(){
	Run( false);
	}
function Run_Watch(){
	Run( true);
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


function CreateWatchfolderProject(project_name, watchfolder_path,reopen){
	var cur_project = new File(app.project.file);
	app.project.save(cur_project);
	var text_string = 'After Effects 13.2v1 Render Control File\nmax_machines=10\nnum_machines=0\ninit=0\nhtml_init=0\nhtml_name=""';
	var folder_path = watchfolder_path + project_name + "/";
	var text_name = project_name + "_RCF.txt";

	var project_folder = new Folder(folder_path);
	if(!project_folder.exists){project_folder.create();}

	var text_path = new File(folder_path + text_name);
	text_path.open("w");
	text_path.write(text_string);
	text_path.close();

	project_file = new File(folder_path + project_name + ".aep");
	app.project.save(project_file);
	if(reopen){
		app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
		app.open(cur_project);
		}else{
			app.project.close(CloseOptions.DO_NOT_SAVE_CHANGES);
			app.newProject();
			}
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
	var my_source = "window {text: 'Send To Watchfolder', alignChildren: 'left' , alignment: ['top','fill'],preferredSize: [400,150],\
			shot_panel: Panel {text: 'INFO:', \
				alignment:['fill','top'], alignChildren: 'left',\
				st: StaticText{text: 'Looks for a composition called: .RENDER and assigns that to be rendered using watchfolder.' ,},\
				st2: StaticText{text: 'This script saves your file, so make sure you are okay with that before running it' ,},\
				st3: StaticText{text: 'Make sure you have an output module called Comp_Render, as this scripts assigns it to render' ,},\
				}\
			queue_panel: Panel {text: 'Click to send .RENDER to renderQueue : ', alignChildren: 'left' ,\
				buttonQ_group: Group{ orientation:'row', runQ_button: Button{ text: 'Run'},},\
			} \
			watch_panel: Panel {text: 'Click to send to project to watchfolder : ', alignChildren: 'left' ,\
				buttonW_group: Group{ orientation:'row', runW_button: Button{ text: 'Run'},},\
				run_box: Checkbox{text: ': reopen this file after script has run', value: true}\
			} \
		}";
		
	var my_window = new Window(my_source);
	my_window.queue_panel.buttonQ_group.runQ_button.onClick = Run_Queue;
	my_window.watch_panel.buttonW_group.runW_button.onClick = Run_Watch;
	/*my_window.onClose = function(){
	SaveWindow(my_window);
	}*/
	return my_window;
}
import_UI = my_window();
import_UI.show();
//LoadWindow(import_UI);