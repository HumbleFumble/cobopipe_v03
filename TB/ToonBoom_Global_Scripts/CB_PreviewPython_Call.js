function PreviewPythonRun(){
    var script_name = "CB_SetLineThickness.py";

    var local_folder = specialFolders.userScripts
    var script_path = local_folder + "/" + script_name
    MessageLog.trace("Checking local path: " + script_path)
    var file = new File( script_path );
    if ( file.exists ){
        MessageLog.trace("Found script at local path. Running now: " + script_name)
        var myPythonObject = PythonManager.createPyObject(script_path);
    }else{
        MessageLog.trace("No local script. Looking for a global script location")
        var server_script_path = System.getenv("BOM_PIPE_PATH")
        if(server_script_path){
            MessageLog.trace("Found script at global path. Running now: " + script_name)
            var myPythonObject = PythonManager.createPyObject(server_script_path +"/TB/CB_PreviewPython.py");
        }else{
            MessageLog.trace("Can't find python file to load. Stopping Execution of: " + script_name)
            return 0
        }
    }

    myPythonObject.setObject("js_exporter",exporter);
    myPythonObject.py.run();
}
