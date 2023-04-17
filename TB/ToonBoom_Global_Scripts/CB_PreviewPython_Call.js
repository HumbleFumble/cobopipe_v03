var script_path = System.getenv("BOM_PIPE_PATH")
var myPythonObject = PythonManager.createPyObject(script_path +"/TB/CB_SelectionPreset.py");
myPythonObject.setObject("js_exporter",exporter);
myPythonObject.py.run();
