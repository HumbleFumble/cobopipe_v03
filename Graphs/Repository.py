import os
import re
import Configs.OLD_CONFIGS.Config_KiwiStrit2 as cfg


class Node:
    def __init__(self, name=None, uri=None, parent=None, type=None):
        self.__uri = uri
        self.name = name
        self.parent = parent
        self.children = []
        self.row = 0
        self.type = type
        self.thumb_path = None

    def __str__(self):
        return self.name


class Repository:

    def __init__(self):
        self.root = None
        self.__map = {}
        self.__types = {0: "episode", 1: "seq", 2: "shot"}

    def search(self, name) -> Node:
        try:
            return self.__map[name]
        except KeyError:
            raise FileExistsError("The given name matches no file in the repository: " + name)

    def boot(self, uri):
        if os.path.exists(uri):
            self.root = self.__iterDir(uri=uri, parent=None, type="root", depth=0)
        else:
            raise FileNotFoundError("The requested path was not detected by os.path")

    def __iterDir(self, uri, parent, type, depth):
        """
        Template Method: Activated by boot() method to iterate down the children directories and create a graph
        for cached search tree functionality.

        Issue: Bluntness of algorithm causes great overhead as the directories being walked contain too much data.

        Solution: Biased search for specific directory names will decrease overhead."""
        new_node = Node(
            name=os.path.split(uri)[-1],
            uri=uri,
            parent=parent,
            type=type
        )
        self.__map[new_node.name] = new_node

        if depth >= len(self.__types):
            return new_node

        for child_dir in os.listdir(uri):
            re_compile = re.compile("%s$" % cfg.regex_strings[self.__types[depth]])
            if re_compile.search(child_dir.lower()):
                new_node.children.append(self.__iterDir(
                    uri=uri + "\\" + child_dir,
                    parent=new_node,
                    type=self.__types[depth],
                    depth=depth + 1)
                )

        return new_node
