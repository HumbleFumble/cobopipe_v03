"""
1. Make tree from film path
2. Find children of specifc parent
3. Find all grandchildren (might fail)
"""

from getConfig import getConfigClass
CC = getConfigClass("KiwiStrit2")
first = "TEST IS TEST"

import Graphs.Repository as rep
rep_class = rep.Repository()

rep_class.boot(CC.get_film_path())
print("FOUND ", rep_class.search("Film").parent.name)

def getParent(name=False):
    if name:
        return self.parent.name
    return self.parent

print("Children ", [i.name for i in rep_class.search("E25_SQ020").children])

print(rep_class.root)