import os
import json

list_of_archived_projects = [
    "HOJ-Pilot",
    "KDH-Jenny",
    "KDH-Lis",
    "KDH-Nina",
    "KDH-Else",
    "KDH-Asta",
    "KiwiStrit2",
    "MiasMagic",
    "Mumsi",
    "KiwiStrit3",
    "MiniSjang-MinSang",
    "DenSaerligeMester",
    "MiasMagic2"
]

if __name__ == '__main__':
    path = os.path.join(os.path.dirname(__file__), 'archivesProjects.json')
    with open(path, "w+") as saveFile:
        json.dump(obj=list_of_archived_projects, fp=saveFile, indent=4, sort_keys=True)