import os
import shutil

def unpack():
    root_folder = 'W:/930507_Lego_Friends/Production/_Temp/project_folder2'
    destination = 'W:/930507_Lego_Friends/Production/_Temp/project_folder2'

    zip_files = []

    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if file.endswith('.zip'):
                source = os.path.join(root, file)
                zip_files.append(source)

    for zip_file in zip_files:
        if not zip_file.endswith("CH.zip"):
            print(zip_file)
            shutil.copy(zip_file, destination)

if __name__ == "__main__":
    unpack()