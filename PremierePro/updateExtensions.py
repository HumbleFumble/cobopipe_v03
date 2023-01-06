import os
import shutil

def updateExtension(source):
    extensionsFolder = os.path.abspath(os.path.join('C:/Program Files (x86)/Common Files/Adobe/CEP/extensions'))
    destination = os.path.abspath(os.path.join(extensionsFolder, source.split(os.sep)[-1]))
    if source.split(os.sep)[-1] in os.listdir(extensionsFolder):
        os.remove(destination)
    shutil.copytree(source, destination)

if __name__ == '__main__':
    workFolder = os.path.abspath(os.path.join(__file__, '..', 'extensions'))
    for extension in os.listdir(workFolder):
        updateExtension(os.path.abspath(os.path.join(workFolder, extension)))