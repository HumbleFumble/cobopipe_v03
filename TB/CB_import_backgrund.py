import sys
import os
from Log.CoboLoggers import getLogger
logger = getLogger()

#Extend the environment's path, in order to find the installed Harmony Python module
#we should be able to use os.environ["HarmonyPremium"] + "/python-packages"
sys.path.append( r"C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages" )
from ToonBoom import harmony

def main():
    scene_path = r'P:\930462_HOJ_Project\Production\Film\S901\S901_SQ010\S901_SQ010_SH070\S901_SQ010_SH070\S901_SQ010_SH070.xstage'
    session, project, scene = load_scene(scene_path)
    print('Halløj')
    print_actions(session)
    print(scene)

def print_actions(session):
    actions = session.actions                                       #Get actions handler.
    for responder in actions.responders:
        print( responder )
        action_list = actions.actions(responder)
        for action in action_list:
            print( "   %s"%(action) )      

def 

def load_scene(path):
    harmony.open_project(path)                                    #Open an offline Harmony project
    session = harmony.session()                                   #Fetch the currently active session of Harmony
    project = session.project
    scene = project.scene
    return session, project, scene

if __name__ == "__main__":
    main()