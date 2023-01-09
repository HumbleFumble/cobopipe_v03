###########################################################################################################################################
##
## aiPipeline. The Pipeliney choice.
##
## Copyright:	aiPipeline is Copyright 2010 AnimationInvasion / Jakob Steffensen all rights reserved.
## File:        aiPipeline.Maya_Functions.Render
## Description: 
##
###########################################################################################################################################


# Standard Module imports.
import os
import os.path
import shutil
import getpass

# Maya_Functions Module imports.
import maya.cmds as cmds
import maya.mel as mel

def getUser():
    '''Returns the username of the active user.'''
    return getpass.getuser().lower()

def getMayaAsciiOrBinary(file_path=None):
    ''''''
    
    file_type = None
    
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read().decode("utf-8")
        f.close()
                
        if data.startswith("FOR"):
            file_type = "mb"
        
        if data.startswith("//M"):
            file_type = "ma"
            
        return file_type

def fixMayaExtension(file_path):
    ''''''
    
    if os.path.exists(file_path):
        
        current_extension = file_path.split(".")[-1]
        true_extension = getMayaAsciiOrBinary(file_path)
        
        new_file_path = None
        
        if not current_extension == true_extension:
        
            new_file_path = file_path.replace(".%s" % current_extension, ".%s" % true_extension)

            try:
                shutil.move(file_path, new_file_path)
            except:
                pass
        else:
            new_file_path = file_path

        # Try and see if this fixes it.
        if new_file_path == None:
            new_file_path = file_path

        return new_file_path
    else:
        return file_path


def convertToMayaBinary(input_files=[], remove_existing=False):
    ''''''
    
    for input_file in input_files:    
        try:
            output_file = input_file.replace(".ma", ".mb")
            cmds.file(input_file, open=True)
            cmds.file(rename=output_file)
            cmds.file(save=True, type="mayaBinary")

        
            if remove_existing:
                try:
                    os.remove(input_file)

                except:
                    print("error")
        except:
            print("error")
    
  
def historyFiles(file_path=None):

    found_files = []

    # If the path is not provided then try and get from the maya scene.
    if file_path == None:    
        file_path = cmds.file(query=True, sceneName=True)
        
    print(file_path)

    if not file_path == "":
    
        # Only proceed if path is valid (ie. we can get a histoy folder from it)
        if os.path.exists(file_path):
       
            filename = os.path.split(file_path)[1]
            folder = os.path.split(file_path)[0]
            basename = os.path.splitext(filename)[0]
            extension = os.path.splitext(filename)[1]
            
            history_folder2 = folder + "/_History"
            history_files2 = os.listdir(history_folder2)
            
            # Loop through all files in history folder and check.
            for history_file in history_files2:        
                
                # Same extension?
                if extension == os.path.splitext(history_file)[1]:
                    # Same basename?
                    if history_file.startswith(basename):
                    
                        # Number of underscore separated parts equal basename + 2 ? (version_username)
                        if len(history_file.split("_")) >= len(basename.split("_"))+2:
                            found_files.append(history_file)

    return found_files
# Test Test Test
def historyFolder(file_path=None):
    '''Return the history folder for a specified file. Oh... and create it if not present.'''

    history_folder = None

    if file_path == None:    
        file_path = cmds.file(query=True, sceneName=True)
    
    # Only proceed if path is valid (ie. we can get a histoy folder from it)
    if os.path.exists(file_path):
        folder = os.path.split(file_path)[0]        
        history_folder = folder + "/_History"
        #Create Folders
        if not os.path.exists(history_folder):
            os.makedirs(history_folder)
        #aiIO.createFolders([history_folder], silent=True)
        
    return history_folder 

def SaveCopyOf(file_path):
    file_type = getMayaAsciiOrBinary(file_path)
    file_path = fixMayaExtension(file_path)
    cmds.file(rename=file_path)
    filename = os.path.split(file_path)[1]
    folder = os.path.split(file_path)[0]
    basename = os.path.splitext(filename)[0]
    extension = os.path.splitext(filename)[1]
    extenstion = file_type
    history_folder = historyFolder()
    history_files = historyFiles()
    version = len(history_files) + 1
    user = getUser()
    history_filename = "%s/%s_%s_%s%s" % (history_folder, basename, str(version).zfill(3), user, extension)
    shutil.copy2(file_path, history_filename)
    print("Trying to make a copy of %s and saving it in a history folder" % file_path)

def incrementalSave(comment=None, zero_pad=3):
    '''Saves the open file in the history folder.'''
    
    file_path = cmds.file(query=True, sceneName=True)
    
    if not file_path == None:
        if not file_path == "":
        
            file_type = getMayaAsciiOrBinary(file_path)
            if not file_type:
                file_type = "ma"
            file_path = fixMayaExtension(file_path)
            cmds.file(rename=file_path)        
            filename = os.path.split(file_path)[1]
            folder = os.path.split(file_path)[0]
            basename = os.path.splitext(filename)[0]
            # extension = os.path.splitext(filename)[1]
            extension = file_type
            history_folder = historyFolder()
            history_files = historyFiles()
            version = len(history_files) + 1
            user = getUser()
            history_filename = "%s/%s_%s_%s.%s" % (history_folder, basename, str(version).zfill(zero_pad), user, extension)
            
            print("file_type = %s, file_path = %s" % (file_type, file_path))
            random_string = "Temp_Save_File"
            #maybe need a random string
            temp_filename = file_path.replace("." + file_type, "_" + random_string + "_Temp." + file_type)
            temp_filename = "c:/Temp/" + os.path.basename(temp_filename)            
            
                    
            # Save current maya file.
            try:
                cmds.file(rename=temp_filename)
                cmds.file(save=True, options="v=0;")
                cmds.file(rename=file_path)

                if file_path.endswith(".ma"):
                    mel.eval("addRecentFile \"%s\" \"mayaAscii\"" % file_path)
                if file_path.endswith(".mb"):
                    mel.eval("addRecentFile \"%s\" \"mayaBinary\"" % file_path)
                    
                cmds.file(modified=False)
            except:
                print("Error 1")
            if os.path.exists(temp_filename):
                try:
                    shutil.copy2(file_path, history_filename)
                    #Debug.write("Backed up %s -> %s" % (file_path, history_filename),  Debug.INFO, "incrementalSave")
                except:
                    print("Error 2")
                
                try:
                    shutil.move(temp_filename, file_path)
                    #Debug.write("Moved %s -> %s" % (temp_filename, file_path),  Debug.INFO, "incrementalSave")
                except:
                    print("Error 3")
                    
            else:
                print("Error 4")
 
        else:
            mel.eval("SaveSceneAs;")
            file_path = cmds.file(query=True, sceneName=True)
            cmds.file(modified=False)
            
        
        if cmds.window("aiIncrementalSaveUI_Window", exists=True):
            cmds.deleteUI("aiIncrementalSaveUI_Window", window=True )  
    else:
        print("File path was none cannot incremental Save")
