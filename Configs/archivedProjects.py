import os
import file_util

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
    "MiasMagic2",
    "LegoFriends",
    "Boerste-Season2",
    "TV2-AlleBorn"
]

if __name__ == '__main__':
    path = os.path.join(os.path.dirname(__file__), 'archivesProjects.json')
    file_util.save_json(path, list_of_archived_projects)