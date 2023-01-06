import os
import shutil
import subprocess
from PySide2 import QtCore

class Worker(QtCore.QRunnable):
    def __init__(self, func=None, *args,**kwargs):
        super(Worker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if self.func:
            result = self.func(*self.args,**self.kwargs)
            print(result)


class transferAssetClass():
    def __init__(self):
        self.env = self._runtime_environment(os.path.dirname(os.path.realpath(__file__)))
        self.pool = QtCore.QThreadPool.globalInstance()
        # self.pool.globalInstance()

    def CopyFolder(self, source, dest):
        """
        copy folder from source path to dest path
        :param source: from path
        :param dest: to path
        """
        if os.path.exists(dest):
            print("Skipping! Folder already exists!: %s" % dest)
            # raise FileExistsError("Folder already exists!: %s" % dest)
            return False
        if os.path.exists(source):
            print("Copying %s to %s" %(source,dest))
            shutil.copytree(source,dest,ignore=shutil.ignore_patterns('_History'))
        else:
            print("NO SOURCE!")
            return False

    def transferAssetRun(self, orig_folder_path, new_folder_path,replace_dict):
        self.CopyFolder(orig_folder_path,new_folder_path)
        maya_files = self.getMayaFiles(new_folder_path)
        print("All maya files in %s: %s" % (new_folder_path,maya_files))
        for maya_file in maya_files:
            # print("File: %s" % maya_file)
            # self.updateMayaFile(maya_file,replace_at,replace_with)
            new_worker = Worker(self.updateMayaFile,maya_file,replace_dict)

            self.pool.start(new_worker)
            # print("FINISHED WITH: %s" % maya_file)
        print("\n\nALL DONE WITH: %s" % new_folder_path)

    def updateAssetRun(self,asset_folder,replace_dict):
        maya_files = self.getMayaFiles(asset_folder)
        print("All maya files in %s: %s" % (asset_folder, maya_files))
        for maya_file in maya_files:
            print("File: %s" % maya_file)
            new_worker = Worker(self.updateMayaFile, maya_file, replace_dict)
            # self.updateMayaFile(maya_file,replace_at,replace_with)
            self.pool.start(new_worker)

            # print("FINISHED WITH: %s" % maya_file)
        print("\n\nALL DONE WITH: %s" % asset_folder)


    # def CreateDictFromKW(self,**kwargs):
    #     return_dict = {}
    #     print(kwargs)
    #     for k,v in kwargs:
    #         return_dict[k] = v
    #     return return_dict

    # def returnDictAsKWString(self, c_dict):
    #     return_string = ""
    #     for k,v in c_dict.items():
    #         return_string = return_string + "%s='%s'," %(k,v)
    #     return return_string

    def updateMayaFile(self,file_path,replace_dict):
        from Maya_Functions.file_util_functions import getMayaFileType
        file_type = getMayaFileType(file_path)
        script_content= """import maya.standalone
maya.standalone.initialize('python')
import maya.cmds as cmds
cmds.file('{file_path}', open=True,f=True)
from Maya_Functions.update_functions import update_ref_and_textures
update_ref_and_textures({replace_dict})
cmds.file(type='{file_type}')
cmds.file(save=True)
print('FILE SAVED!!')
cmds.quit(f=True)""".format(file_path=file_path,file_type=file_type,replace_dict=replace_dict)
        script_content = ";".join(script_content.split("\n"))
        base_command = 'mayapy.exe -c "%s"' % (script_content)
        print("Run Command for %s:" % file_path)
        print(base_command)
        cp = subprocess.Popen(base_command, shell=False, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # cp = subprocess.call(base_command)
        return cp.communicate()[0]


    def getMayaFiles(self,directory):
        return_list = []
        for cur_item in os.listdir(directory):
            cur_path = os.path.join(directory, cur_item).replace(os.sep, '/')
            if os.path.isdir(cur_path):
                return_list.extend(self.getMayaFiles(cur_path))
            else:
                if cur_path[-3:] in ['.ma', '.mb']:
                    return_list.append(cur_path)
        return return_list

    def _runtime_environment(self, new_path):
        '''
        Returns a new environment dictionary for this intepreter, with only the supplied paths
        (and the required maya paths).  Dictionary is independent of machine level settings;
        non maya/python related values are preserved.
        '''
        runtime_env =  os.environ.copy()
        runtime_env['PYTHONPATH'] = "%s;%s" % (runtime_env['PYTHONPATH'],new_path)
        print(runtime_env['PYTHONPATH'])
        runtime_env['PATH'] = ''
        return runtime_env


if __name__ == "__main__":
    pass
    # arm_asset_dict = {'asset_name':'ArmARight', 'asset_type':"RigModule", 'asset_category':'Arm'}
    # arms_asset_dict = {'asset_name': 'ArmsA', 'asset_type': "RigModule", 'asset_category': 'Arm'}
    # eyes_asset_dict = {'asset_name': 'EyesA', 'asset_type': "RigModule", 'asset_category': 'Head'}
    # legs_asset_dict = {'asset_name': 'LegsA', 'asset_type': "RigModule", 'asset_category': 'Leg'}
    # ta = transferAssetClass()

    # replace_dict = {'/Char/Module/EyesA/':'/RigModule/Eye/EyesA/','/Char/Module/LegsA/':'/RigModule/Leg/LegsA/','/Char/Module/ArmsA/':'/RigModule/Arm/ArmsA/','/Char/Module/ArmARight/':'/RigModule/Arm/ArmARight/'}

    # ta.transferAssetRun()
    # ta._runtime_environment("test_path")
    # print("test")
    # script_content = "import maya.standalone;maya.standalone.initialize('python');import maya.cmds as cmds;cmds.file('P:/930383_KiwiStrit3/Production/Assets/3D_Assets/Prop/Art/CanvasA/01_Work/Maya/CanvasA_Base.ma', open=True,f=True);from Maya_Functions.update_functions import update_ref_and_textures;update_ref_and_textures('P:/930382_KiwiStrit2/Production', 'P:/930383_KiwiStrit3/Production');cmds.file(type='mayaAscii');cmds.file(save=True);cmds.quit(f=True)"
    # base_command = 'mayapy.exe -c "%s"' % (script_content)
    # cp = subprocess.Popen(base_command, shell=False, universal_newlines=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # output,err = cp.communicate()
    # print("\n\n%s\n\nDONE WITH OUTPUT\n\n" % output)

