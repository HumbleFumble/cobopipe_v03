import sys
from TB.ToonBoom_Global_Python.Harmony_RR_RenderSubmit import RenderSubmitInfo

"""
A catcher script to redirect a call from toonboom to the right script -> ToonBoom_RR_Submit

# Harmony calling commands
# var cur_full_path = scene.currentProjectPath() + ".xstage"
# MessageLog.trace(cur_full_path);

# p1 = new Process2("python", "P:\\tools\\_Scripts\\toonboom_scripts\\_InHouse\\ToonBoom_RR_Submit_Call.py", cur_full_path );
# p1.launchAndDetach();

"""
# def SaveFile(arg1,arg2=False,arg3="Test",arg4="Test4"):
#     f = "C:/Temp/TB_Test.txt"
#     fo = open(f,"w")
#     fo.write(arg1)
#     if arg2 and arg2 != "False":
#         fo.write(my_args[2])
#     fo.write(arg3)
#     fo.write(arg4)
#     # my_string = str(my_args[1:])
#     # fo.write("Test: " + my_string)
#     fo.close()

my_args = sys.argv
# SaveFile(*my_args[1:])

RenderSubmitInfo(*my_args[1:])