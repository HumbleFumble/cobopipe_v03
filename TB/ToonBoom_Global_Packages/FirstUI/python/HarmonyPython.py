import sys
sys.path.append( "C:/Program Files (x86)/Toon Boom Animation/Toon Boom Harmony 22 Premium/win64/bin/python-packages/")
from ToonBoom import harmony

def run_harmony():
    harmony.open_project("P:/930499_Borste_02/Production/Temp/UI_Testing_V001/UI_Testing_V001.xstage")

def run():
    current_session = harmony.session() #Fetch the currently active session of Harmony
    project = current_session.project   #The project that is already loaded.
    scene = project.scene
    # selection_handler = scene.selection.nodes[0].out_ports[0].link()
    select_all = scene.selection.select_all()
    print( "Current Project: %s"%(project.project_path) )

    # messageLog.trace("Current Project: %s"%(project.project_path) )

run_harmony()