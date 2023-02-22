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
    // alert("render_path: " + render_path + "\nFilename:" + file_name);
	//var file_name = shot  + "_[####]"; //USE FOR FRAME STACKS
    
	//var episode_name = "E"+ Pad(scene,3);
	//var shot_name = Pad(cur_shot,3);
	var render_comp = FindOutputComp(comp_name);

    
	if(render_comp){
		SetupRenderQueue(render_comp, render_path, file_name, output_module);
		}else{
			alert("Can't find '.RENDER' comp to render");
			}

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
	var submit_file = create_submit_job_file(temp_folder, '.RENDER', start_frame, end_frame, output_file);
	var plugin_file = create_plugin_job_file(temp_folder);

	commandLine = deadline_exe + " \"" + submit_file + "\" \"" + plugin_file + "\" \"" + app.project.file.fsName + "\""
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

function create_submit_job_file(tempFolder, jobName, start_frame, end_frame, output_file){
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
	submitInfoFile.writeln( "Pool=hoj" );
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
	submitInfoFile.writeln( "OutputFilename0=" + output_file.toString());
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
	pluginInfoFile.writeln( "SceneFile=" + app.project.file.fsName);
	pluginInfoFile.writeln( "Comp=.RENDER" );
	pluginInfoFile.writeln( "Version=" + app.version.substring( 0, app.version.indexOf( 'x' ) ) );
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

// function getDeadlineTemp()
// {
// 	var tempFolder = callDeadlineCommand( "GetCurrentUserHomeDirectory" ).replace("\r","").replace("\n","");
// 	if (system.osName == "MacOS")
// 		tempFolder = tempFolder + "/temp/";
// 	else
// 		tempFolder = tempFolder + "\\temp\\";
// 	Folder( tempFolder ).create();
// 	return tempFolder;
// }

// //Calls deadline with the given arguments.  Checks the OS and calls DeadlineCommand appropriately.
// function callDeadlineCommand( args, removeNewLineChars )
// {
// 	var commandLine = "";
	
// 	deadlineBin = $.getenv("DEADLINE_PATH")
// 	if( (deadlineBin === null || deadlineBin == "") && (system.osName == "MacOS" ))
// 	{
// 		deadlineBin = system.callSystem("cat /Users/Shared/Thinkbox/DEADLINE_PATH");
// 	}
	
// 	deadlineBin = trim(deadlineBin);
// 	//On OSX, we look for the DEADLINE_PATH file. On other platforms, we use the environment variable.
// 	if (deadlineBin == "" )
// 	{
// 		commandLine =  "\"deadlinecommand\" "
// 	}
// 	else
// 	{
// 		if (system.osName == "MacOS")
// 		{
// 			commandLine = "\"" + deadlineBin + "/deadlinecommand\" ";
// 		}
// 		else
// 		{
// 			commandLine = "\"" + deadlineBin + "\\deadlinecommand.exe\" ";
// 		}
// 	}
	
// 	commandLine = commandLine + args;
	
// 	result = system.callSystem(commandLine);
	
// 	if( system.osName == "MacOS" )
// 	{
// 		result = cleanUpResults( result, "Could not set X local modifiers" );
// 		result = cleanUpResults( result, "Could not find platform independent libraries" );
// 		result = cleanUpResults( result, "Could not find platform dependent libraries" );
// 		result = cleanUpResults( result, "Consider setting $PYTHONHOME to" );
// 		result = cleanUpResults( result, "using built-in colorscheme" );
// 	}
// 	else
// 	{
// 		result = cleanUpResults( result, "Qt: Untested Windows version 10.0 detected!" );
// 	}
	
// 	removeNewLineChars = ( typeof removeNewLineChars != 'undefined' ) ? removeNewLineChars : false;
// 	if (removeNewLineChars)
// 	{
// 		result = result.replace( "\n", "" );
// 		result = result.replace( "\r", "" );
// 	}

// 	return result;
// }

// // Looks for the given txt in result, and if found, that line and all previous lines are removed.
// function cleanUpResults( result, txt )
// {
// 	newResult = result;
	
// 	txtIndex = result.indexOf( txt );
// 	if( txtIndex >= 0 )
// 	{
// 		eolIndex = result.indexOf( "\n", txtIndex );
// 		if( eolIndex >= 0 )
// 			newResult = result.substring( eolIndex + 1 );
// 	}
	
// 	return newResult;
// }

// function trim( stringToTrim )
// {
// 	return stringToTrim.replace( /^\s+|\s+$/g, "" );
// }

import_UI = my_window();
import_UI.show();
//LoadWindow(import_UI);
