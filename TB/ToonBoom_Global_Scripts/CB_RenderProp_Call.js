function run_setupRenderInfo_Python_render_prop(){
    var myPythonObject = PythonManager.createPyObject(System.getenv("BOM_PIPE_PATH")+"/TB/CB_SetupRenderInfo_Python.py");
    myPythonObject.py.render_prop();
    }