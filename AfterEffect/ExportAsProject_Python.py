import os.path
import sys
import shutil
import subprocess

def run(orig_file, new_file, list_of_ids):
    # duplicate file and save it correctly
    orig_drive_letter = orig_file.split("/")[1]
    orig_file = "P:/" + orig_file.split("/"+orig_drive_letter+"/")[1]
    new_drive_letter = new_file.split("/")[1]
    new_file = "P:/" + new_file.split("/" + new_drive_letter + "/")[1]
    temp_save_location = "C:/Temp/AE_ExportAsProject_Temp.aep"
    print(temp_save_location)
    if os.path.exists(orig_file):
        shutil.copy(orig_file,temp_save_location)
        script_file = f"{os.path.dirname(temp_save_location)}/Temp_ExportAsProject_script.jsx"
        print(script_file)

        # run script
        ExportAsProject(temp_save_location,new_file, list_of_ids, script_file)
        # remove script bat
        #os.remove(script_file)
        return True
    else:
        print(f"Can't find {orig_file}. Stopped exporting project")


def ExportAsProject(cur_location,comp_path, list_of_ids, script_location):
    script_path = script_location
    # script_path = "%s/Temp_ExportAsProject.jsx" % script_location
    # print("Dest: %s Src: %s Pass: %s" % (dst_comp,src_comp,passes_folder))
    script_content = """
      #target.aftereffects
      app.beginSuppressDialogs()
      
      function Run(cur_location,file_path,list_of_ids){
          //Setting paths and variables
          var new_project = new File(cur_location);
          app.open(new_project);
          reduce_items = ReturnItemsFromIds (list_of_ids)
          app.project.reduceProject(reduce_items);
          app.project.save(file_path);
          
      }

      function ReturnItemsFromIds(list_of_ids){
          return_list = []
          for(var i =0; i < list_of_ids.length;i++){
              return_list.push(app.project.itemByID(list_of_ids[i]))
              }
          return return_list
      }
      
      Run("%s","%s",[%s])
      app.endSuppressDialogs(0)
      """ % (cur_location, comp_path, list_of_ids)

    script_file = open(script_path, "w")
    script_file.write(script_content)
    script_file.close()

    ae_apply = 'afterfx -noui -r "%s"' % (script_path)
    print(ae_apply)
    wait = subprocess.run(ae_apply, shell=True, universal_newlines=True)
    #os.remove(script_path)  # Deletes before subprocess finishes
    return True

if __name__ == "__main__":
    print(sys.argv)
    run(*sys.argv[1:])
