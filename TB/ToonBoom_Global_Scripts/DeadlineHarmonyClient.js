submissionDir = callDeadlineCommand( ["-GetRepositoryPath", "submission/Harmony/Main"] )
scriptPath = trim(submissionDir) + "/SubmitHarmonyToDeadline.js";

MessageLog.trace("This is here: " + submissionDir)

include( scriptPath );

function callDeadlineCommand( args )
{
	var commandLine = "";
	var deadlineBin = "";
	
	deadlineBin = System.getenv( "DEADLINE_PATH" )
	if( ( deadlineBin === null || deadlineBin == "" ) && about.isMacArch() )
	{
		//var file = new File( "/Users/Shared/Thinkbox/DEADLINE_PATH" );
		var file = new File( "C:/Temp/Deadline10/DEADLINE_PATH" );
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
	//commandArgs[commandArgIndex++] = commandLine;
	for( arg in args)
	{
		commandArgs[commandArgIndex++] = args[arg];
	}
	MessageLog.trace(commandLine)
	MessageLog.trace(String(typeof(commandArgs)))
	var result = runQprocess(commandLine,commandArgs)
	//var status = new Process2("ipconfig");

	//status = testQprocess("ipconfig",[])


	// var status = Process.execute(commandArgs);
	// var mOut = Process.stdout;
//	var mOut = status.launch();
//	var result = mOut;
	return result;
}

function runQprocess(call,list_of_args)
{
   var p1 = new QProcess;
   //var bin = "/bin/ls";
   //var args = ["-la"];
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
	
function SubmitToDeadline()
{	
	if (typeof InnerSubmitToDeadline === 'undefined') 
	{
		MessageBox.information( "Failed to import Deadline" );
	}
	else
	{
		InnerSubmitToDeadline( submissionDir );
	}
	
}

function testRun(){
    status = runQprocess("ipconfig")
}