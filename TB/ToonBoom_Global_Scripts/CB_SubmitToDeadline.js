
sceneFile = scene.currentProjectPath() +"/"+ scene.currentVersionName()+".xstage";

function SaveDeadlineJobInfoFile(file_path,jobName,group,pool,start_frame,end_frame,chunkSize,output_dir){

    jobInfoFilePath = file_path+"harmony_submit_info.job"
    var jobInfoFile = new File( jobInfoFilePath );
    jobInfoFile.open(FileAccess.WriteOnly);
    jobInfoFile.writeLine("Plugin=Harmony")
    jobInfoFile.writeLine( "Name=" + jobName );
    //jobInfoFile.writeLine( "Comment=" + comment );
    //jobInfoFile.writeLine( "Department=" + department );

    jobInfoFile.writeLine( "Group=" +group );
    jobInfoFile.writeLine( "Pool=" +pool );
//    jobInfoFile.writeLine( "SecondaryPool=" +secondaryPool );
//    jobInfoFile.writeLine( "Priority=" +priority );
//    jobInfoFile.writeLine( "TaskTimeoutMinutes=" +taskTimeout );
//    jobInfoFile.writeLine( "LimitGroups=" + limitGroups );
//    jobInfoFile.writeLine( "ConcurrentTasks=" + concurrentTasks );
//    jobInfoFile.writeLine( "JobDependencies=" + jobDependencies );
//    jobInfoFile.writeLine( "OnJobComplete=" + onComplete );
    jobInfoFile.writeLine( "Frames=" + start_frame + "-" + end_frame); //jobInfoFile.writeLine( "Frames=" + frameList );
//    jobInfoFile.writeLine( "MachineLimit=" + machineLimit );
    jobInfoFile.writeLine( "ChunkSize=" + chunkSize );
    jobInfoFile.writeLine( "OutputDirectory0=" + output_dir );
//    if( isBlacklist )
//        jobInfoFile.writeLine( "Blacklist=" + machineList );
//    else
//        jobInfoFile.writeLine( "Whitelist=" + machineList );
//
//    if( submitSuspended )
//        jobInfoFile.writeLine( "InitialStatus=Suspended" );
//
//    var n = node.numberOfSubNodes("Top");
//    var root = node.root();
//    var name;
//    var outputNum = 0;
//    for(i = 0; i < n; ++i)
//    {
//        name = node.subNode(root, i);
//
//        if(node.type(name) == "WRITE")
//        {
//            var exportType = node.getTextAttr( name, 1, "exportToMovie" );
//            if( exportType == "Output Drawings" ||exportType == "OutputMovieAndKeepFrames" )
//            {
//                var outputPath = node.getTextAttr( name, 1, "drawingName" );
//                var paddingLength = node.getTextAttr( name, 1, "leadingZeros" );
//                var drawingType = node.getTextAttr( name, 1, "drawingType" )
//
//                outputPath = modifyOutputPaths( outputPath );
//                drawingType = drawingType.toLowerCase()
//                for(h = 0; h <= paddingLength; ++h )
//                {
//                    outputPath = outputPath + "#";
//                }
//
//                //Drawing types are the output file formats that are used when rendering for example "TGA1", "scan", "tvg" "PSDDP4"
//                //the file extension is always the first 3 letters with the exception of scan.
//                if( drawingType  == "scan" )
//                {
//                    outputPath = outputPath + "." + drawingType;
//                }
//                else
//                {
//                    outputPath = outputPath + "." + drawingType.substr(0, 3);
//                }
//
//                jobInfoFile.writeLine("OutputFilename"+outputNum+"=" +outputPath );
//
//                outputNum++;
//            }
//
//            if( exportType == "Output Movie" ||exportType == "OutputMovieAndKeepFrames" )
//            {
//                var outputPath = node.getTextAttr( name, 1, "moviePath" );
//                outputPath = modifyOutputPaths( outputPath );
//                jobInfoFile.writeLine("OutputFilename"+outputNum+"=" +outputPath+".mov" );
//                outputNum++;
//            }
//        }
//    }

    jobInfoFile.close();
    return jobInfoFilePath
}
function SavePluginFile(plugin_path,version,resolutionX,resolutionY,resolutionFov){
    pluginInfoFilePath = plugin_path+"harmony_plugin_info.job"
    var pluginInfoFile = new File( pluginInfoFilePath );
    pluginInfoFile.open(FileAccess.WriteOnly);
    pluginInfoFile.writeLine("Version="+version);
    pluginInfoFile.writeLine("ProjectPath="+scene.currentProjectPath());

//    if( isDB )
//    {
//        pluginInfoFile.writeLine("IsDatabase=True");
//        pluginInfoFile.writeLine("Environment="+env);
//        pluginInfoFile.writeLine("Job="+job);
//        pluginInfoFile.writeLine("SceneName="+sceneName);
//        pluginInfoFile.writeLine("SceneVersion="+sceneVersion);
//
//    }
//    else
//    {
    pluginInfoFile.writeLine("IsDatabase=False");
    pluginInfoFile.writeLine("SceneFile="+sceneFile);
//    }

//    pluginInfoFile.writeLine("UsingResPreset="+useResName);
//    if( useResName )
//    {
//        pluginInfoFile.writeLine("ResolutionName="+resolutionName);
//        if( resolutionName == "Custom" )
//        {
//            pluginInfoFile.writeLine("PresetName="+presetName);
//        }
//    }
//    else
//    {
    pluginInfoFile.writeLine("ResolutionX="+resolutionX);
    pluginInfoFile.writeLine("ResolutionY="+resolutionY);
    pluginInfoFile.writeLine("FieldOfView="+resolutionFov);
//    }

    //pluginInfoFile.writeLine("Camera="+camera);

//    var n = node.numberOfSubNodes("Top");
//    var root = node.root();
//    var name;
//    var outputNum = 0;
    n = GroupTravel("Top","WRITE", "RENDER_")
    for(i = 0; i < n.length; i++)
    {

        //name = node.subNode("Top", n[i]);
        name = n[i]
        MessageLog.trace(name)
//        if(node.type(name) == "WRITE")
//        {
//            var exportType = node.getTextAttr( name, 1, "exportToMovie" );
//            if( exportType == "Output Drawings" ||exportType == "OutputMovieAndKeepFrames" )
//            {
        var outputPath = node.getTextAttr( name, 1, "drawingName" );
        var paddingLength = node.getTextAttr( name, 1, "leadingZeros" );
        var drawingType = node.getTextAttr( name, 1, "drawingType" )
        var startFrame = node.getTextAttr( name, 1, "start" )
        pluginInfoFile.writeLine("Output"+i+"Node="+name);
        pluginInfoFile.writeLine("Output"+i+"Type=Image");
        pluginInfoFile.writeLine("Output"+i+"Path=" +outputPath );
        //pluginInfoFile.writeLine("Output"+i+"LeadingZero=" +paddingLength );
        //pluginInfoFile.writeLine("Output"+i+"Format=" +drawingType );
        //pluginInfoFile.writeLine("Output"+i+"StartFrame=" +startFrame );

//                outputNum++;
//            }

//            if( exportType == "Output Movie" ||exportType == "OutputMovieAndKeepFrames" )
//            {
//                var outputPath = node.getTextAttr( name, 1, "moviePath" );
//                pluginInfoFile.writeLine("Output"+outputNum+"Node="+name);
//                pluginInfoFile.writeLine("Output"+outputNum+"Type=Movie");
//                pluginInfoFile.writeLine("Output"+outputNum+"Path=" +outputPath );
//                outputNum++;
//            }
        }
    pluginInfoFile.close();
    return pluginInfoFilePath
    }


function GroupTravel(groupName,my_type,name_filter)
  {
    var node_list = []
    var nNodes = node.numberOfSubNodes(groupName);

    for( var i = 0; i < nNodes; i++)
    {
      var nodeName =  node.subNode( groupName, i );
      var type = node.type( nodeName );

       if (type == my_type ){
        if(nodeName.search(name_filter)>-1){
            node_list.push(nodeName)
            }
	}

      if ( type == "GROUP" ){
       new_list = GroupTravel( nodeName, my_type,name_filter );
       if(new_list){
        node_list = node_list.concat(new_list)
        }
      }
    }
    return node_list
  }


function runInTB(){
    job_path = "C:/Temp/TB_Submit_Test/"
    job_name = "Test"

    group = "harmony"
    pool = "hoj"
    version = "22"


    start_frame = "1"
    end_frame = "25"
    plugin_path = "C:/Temp/TB_Submit_Test/"
    submitScene = true
    resolutionX = scene.currentResolutionX();
    resolutionY = scene.currentResolutionY();
    resolutionFov = scene.defaultResolutionFOV();
    chunkSize = 50

    var scene_path = scene.currentProjectPath();
	var scene_path_split =scene_path.split("/");
	scene_path_split.pop();
	scene_path = scene_path_split.join("/") + "/Passes/";
    output_dir = scene_path //Path to the shot passes folder

    job_file = SaveDeadlineJobInfoFile(job_path,job_name,group,pool,start_frame,end_frame,chunkSize,output_dir)
    plug_file = SavePluginFile(plugin_path,version,resolutionX,resolutionY,resolutionFov)

    renderArguments = [];
    renderArgCount = 0;
    renderArguments[renderArgCount++] = job_file;
    renderArguments[renderArgCount++] = plug_file;
    if( submitScene )
        renderArguments[renderArgCount++] = sceneFile;

    MessageLog.trace(renderArguments)

    //"C:\Program Files\Thinkbox\Deadline10\bin\deadline.exe"
    }

//How to get info back frmo process in javascript harmony
function testQprocess()
{
   var p1 = new QProcess;
   var bin = "/bin/ls";
   var args = ["-la"];
   p1.start(bin,args);
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
   MessageLog.trace("STDOUT: \n" + resStdOut);
   MessageLog.trace("STDERR: \n" + resStdErr);
   MessageLog.trace("Done");
}