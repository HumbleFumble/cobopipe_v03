function Testing(){
	var pyObjects = PythonManager;
	Object.keys(pyObjects).forEach(function(k) {
  		MessageLog.trace("Loaded script : " + k);
	});
}


function call_CB_SelectionPreset(){
    var myPythonObject = PythonManager.createPyObject(System.getenv("BOM_PIPE_PATH")+"/TB/ToonBoom_Global_Packages/FirstUI/python/CB_SelectionPreset.py");
    myPythonObject.addObject("messageLog",MessageLog);
    myPythonObject.addObject("pythonManager",PythonManager);
    myPythonObject.py.run();
}
//
//function call_me(){
//	var myPythonObject = PythonManager.createPyObject(System.getenv("BOM_PIPE_PATH")+"/TB/ToonBoom_Global_Packages/FirstUI/python/BasicTreeViewTB.py");
//  myPythonObject.addObject("messageLog",MessageLog);
//  myPythonObject.addObject("pythonManager",PythonManager);
//  myPythonObject.py.run();
//}


//function harmonyPython(){
//    var myPythonObject = PythonManager.createPyObject(System.getenv("BOM_PIPE_PATH")+"/ToonBoom/ToonBoom_Global_Packages/FirstUI/python/HarmonyPython.py");
//    myPythonObject.addObject("messageLog",MessageLog);
//    myPythonObject.addObject("pythonManager",PythonManager);
//	//myPythonObject.wrapFunction(TB_SelectAll);
//  myPythonObject.py.run();
//}
//
//function demoUI(){
//    var myPythonObject = PythonManager.createPyObject(System.getenv("BOM_PIPE_PATH")+"/ToonBoom/ToonBoom_Global_Packages/FirstUI/python/DemoUI.py");
//    myPythonObject.addObject("messageLog",MessageLog);
//    myPythonObject.addObject("pythonManager",PythonManager);
//  myPythonObject.py.createUI();
//}