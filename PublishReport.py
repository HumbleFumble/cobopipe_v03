import os
from datetime import datetime
from getConfig import getConfigClass
from Log.CoboLoggers import getLogger
import file_util

CC = getConfigClass()
logger = getLogger()


class PublishReport:
    """Managing asset nodes and process data."""

    def __init__(self):
        """Initializing the class instance"""
        self.folderPath = CC.get_publish_report_folder()
        self.data = {}
        self.timestamp = datetime.now()

    def getData(self, scope=None, path=None):
        """Fetching publish data.

        Args:
            scope (str, optional): Name of the scope to start recursion from. Example 'E01_SQ010'. Defaults to None.
            path (str, optional): Direct path to start recursion from. Path overrides scope. Defaults to None.

        Returns:
            bool: Returns True if node was created.
        """

        # If path is not set. Use scope.
        # If no scope, use publish report folder path.
        if not path:
            if scope:
                path = self.getPath(scope)
            else:
                path = self.folderPath
                if not path:
                    logger.error("Invalid scope for data search")

        # If target is a file, create a node.
        if os.path.isfile(path):  # shot or asset
            self.createNode(path=path)
            return True

        # If target is folder, loop through children and start recursion.
        if os.path.exists(path):  # folder
            for item in os.listdir(path):
                targetPath = os.path.join(path, item).replace(os.sep, "/")
                if os.path.isfile(targetPath):
                    self.createNode(path=targetPath)
                else:
                    self.getData(path=targetPath)
        else:
            return None

    def createNode(self, identifier=None, path=None):
        """Creating node.

        Args:
            identifier (str, optional): Node identifier. For example 'Char_Main_Mia' or 'E01_SQ010_SH010'. Defaults to None.
            path (str, optional): Path to asset or shot. Defaults to None.

        Returns:
            object: Returns instance of Node.
        """

        # Prioritizing path as it is rooted in files on the server.
        if path:
            # Creating identifier from path.
            identifier = self.identify(path)
            # If identifier not in data dictionary. Create new Node instance for asset/shot.
            if not identifier in self.data.keys():
                self.data[identifier] = self.Node(self, identifier, path)
            else:
                # If identifier already in data dictionary. Update Node instance with provided path.
                if self.data[identifier].path != path:
                    self.data[identifier].path = path
                    self.data[identifier].update()
            return self.data[identifier]

        # Runs if only identifier is provided.
        elif identifier:
            # Gets the path to the asset/shot report from identifier.
            path = self.getPath(identifier)
            # If identifier not in data dictionary. Create new Node instance for asset/shot.
            if not identifier in self.data.keys():
                self.data[identifier] = self.Node(self, identifier, path)
            else:
                # If identifier already in data dictionary. Update Node instance with provided path.
                if self.data[identifier].path != path:
                    self.data[identifier].path = path
                    # Update data within Node instance.
                    self.data[identifier].update()
            return self.data[identifier]

        # Return None if neither path or identifier was provided as argument.
        return None

    def getPath(self, identifier):
        """Get path to asset/shot report from identififer.

        Args:
            identifier (str): Asset or shot identifier. Example 'Char_Main_Mia' or 'E01_SQ010_SH010'.

        Returns:
            str: Returns path as string.
        """
        try:
            # Solving Python 2 issue
            # Python 3 strings are unicode by default.
            identifier = unicode(identifier, "utf-8")
        except:
            pass

        # Setting publish report folder path as starting point.
        path = self.folderPath

        # Decoding identifier to add necessary elements to path.
        if identifier.lower() == "film":
            path = os.path.join(path, "Film").replace(os.sep, "/")
        elif identifier.lower() in ["asset", "assets"]:
            path = os.path.join(path, "Assets").replace(os.sep, "/")
        elif identifier[0] == "E" and identifier[1:3].isnumeric():
            path = os.path.join(path, "Film", identifier[:3]).replace(os.sep, "/")
            if len(identifier) > 3:
                if (
                    identifier[3] == "_"
                    and identifier[4:6] == "SQ"
                    and identifier[6:9].isnumeric
                ):
                    path = os.path.join(path, identifier[:9]).replace(os.sep, "/")
                    if len(identifier) > 9:
                        if (
                            identifier[9] == "_"
                            and identifier[10:12] == "SH"
                            and identifier[12:15].isnumeric
                        ):
                            path = os.path.join(
                                path, identifier[:15] + ".json"
                            ).replace(os.sep, "/")
        else:
            _list = identifier.split("_")
            path = os.path.join(path, "Assets", *_list).replace(os.sep, "/")
            if len(_list) == 3:
                path = path + ".json"

        return path

    def identify(self, path):
        """Converts path to identifier.

        Args:
            path (str): Path to asset/shot report.

        Returns:
            str: Returns identifier as string.
        """
        if CC.get_asset_publish_path() in path:
            if os.path.exists(path) and os.path.isfile(path):
                if self.folderPath in path:
                    identifiers = path.replace(".json", "").split("/")[-3:]
                    identifier = "_".join(identifiers)
                    if identifier:
                        return identifier
        elif CC.get_shot_publish_path() in path:
            if os.path.exists(path) and os.path.isfile(path):
                if self.folderPath in path:
                    identifier = os.path.splitext(path.split("/")[-1])[0]
                    if identifier:
                        return identifier
        elif CC.get_asset_top_path() in path:
            if "02_Ref" in path:
                _dict = CC.util.ComparePartOfPath(path, CC.get_asset_ref_folder())
            elif "01_Work" in path:
                _dict = CC.util.ComparePartOfPath(path, CC.get_asset_work_folder())

            if _dict:
                jsonPath = CC.get_asset_publish_report_file(**_dict)
                identifiers = jsonPath.replace(".json", "").split("/")[-3:]
                identifier = "_".join(identifiers)
                if identifier:
                    return identifier
        else:
            return None

    def mention(self, publishType, path, originNode):
        """Handling one report node mentioning another.

        Args:
            publishType (_type_): _description_
            path (str): Mentioned path.
            originNode (object): Instance of Node class.
        """

        # Creates identifier for the mentioned path.
        identifier = self.identify(path)

        # If node is not mentioning itself.
        if identifier and not identifier == originNode.identity:
            # If identifier does not already exists in data dictionary.
            if not identifier in self.data.keys():
                # Create new Node in the data dictionary.
                self.data[identifier] = self.Node(self, identifier)

            node = self.data[identifier]
            if path not in node.filePaths:
                node.filePaths.append(path)

            # Incrementing mention counter
            if originNode.identity in node.mentions.keys():
                key = node.mentions[originNode.identity]
                if publishType in key.keys():
                    if path in key[publishType].keys():
                        key[publishType][path] = key[publishType][path] + 1
                    else:
                        key[publishType][path] = 1
                else:
                    key[publishType] = {path: 1}
            else:
                node.mentions[originNode.identity] = {publishType: {path: 1}}

    def getAllReferences(self):
        """Fetches all references.

        Returns:
            dict: Returns dictionary of references.
        """
        references = {}
        for identity, node in sorted(self.data.items()):
            if node.references != {}:
                references[identity] = node.references
        return references

    def getAllTextures(self):
        """Fetches all texture references.

        Returns:
            dict: Returns dictionary of texture references.
        """
        textures = {}
        for identity, node in sorted(self.data.items()):
            if node.textures != {}:
                textures[identity] = node.textures
        return textures

    def getAllOIDs(self):
        """Fetches all Object IDs.

        Returns:
            dict: Returns dictionary of Object IDs.
        """
        OIDs = {}
        for identity, node in sorted(self.data.items()):
            if node.OIDs != {}:
                OIDs[identity] = node.OIDs
        return OIDs

    def getAllMIDs(self):
        """Fetches all Material IDs.

        Returns:
            dict: Returns dictionary of Material IDs.
        """
        MIDs = {}
        for identity, node in sorted(self.data.items()):
            if node.MIDs != {}:
                MIDs[identity] = node.MIDs
        return MIDs

    def getAllMentions(self):
        """Fetches all mentions.

        Returns:
            dict: Returns dictionary of mentions.
        """
        mentions = {}
        for identity, node in sorted(self.data.items()):
            if node.mentions != {}:
                mentions[identity] = node.mentions
        return mentions

    def getShotsByAsset(self, identity, scope=None):
        """Fetches shots which contains a specific asset. Optionally within specific scope.

        Args:
            identity (str): Identity of asset as string.
            scope (str, optional): Scope as string. For example 'E01_SQ010'. Defaults to None.

        Returns:
            list: Returns list of shots.
        """
        shots = []
        if not identity in self.data.keys():
            self.createNode(identity)
        for key, value in sorted(self.data[identity].mentions.items()):
            if self.data[key].type == "Shot":
                if key not in shots:
                    if scope:
                        if scope in [
                            self.data[key].episode,
                            "%s_%s" % (self.data[key].episode, self.data[key].sequence),
                            "%s_%s_%s"
                            % (
                                self.data[key].episode,
                                self.data[key].sequence,
                                self.data[key].shot,
                            ),
                        ]:
                            shots.append(key)
                    else:
                        shots.append(key)
            else:
                if not self.data[key].identity == identity:
                    output = self.getShotsByAsset(self.data[key].identity, scope=scope)
                    for item in output:
                        if output not in shots:
                            shots.append(item)
        return sorted(shots)

    def printReferenceOverview(self):
        """Prints out a complete overview of references."""
        for identity, node in self.data.items():
            if node.references:
                print("")
                print(identity)
                for key, value in node.references.items():
                    print("  " + key)
                    for path, amount in value.items():
                        print("    " + str(amount) + "x " + path)

    def gatherAssetsWithinAsset(self, identifier):
        """Fetches a list of assets contained within an asset.
        For example set dress assets in a set.

        Args:
            identifier (str): Identifier of parent asset.

        Returns:
            list: Returns list of assets.
        """
        assets = []
        for ref_type, refs in self.data[identifier].references.items():
            for ref in refs.keys():
                identity = self.identify(ref)
                if identity not in assets:
                    assets.append(identity)
        return assets

    def gatherShotAssetLists(
        self,
        scope=None,
        step_list=["AnimScene", "LightScene"],
        filter_type=["Char", "Prop", "Setdress", "Set"],
    ):
        """Gatheres a dictionary of shot's asset lists.

        Args:
            scope (str, optional): Scope as string. Defaults to None.
            step_list (list, optional): Pipeline step whitelist. Defaults to ["AnimScene", "LightScene"].
            filter_type (list, optional): Asset types whitelist. Defaults to ["Char", "Prop", "Setdress", "Set"].

        Returns:
            dict: Returns dictionary of shot's asset lists.
        """
        shot_asset_dict = {}
        used_nodes = []
        asset_ref_dict = {}
        for identity in self.data.keys():
            node = self.data[identity]
            if node.type == "Shot":
                if not scope in identity and scope:
                    continue
                shot_asset_dict[identity] = []
                for report_step in node.references.keys():
                    if not report_step in step_list:
                        continue
                    for ref_path in node.references[report_step]:
                        if (
                            "AnimRef.mb" in ref_path
                        ):  # skipping animation-scene-ref in light-scene.
                            continue
                        ref_path_key = ref_path
                        if ref_path in asset_ref_dict.keys():
                            shot_asset_dict[identity].append(asset_ref_dict[ref_path])
                            continue
                        if "3D_Assets" in ref_path:
                            ref_dict = CC.util.ComparePartOfPath(
                                ref_path, CC.get_asset_ref_folder()
                            )
                            ref_path_key = "_".join(
                                [
                                    ref_dict["asset_type"],
                                    ref_dict["asset_category"],
                                    ref_dict["asset_name"],
                                ]
                            )
                            if ref_path_key in self.data.keys():
                                if not self.data[ref_path_key].path:
                                    self.data[ref_path_key].setTypeFromDict(ref_dict)
                                if not self.data[ref_path_key] in used_nodes:
                                    used_nodes.append(self.data[ref_path_key])

                            if self.data[ref_path_key].assetType in filter_type:
                                asset_ref_dict[ref_path] = ref_path_key
                                shot_asset_dict[identity].append(ref_path_key)
                                output = self.gatherAssetsWithinAsset(ref_path_key)
                                for item in output:
                                    shot_asset_dict[identity].append(item)

        return shot_asset_dict

    class Node:
        """PublishReport Node"""
        def __init__(self, parent, identity, path=None):
            """Initializing instance of Node.

            Args:
                parent (object): Instance of PublishReport which the Node belongs to.
                identity (str): Node identity as string. For example 'Char_Main_Mia' or 'E01_SQ010_SH010'.
                path (str, optional): Path to the report file. Defaults to None.
            """
            logger.debug("Initializing PublishReport.Node: " + identity)

            # Creating Node variables.
            self.parent = parent
            self.identity = identity
            self.path = path
            self.type = None
            self.assetType = None
            self.assetCategory = None
            self.assetName = None
            self.episode = None
            self.sequence = None
            self.shot = None
            self.data = None
            self.references = {}
            self.textures = {}
            self.OIDs = {}
            self.MIDs = {}
            self.mentions = {}
            self.filePaths = []
            self.info_dict = {}

            # Updating Node data.
            self.update()

        def getInfoDict(self):
            """Creates info_dict from instance variables to interface with Class Config.

            Returns:
                dict: Returns info_dict as dictionary.
            """
            self.info_dict = {}
            if self.type == "Asset":
                self.info_dict = {
                    "asset_name": self.assetName,
                    "asset_type": self.assetType,
                    "asset_category": self.assetCategory,
                }
            if self.type == "Shot":
                self.info_dict = {
                    "shot_name": self.shot,
                    "seq_name": self.sequence,
                    "episode_name": self.episode,
                }
            return self.info_dict

        def update(self):
            """Updating Node data."""
            logger.debug("Updating PublishReport.Node: " + self.identity)
            if self.path:
                if os.path.exists(self.path) and os.path.isfile(self.path):
                    self.findType()
                    if self.type:
                        self.findAttributes()
                    if self.fetchJSON():
                        if self.data:
                            self.unwrap()

        def setTypeFromDict(self, input_dict={}):
            """TODO: Comment this.
            """
            for k in input_dict.keys():
                v = input_dict[k]
                if k == "asset_type":
                    if not self.assetType:
                        self.assetType = v
                if k == "asset_category":
                    if not self.assetCategory:
                        self.assetCategory = v
                if k == "asset_name":
                    if not self.assetName:
                        self.assetName = v

        def findType(self):
            """Fiding the type of Node."""
            logger.debug("Finding type of PublishReport.Node: " + self.identity)
            if os.path.exists(self.parent.folderPath):
                if self.parent.folderPath in self.path:
                    if CC.get_asset_publish_path() in self.path:
                        self.type = "Asset"
                    elif CC.get_shot_publish_path() in self.path:
                        self.type = "Shot"

        def findAttributes(self):
            """Finding attributes of Node."""
            logger.debug("Finding attributes of PublishReport.Node: " + self.identity)
            if self.type == "Asset":
                if os.path.exists(self.parent.folderPath):
                    if self.parent.folderPath in self.path:
                        _dictionary = CC.util.ComparePartOfPath(
                            self.path, CC.get_asset_publish_report_file()
                        )
                        if "asset_type" in _dictionary.keys():
                            self.assetType = _dictionary["asset_type"]
                        if "asset_category" in _dictionary.keys():
                            self.assetCategory = _dictionary["asset_category"]
                        if "asset_name" in _dictionary.keys():
                            self.assetName = _dictionary["asset_name"]
            if self.type == "Shot":
                if os.path.exists(self.parent.folderPath):
                    if self.parent.folderPath in self.path:
                        _dictionary = CC.util.ComparePartOfPath(
                            self.path, CC.get_shot_publish_report_file()
                        )
                        if "episode_name" in _dictionary.keys():
                            self.episode = _dictionary["episode_name"]
                        if "seq_name" in _dictionary.keys():
                            self.sequence = _dictionary["seq_name"]
                        if "shot_name" in _dictionary.keys():
                            self.shot = _dictionary["shot_name"]

        def fetchJSON(self):
            """Fetching data from report json file.

            Returns:
                dict: Returns dictionary of data.
            """
            logger.debug("Loading JSON data of PublishReport.Node: " + self.identity)
            jsonData = file_util.load_json(save_location=self.path)
            if self.data != jsonData:
                self.data = jsonData
                return True
            else:
                return False

        def unwrap(self):
            """Unwrapping data from report file."""
            logger.debug("Unwrapping data of PublishReport.Node: " + self.identity)
            self.references = {}
            self.textures = {}

            # Looping over all the data and handling each individual type.
            for key in self.data.keys():
                value = self.data[key]
                if "_ref_paths" in key:
                    key = key.split("_ref_paths")[0]
                    for item in value:  # item = ref_paths
                        if key in self.references.keys():
                            if item in self.references[key].keys():
                                self.references[key][item] = (
                                    self.references[key][item] + 1
                                )
                            else:
                                self.references[key][item] = 1
                        else:
                            self.references[key] = {item: 1}
                        self.parent.mention(key, item, self)

                elif "_texture_paths" in key:
                    for item in value:
                        if key in self.textures.keys():
                            if item in self.textures[key].keys():
                                self.textures[key][item] = self.textures[key][item] + 1
                            else:
                                self.textures[key][item] = 1
                        else:
                            self.textures[key] = {item: 1}

                elif "_OIDs" in key:
                    if key.split("_")[0] in ["Render", "Light"]:
                        self.OIDs = value

                elif "_MIDs" in key:
                    if key.split("_")[0] in ["Render", "Light"]:
                        self.MIDs = value


if __name__ == "__main__":
    pr = PublishReport()
    pr.getData("Char_Main_Mia")
    print(pr.data["Char_Main_Mia"])
