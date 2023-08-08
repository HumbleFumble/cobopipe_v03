function run_setupRenderInfo_Python(){
    var script_name = "CB_SetupRenderInfo_Python.py";

    var server_script_path = System.getenv("BOM_PIPE_PATH")

    if(server_script_path){
        MessageLog.trace("Found script at global path. Running now: " + script_name)
        var myPythonObject = PythonManager.createPyObject(server_script_path +"/TB/" + script_name);
    }else{
        var local_folder = specialFolders.userScripts
        var script_path = local_folder + "/" + script_name
        MessageLog.trace("Checking local path: " + script_path)
        var file = new File( script_path );
        if ( file.exists ){
            MessageLog.trace("Found script at local path. Running now: " + script_path)
            var myPythonObject = PythonManager.createPyObject(script_path);
            }else{
                MessageLog.trace("Can't find python file to load. Stopping Execution of: " + script_name)
                return null
            }
    }

    myPythonObject.py.run();
    }