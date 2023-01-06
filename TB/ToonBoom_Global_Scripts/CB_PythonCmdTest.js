function createTxt(){
	var p = "C:/Users/cg/PycharmProjects/bombay_base_production/Notes/TestToonboomCall.py";
	//p4 = new Process2("C:/Python27/python.exe", p);
	p4 = new Process2("python", p);
	p4.launchAndDetach();
	MessageLog.trace("WORKS?");
}