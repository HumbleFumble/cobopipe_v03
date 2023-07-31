function SetLineThickness(){
    if(System.getenv("BOM_PIPE_PATH")){
	    var myPythonObject = PythonManager.createPyObject(System.getenv("BOM_PIPE_PATH")+"/TB/CB_SetLineThickness.py")
    }else{
		var myPythonObject = PythonManager.createPyObject(specialFolders.userScripts +"/CB_SetLineThickness.py")
    }
    //myPythonObject.setObject("js_select",subselection_obj);
    myPythonObject.py.run();
}