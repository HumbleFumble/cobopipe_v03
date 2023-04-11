include("CB_GetInfo.js")
include("CB_SetupRenderInfo_Pathless.js")


function submit(){
    SetupRenderInfo_NoRender();
    scene.saveAll();
    var project_settings = GetProjectSettings();

    var jobName = scene.currentVersionName();
    var group = 'harmony';
    var pool = project_settings['deadline_pool'];
    var priority = 50;
    var frameList = scene.getStartFrame() + '-' + scene.getStopFrame();
    var chunkSize = 100;

    var versionRegex = / (\d+)\.\d+\.\d/;
    var versionInformation = about.getVersionInfoStr();
    var matches = versionInformation.match( versionRegex );
    var version = matches[1];
    var sceneFile = scene.currentProjectPath() + "/" + scene.currentVersionName() + ".xstage";
    var resolutionX = scene.currentResolutionX();
	var resolutionY = scene.currentResolutionY();
	var resolutionFov = scene.defaultResolutionFOV();
    var camera =  node.getDefaultCamera();

    tempFolder = callDeadlineCommand( ["-GetCurrentUserHomeDirectory"] )
    MessageLog.trace( "Temp Folder: " + tempFolder )
    tempFolder = trim( tempFolder )
    if (about.isMacArch() || about.isLinuxArch() )
        tempFolder = tempFolder + "/temp/";
    else
        tempFolder = tempFolder + "\\temp\\";

    jobInfoFile(tempFolder, jobName, group, pool, priority, frameList, chunkSize);
    pluginInfoFile(tempFolder, version, sceneFile, resolutionX, resolutionY, resolutionFov, camera);

    var renderArguments = [];
    var renderArgCount = 0;
    renderArguments[renderArgCount++] = jobInfoFilePath;
    renderArguments[renderArgCount++] = pluginInfoFilePath;
    
    var results = callDeadlineCommand(renderArguments);
}


function jobInfoFile(tempFolder, jobName, group, pool, priority, frameList, chunkSize){
    jobInfoFilePath = tempFolder + "harmony_submit_info.job";
    var jobInfoFile = new File( jobInfoFilePath );
    jobInfoFile.open(FileAccess.WriteOnly);
    jobInfoFile.writeLine( "Plugin=Harmony" );
    jobInfoFile.writeLine( "Name=" + jobName );
    // jobInfoFile.writeLine( "Comment=" + comment );
    // jobInfoFile.writeLine( "Department=" + department );
    
    jobInfoFile.writeLine( "Group=" + group );
    if(pool != undefined){
        jobInfoFile.writeLine( "Pool=" + pool );
    }
    // jobInfoFile.writeLine( "SecondaryPool=" + secondaryPool );
    jobInfoFile.writeLine( "Priority=" + priority );
    // jobInfoFile.writeLine( "TaskTimeoutMinutes=" + taskTimeout );
    // jobInfoFile.writeLine( "LimitGroups=" + limitGroups );
    // jobInfoFile.writeLine( "ConcurrentTasks=" + concurrentTasks );
    // jobInfoFile.writeLine( "JobDependencies=" + jobDependencies );
    // jobInfoFile.writeLine( "OnJobComplete=" + onComplete );
    jobInfoFile.writeLine( "Frames=" + frameList );
    // jobInfoFile.writeLine( "MachineLimit=" + machineLimit );
    jobInfoFile.writeLine( "ChunkSize=" + chunkSize );

    var n = node.numberOfSubNodes("Top");
    var root = node.root();
    var name;
    var outputNum = 0;
    for(i = 0; i < n; ++i)
    {
        name = node.subNode(root, i);

        if(node.type(name) == "WRITE")
        {
            var exportType = node.getTextAttr( name, 1, "exportToMovie" );
            if( exportType == "Output Drawings" ||exportType == "OutputMovieAndKeepFrames" )
            {
                var outputPath = node.getTextAttr( name, 1, "drawingName" );
                var paddingLength = node.getTextAttr( name, 1, "leadingZeros" );
                var drawingType = node.getTextAttr( name, 1, "drawingType" )
                
                outputPath = modifyOutputPaths( outputPath );
                drawingType = drawingType.toLowerCase()
                for(h = 0; h <= paddingLength; ++h )
                {
                    outputPath = outputPath + "#";
                }
                
                //Drawing types are the output file formats that are used when rendering for example "TGA1", "scan", "tvg" "PSDDP4"
                //the file extension is always the first 3 letters with the exception of scan.
                if( drawingType  == "scan" )
                {
                    outputPath = outputPath + "." + drawingType;
                }
                else
                {
                    outputPath = outputPath + "." + drawingType.substr(0, 3);
                }
                
                jobInfoFile.writeLine("OutputFilename"+outputNum+"=" +outputPath );
                
                outputNum++;
            }
            
            if( exportType == "Output Movie" ||exportType == "OutputMovieAndKeepFrames" )
            {
                var outputPath = node.getTextAttr( name, 1, "moviePath" );
                outputPath = modifyOutputPaths( outputPath );
                jobInfoFile.writeLine("OutputFilename"+outputNum+"=" +outputPath+".mov" );
                outputNum++;
            }
        }
    }

    jobInfoFile.close();
}

// Camera=Camera
// FieldOfView=31.42
// IsDatabase=False
// Output0Format=TGA4
// Output0LeadingZero=3
// Output0Node=Top/RENDER_BaseFile
// Output0Path=P:/930462_HOJ_Project/Production/Film/S100/S100_SQ010/S100_SQ010_SH030/Passes/BaseFile_
// Output0StartFrame=1
// Output0Type=Image
// ProjectPath=P:/930462_HOJ_Project/Production/Film/S100/S100_SQ010/S100_SQ010_SH030/S100_SQ010_SH030
// ResolutionX=2112
// ResolutionY=1188
// SceneFile=P:/930462_HOJ_Project/Production/Film/S100/S100_SQ010/S100_SQ010_SH030/S100_SQ010_SH030/S100_SQ010_SH030.xstage
// UsingResPreset=false
// Version=22

function pluginInfoFile(tempFolder, version, sceneFile, resolutionX, resolutionY, resolutionFov, camera){
    pluginInfoFilePath = tempFolder + "harmony_plugin_info.job"
    var pluginInfoFile = new File( pluginInfoFilePath );
    pluginInfoFile.open(FileAccess.WriteOnly);
    pluginInfoFile.writeLine("Version=" + version);
    
    pluginInfoFile.writeLine("ProjectPath=" + scene.currentProjectPath());
    pluginInfoFile.writeLine("IsDatabase=False");
    pluginInfoFile.writeLine("SceneFile="+ sceneFile );
    pluginInfoFile.writeLine("UsingResPreset=False");
    pluginInfoFile.writeLine("ResolutionX=" + resolutionX);
    pluginInfoFile.writeLine("ResolutionY=" + resolutionY);
    pluginInfoFile.writeLine("FieldOfView=" + resolutionFov);
    pluginInfoFile.writeLine("Camera=" + camera);
    
    var n = node.numberOfSubNodes("Top");
    var root = node.root();
    var name;
    var outputNum = 0;
    for(i = 0; i < n; ++i)
    {
        name = node.subNode(root, i);

        if(node.type(name) == "WRITE")
        {
            var exportType = node.getTextAttr( name, 1, "exportToMovie" );
            if( exportType == "Output Drawings" ||exportType == "OutputMovieAndKeepFrames" )
            {
                var outputPath = node.getTextAttr( name, 1, "drawingName" );
                var paddingLength = node.getTextAttr( name, 1, "leadingZeros" );
                var drawingType = node.getTextAttr( name, 1, "drawingType" )
                var startFrame = node.getTextAttr( name, 1, "start" )
                pluginInfoFile.writeLine("Output" + outputNum + "Node=" + name);
                pluginInfoFile.writeLine("Output" + outputNum + "Type=Image");
                pluginInfoFile.writeLine("Output" + outputNum + "Path=" + outputPath );
                pluginInfoFile.writeLine("Output" + outputNum + "LeadingZero=" + paddingLength );
                pluginInfoFile.writeLine("Output" + outputNum + "Format=" + drawingType );
                pluginInfoFile.writeLine("Output" + outputNum + "StartFrame=" + startFrame );
                
                outputNum++;
            }
            
            if( exportType == "Output Movie" ||exportType == "OutputMovieAndKeepFrames" )
            {
                var outputPath = node.getTextAttr( name, 1, "moviePath" );
                pluginInfoFile.writeLine("Output" + outputNum + "Node=" + name);
                pluginInfoFile.writeLine("Output" + outputNum + "Type=Movie");
                pluginInfoFile.writeLine("Output" + outputNum + "Path=" + outputPath );
                outputNum++;
            }
        }
    }
    
    pluginInfoFile.close();
}


function callDeadlineCommand( args )
{
	var commandLine = "";
	var deadlineBin = "";
	
	deadlineBin = System.getenv( "DEADLINE_PATH" )
	if( ( deadlineBin === null || deadlineBin == "" )  && about.isMacArch() )
	{
		var file = new File( "/Users/Shared/Thinkbox/DEADLINE_PATH" );
		file.open(FileAccess.ReadOnly);
		deadlineBin = file.read();
		file.close();
	}
		
	if( deadlineBin === null || deadlineBin == "" )
	{
		commandLine = "deadlinecommand";
	}
	else
	{
		deadlineBin = trim(deadlineBin);
		commandLine = deadlineBin + "/deadlinecommand";
	}
	
	commandArgs = [];
	commandArgIndex = 0;
//	commandArgs[commandArgIndex++] = commandLine;
	for( arg in args)
	{
		commandArgs[commandArgIndex++] = args[arg];
	}
//	var status = Process.execute(commandArgs);
//	var mOut = Process.stdout;
//
//	var result = mOut;
    MessageLog.trace("CommandLine: " + commandLine )
    MessageLog.trace("CommandArgs: " + commandArgs )
    var result = runQprocess(commandLine,commandArgs)
    MessageLog.trace("Result: " + result)
	return result;
}


function runQprocess(call,list_of_args)
{
   var p1 = new QProcess;
   //var bin = "/bin/ls";
   //var args = ["-la"];
   var new_env = new QProcessEnvironment()
   os_var = ["PATH","DEADLINE_PATH","SYSTEMROOT","SYSTEMDRIVE"]
	for(i=0;i<os_var.length;i++){
	    new_env.insert(os_var[i],System.getenv(os_var[i]))
    }
   p1.setProcessEnvironment(new_env)
   p1.start(call,list_of_args);
   p1.waitForFinished();
   var stdout = p1.readAllStandardOutput();
   var stderr = p1.readAllStandardError();
   var textStreamStdout = new QTextStream(stdout);
   var textStreamStderr = new QTextStream(stderr);

//If you need to do some string replacement
//var response = textStreamStdout.readAll().replace(/\r?\n|\r/g, "");
//var response = textStreamStdout.readAll().replace(/\r?\n|\r/g, "");

   var resStdOut = textStreamStdout.readAll();
   var resStdErr = textStreamStderr.readAll();
   if(resStdErr){
   MessageLog.trace("Error: " + resStdErr)
   }
//   MessageLog.trace("STDOUT: \n" + resStdOut);
//   MessageLog.trace("STDERR: \n" + resStdErr);
//   MessageLog.trace("Done");
   return resStdOut
}


function trim(string)
{
	return string
		.replace( "\n","" )
		.replace( "\r", "" )
		.replace( "^\s+", "" )
		.replace( "\s+$");
}


function modifyOutputPaths( path )
{
	path = path.replace( "\\", "/" );
	var results = "";
	
	if( about.isWindowsArch() && ( path.indexOf( ":/" ) == 1 ||  path.indexOf( "//" ) == 0 ) )
	{
		results = path;
	}
	else if( !about.isWindowsArch() && path.indexOf( "/" ) == 0 )
	{
		results = path;
	}
	else
	{
		results = scene.currentProjectPath()+"/"+path;
	}
	return results;	

}