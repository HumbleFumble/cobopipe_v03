
import sys
#Extend the environment's path, in order to find the installed Harmony Python module
#we should be able to use os.environ["HarmonyPremium"] + "/python-packages"
sys.path.append( r"C:\Program Files (x86)\Toon Boom Animation\Toon Boom Harmony 22 Premium\win64\bin\python-packages" )
import TB.ToonBoom_Global_Python.CB_SetupRenderInfo_Python as rs

def externalRendering(scene_file):
    from ToonBoom import harmony
    print("Trying to render out: %s" % scene_file)
    harmony.open_project( scene_file )                                    #Open an offline Harmony project
    current_session = harmony.session()                                   #Fetch the currently active session of Harmony
    project = current_session.project                                     #The project that is already loaded.
    print( "Current Project: %s" % (project.project_path) )
    passes_folder = rs.findPassesFolder()
    write_nodes = []
    for node in project.scene.nodes:
      if(node.type == "WRITE" and "RENDER_" in node.name):
          rs.setRenderNodePaths(node,passes_folder)
          write_nodes.append(node)

    if write_nodes:
        project.save_all()
        render_handler = project.create_render_handler()
        render_handler.blocking = True
        for cur in write_nodes:
            render_handler.node_add( cur )
        #The render handler will render any nodes added to it.
        render_handler.render()
        print("\n\nRENDERING DONE FOR %s\n\n" % scene_file)


if __name__ == "__main__":
    externalRendering(sys.argv[1])
# harmony.open_project( r"P:\930462_HOJ_Project\Production\Film\S104\S104_SQ010\S104_SQ010_SH010\S104_SQ010_SH010\S104_SQ010_SH010_V007.xstage" )