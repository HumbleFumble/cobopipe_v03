function PreviewPythonRun(){
var script_path = System.getenv("BOM_PIPE_PATH")
var myPythonObject = PythonManager.createPyObject(script_path +"/TB/CB_PreviewPython.py");
myPythonObject.setObject("js_exporter",exporter);
myPythonObject.py.run();
}
