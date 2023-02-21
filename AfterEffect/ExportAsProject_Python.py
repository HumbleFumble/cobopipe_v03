import os.path
import sys
import AfterEffectFunctions as AF
import shutil

def run(orig_file, new_file, list_of_ids):
    # duplicate file and save it correctly
    if os.path.exists(orig_file):
        shutil.copy(orig_file,new_file)
    else:
        print(f"Can't find {orig_file}. Stopped exporting project")
    script_file = f"{os.path.dirname(new_file)}/Temp_ExportAsProject_script.jsx"

    #run script
    AF.ExportAsProject(new_file, list_of_ids,script_file)
    #remove script bat
    # os.remove(script_file)
    return True

if __name__ == "__main__":
    print(sys.argv)
    run(*sys.argv[1:])
