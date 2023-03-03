function SetLineThickness(){
    var myPythonObject = PythonManager.createPyObject(System.getenv("BOM_PIPE_PATH")+"/TB/CB_SetLineThickness.py");
    //myPythonObject.setObject("js_select",subselection_obj);
    myPythonObject.py.run();
    }