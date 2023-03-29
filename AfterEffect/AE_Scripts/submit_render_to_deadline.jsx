#target.aftereffects;
#include "includes/config.jsx";

function Run(){
	// FETCHING CONFIG
	var config = get_config();
    
	// PREPARING RENDER QUEUE
    var split_path = app.project.file.path.split("/Comp");
    var base_path = split_path[0];
	var comp_name = ".RENDER";
	var output_module = "Comp_Render";
    var shot_name = base_path.split("/");
    shot_name = shot_name[shot_name.length-1];
    render_path = base_path + "/_CompOutput/";
    render_path_folder = new Folder(render_path);
    var file_name = shot_name + "_CompOutput";
	var render_comp = FindOutputComp(comp_name);
	if(render_comp){
		SetupRenderQueue(render_comp, render_path, file_name, output_module);
		}else{
			alert("Can't find '.RENDER' comp to render");
			}
	app.project.save() 


	// SUBMIT TO DEADLINE
	var deadlineBin = $.getenv( "DEADLINE_PATH" );
	var deadline_exe = "\"" + deadlineBin + "\\deadlinecommand.exe\"";
	var commandLine = deadline_exe + " GetCurrentUserHomeDirectory";
	var deadline_home = system.callSystem(commandLine).replace("\r","").replace("\n","");
	var temp_folder = deadline_home + "\\temp\\";
	Folder( temp_folder ).create();
	renderQueueItem = app.project.renderQueue.item( 1 );
	var frameDuration = renderQueueItem.comp.frameDuration;
	var frameOffset = app.project.displayStartFrame;
	var displayStartTime = renderQueueItem.comp.displayStartTime;
	var start_frame = frameOffset + Math.round( displayStartTime / frameDuration ) + Math.round( app.project.renderQueue.item( 1 ).timeSpanStart / frameDuration );
	var end_frame = start_frame + Math.round( app.project.renderQueue.item( 1 ).timeSpanDuration / frameDuration ) - 1;
	var output_file = app.project.renderQueue.item(1).outputModule(1).file
	var jobname = app.project.file.fsName.split('\\')[app.project.file.fsName.split('\\').length-1].replace('.aep', '')
	var pool = null;
	var config_pool = config.project_settings.deadline_pool;
	if(config_pool != undefined){
		pool = config_pool
	}
	var submit_file = create_submit_job_file(temp_folder, jobname, pool, start_frame, end_frame, output_file);
	var plugin_file = create_plugin_job_file(temp_folder);
	commandLine = deadline_exe + " \"" + submit_file + "\" \"" + plugin_file +  "\" \"" + app.project.file.fsName + "\""
	result = system.callSystem(commandLine)
	alert(result)
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
				buttonQ_group: Group{ orientation:'row', runQ_button: Button{ text: 'Submit'},},\
			} \
		}";
		
	var my_window = new Window(my_source);
	my_window.queue_panel.buttonQ_group.runQ_button.onClick = Run;

	return my_window;
}

function create_submit_job_file(tempFolder, jobName, pool, start_frame, end_frame, output_file){
	// Create the submission info file
	// These settings are specific for hoj and prores
	var submitInfoFilename = tempFolder + "ae_submit_info.job";
	var submitInfoFile = File( submitInfoFilename );
	submitInfoFile.open( "w" );
	submitInfoFile.writeln( "Plugin=AfterEffects" );
	submitInfoFile.writeln( "Name=" + jobName );
	submitInfoFile.writeln( "Comment=" );
	submitInfoFile.writeln( "Department=Comp" );
	submitInfoFile.writeln( "Group=after_effects" );
	if(pool != null){
		submitInfoFile.writeln( "Pool=" + pool );
	}
	submitInfoFile.writeln( "SecondaryPool=" );
	submitInfoFile.writeln( "Priority=" + Math.round( 50 ) );
	submitInfoFile.writeln( "TaskTimeoutMinutes=" + Math.round( 0 ) );
	submitInfoFile.writeln( "LimitGroups=" );
	submitInfoFile.writeln( "ConcurrentTasks=" + Math.round( 1 ) );
	submitInfoFile.writeln( "LimitConcurrentTasksToNumberOfCpus=" + true );
	submitInfoFile.writeln( "JobDependencies=");
	submitInfoFile.writeln( "OnJobComplete=Nothing");
	submitInfoFile.writeln( "Whitelist=");
	submitInfoFile.writeln( "Frames=" + String(start_frame) + "-" + String(end_frame));
	submitInfoFile.writeln( "OutputFilename0=" + output_file.toString()); // .replace('/p/', '//dumpap3/production/')
	submitInfoFile.writeln( "MachineLimit=1");
	submitInfoFile.writeln( "ChunkSize=1000000");
	submitInfoFile.close();
		
	return submitInfoFilename;
}

function create_plugin_job_file(tempFolder){
	// create the plugin info file
	var pluginInfoFilename = tempFolder + "ae_plugin_info.job";
	var pluginInfoFile = new File( pluginInfoFilename );
	pluginInfoFile.open( "w" );
	//pluginInfoFile.writeln( "SceneFile=" + app.project.file.fsName);
	pluginInfoFile.writeln( "Comp=.RENDER" );
	float_version = app.version.substring( 0, app.version.indexOf( 'x' )).substring(0, getPosition(app.version, '.', 2))
	pluginInfoFile.writeln( "Version=" + float_version );
	pluginInfoFile.writeln( "SubmittedFromVersion=" + app.version );
	pluginInfoFile.writeln( "IgnoreMissingEffectReferencesErrors=false" );
	pluginInfoFile.writeln( "FailOnWarnings=false" );
	pluginInfoFile.writeln( "MinFileSize=1" );
	pluginInfoFile.writeln( "DeleteFilesUnderMinSize=True" );
	pluginInfoFile.writeln( "OverrideFailOnExistingAEProcess=false" );
	pluginInfoFile.writeln( "FailOnExistingAEProcess=false" );
	pluginInfoFile.writeln( "MemoryManagement=false" );
	pluginInfoFile.writeln( "ImageCachePercentage=100" );
	pluginInfoFile.writeln( "MaxMemoryPercentage=100" );
	pluginInfoFile.writeln( "MultiProcess=false" );
	pluginInfoFile.writeln( "ContinueOnMissingFootage=false" );	
	pluginInfoFile.close();

	return pluginInfoFilename;
}

function getPosition(string, subString, index) {
  return string.split(subString, index).join(subString).length;
}

import_UI = my_window();
import_UI.show();
