import os

def findFiles(list_of_names=[],base_path=""):
    return_list = []
    for name in list_of_names:
        for root,folder,files in os.walk(base_path):
            for cur_file in files:

                if name in cur_file:
                    if "_V001" in cur_file:
                        print(cur_file)
                        print(os.path.join(root,cur_file) )
                        return_list.append(os.path.join(root,cur_file))
    return return_list

def createFolder(thumb_folder,file_name):
    """creates folder to place shot pngs in"""
    if not os.path.exists(os.path.join(thumb_folder,file_name)):
        os.makedirs(os.path.join(thumb_folder,file_name))


def createThumbnails():
    pass

def run():
    base_path = "P:/930462_HOJ_Project/Production/Asset/Environment/Nifleheim/FrostKingDomain/"
    list_of_names = ["FenrisCostume_INT_0101_D"]
    google_save_folder = "P:/930462_HOJ_Project/Production/Asset/Thumbnails/"
    found_list = findFiles(list_of_names=list_of_names,base_path=base_path)

    for file_name in found_list:
        pretty_name = os.path.splitext((os.path.split(file_name)[1]))[0]
        createFolder(google_save_folder,pretty_name)

if __name__ == '__main__':
    run()
