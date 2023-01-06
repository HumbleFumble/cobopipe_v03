//JavaScript file
function pythonScripting()
{
  var myPythonObject = PythonManager.createPyObject("/python/DemoUI.py");

  myPythonObject.addObject("messageLog",MessageLog);
  myPythonObject.addObject("pythonManager",PythonManager);

  myPythonObject.py.createUI();
 }