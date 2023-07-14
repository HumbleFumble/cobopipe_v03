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

if __name__ == '__main__':
    base_path = ""
    list_of_names = [""]