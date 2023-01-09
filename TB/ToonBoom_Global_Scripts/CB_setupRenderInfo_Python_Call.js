function run_setupRenderInfo_Python(){
    var myPythonObject = PythonManager.createPyObject(System.getenv("BOM_PIPE_PATH")+"/TB/CB_SetupRenderInfo_Python.py");
    myPythonObject.py.run();
    }