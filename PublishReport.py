import os
from datetime import datetime
from getConfig import getConfigClass
from Log.CoboLoggers import getLogger
from Maya_Functions.file_util_functions import saveJson, makeFolder, loadJson

CC = getConfigClass()
logger = getLogger()

class PublishReport():
    def __init__(self):
        self.folderPath = CC.get_publish_report_folder()
        print(self.folderPath)
        self.data = {}
        self.timestamp = datetime.now()

    def getData(self, scope=None, path=None):
        if not path:
            if scope:
                path = self.getPath(scope)
            else:
                path = self.folderPath
                if not path:
                    logger.error('Invalid scope for data search')
        if os.path.isfile(path): # shot or asset
            self.createNode(path=path)
            return True
        if os.path.exists(path): # folder
            for item in os.listdir(path):
                targetPath = os.path.join(path, item).replace(os.sep, '/')
                if os.path.isfile(targetPath):
                    self.createNode(path=targetPath)
                    # identifier = self.identify(targetPath)
                    # if identifier:
                    #     if not identifier in self.data.keys():
                    #         self.data[identifier] = self.Node(self, identifier, targetPath)
                    #     else:
                    #         if self.data[identifier].path != targetPath:
                    #             self.data[identifier].path = targetPath
                    #             self.data[identifier].update()
                else:
                    self.getData(path=targetPath)
        else:
            return None

    def createNode(self, identifier=None, path=None):
        if path:
            identifier = self.identify(path)
            if not identifier in self.data.keys():
                self.data[identifier] = self.Node(self, identifier, path)
            else:
                if self.data[identifier].path != path:
                    self.data[identifier].path = path
                    self.data[identifier].update()
            return self.data[identifier]
        elif identifier:
            path = self.getPath(identifier)
            if not identifier in self.data.keys():
                self.data[identifier] = self.Node(self, identifier, path)
            else:
                if self.data[identifier].path != path:
                    self.data[identifier].path = path
                    self.data[identifier].update()
            return self.data[identifier]
        return None

    def getPath(self, identifier):
        try:
            identifier = unicode(identifier, "utf-8")
        except:
            pass
        path = self.folderPath
        if identifier.lower() == 'film':
            path = os.path.join(path, 'Film').replace(os.sep, '/')
        elif identifier.lower() in ['asset', 'assets']:
            path = os.path.join(path, 'Assets').replace(os.sep, '/')
        elif identifier[0] == 'E' and identifier[1:3].isnumeric():
            path = os.path.join(path, 'Film', identifier[:3]).replace(os.sep, '/')
            if len(identifier) > 3:
                if identifier[3] == '_' and identifier[4:6] == 'SQ' and identifier[6:9].isnumeric:
                    path = os.path.join(path, identifier[:9]).replace(os.sep, '/')
                    if len(identifier) > 9:
                        if identifier[9] == '_' and identifier[10:12] == 'SH' and identifier[12:15].isnumeric:
                            path = os.path.join(path, identifier[:15] + '.json').replace(os.sep, '/')
        else:
            _list = identifier.split('_')
            path = os.path.join(path, 'Assets', *_list).replace(os.sep, '/')
            if len(_list) == 3:
                path = path + '.json'

        return path

    def identify(self, path):
        # P:/_WFH_Projekter/930486_MiaMagicPlayground_S3-4/4_Production/Assets/3D_Assets/Char/Secondary/BuckieWithoutHisBucket/01_Work/Maya/BuckieWithoutHisBucket_Model.ma
        if CC.get_asset_publish_path() in path:
            if os.path.exists(path) and os.path.isfile(path):
                if self.folderPath in path:
                    identifiers = path.replace('.json', '').split('/')[-3:]
                    identifier = '_'.join(identifiers)
                    if identifier:
                        return identifier
        elif CC.get_shot_publish_path() in path:
            if os.path.exists(path) and os.path.isfile(path):
                if self.folderPath in path:
                    identifier = os.path.splitext(path.split('/')[-1])[0]
                    if identifier:
                        return identifier
        elif CC.get_asset_top_path() in path:
            if '02_Ref' in path:
                _dict = CC.util.ComparePartOfPath(path,CC.get_asset_ref_folder())
            elif '01_Work' in path:
                _dict = CC.util.ComparePartOfPath(path, CC.get_asset_work_folder())

            if _dict:
                jsonPath = CC.get_asset_publish_report_file(**_dict)
                identifiers = jsonPath.replace('.json', '').split('/')[-3:]
                identifier = '_'.join(identifiers)
                if identifier:
                    return identifier
        else:
            return None

    def mention(self, publishType, path, originNode):
        identifier = self.identify(path)

        if identifier and not identifier == originNode.identity:
            if not identifier in self.data.keys():
                self.data[identifier] = self.Node(self, identifier)
            node = self.data[identifier]
            if path not in node.filePaths:
                node.filePaths.append(path)

            if originNode.identity in node.mentions.keys():
                key = node.mentions[originNode.identity]
                if publishType in key.keys():
                    if path in key[publishType].keys():
                        key[publishType][path] = key[publishType][path] + 1
                    else:
                        key[publishType][path] = 1
                else:
                    key[publishType] = {path:1}
            else:
                node.mentions[originNode.identity] = {publishType:{path:1}}

    def getAllReferences(self):
        references = {}
        for identity, node in sorted(self.data.items()):
            if node.references != {}:
                references[identity] = node.references
        return references

    def getAllTextures(self):
        textures = {}
        for identity, node in sorted(self.data.items()):
            if node.textures != {}:
                textures[identity] = node.textures
        return textures

    def getAllOIDs(self):
        OIDs = {}
        for identity, node in sorted(self.data.items()):
            if node.OIDs != {}:
                OIDs[identity] = node.OIDs
        return OIDs

    def getAllMIDs(self):
        MIDs = {}
        for identity, node in sorted(self.data.items()):
            if node.MIDs != {}:
                MIDs[identity] = node.MIDs
        return MIDs

    def getAllMentions(self):
        mentions = {}
        for identity, node in sorted(self.data.items()):
            if node.mentions != {}:
                mentions[identity] = node.mentions
        return mentions

    def getShotsByAsset(self, identity, scope=None):
        shots = []
        if not identity in self.data.keys():
            self.createNode(identity)
        for key, value in sorted(self.data[identity].mentions.items()):
            if self.data[key].type == 'Shot':
                if key not in shots:
                    if scope:
                        if scope in [self.data[key].episode,
                                     "%s_%s" % (self.data[key].episode, self.data[key].sequence),
                                     "%s_%s_%s" % (self.data[key].episode, self.data[key].sequence, self.data[key].shot)]:
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

    # Use this to print out a complete overview of references
    def printReferenceOverview(self):
        for identity, node in self.data.items():
            if node.references:
                print('')
                print(identity)
                for key, value in node.references.items():
                    print('  ' + key)
                    for path, amount in value.items():
                        print('    ' + str(amount) + 'x ' + path)


    def gatherAssetsWithinAsset(self, identifier):
        assets = []
        for ref_type, refs in self.data[identifier].references.items():
            for ref in refs.keys():
                identity = self.identify(ref)
                if identity not in assets:
                    assets.append(identity)
        return assets


    def gatherShotAssetLists(self, scope=None, step_list=["AnimScene", "LightScene"], filter_type=['Char', 'Prop', 'Setdress', 'Set']):
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
                        if "AnimRef.mb" in ref_path: #skipping animation-scene-ref in light-scene.
                            continue
                        ref_path_key = ref_path
                        if ref_path in asset_ref_dict.keys():
                            shot_asset_dict[identity].append(asset_ref_dict[ref_path])
                            continue
                        if "3D_Assets" in ref_path:
                            ref_dict = CC.util.ComparePartOfPath(ref_path, CC.get_asset_ref_folder())
                            ref_path_key = '_'.join([ref_dict["asset_type"],
                                                     ref_dict["asset_category"],
                                                     ref_dict["asset_name"]])
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


    class Node():
        def __init__(self, parent, identity, path=None):
            logger.debug('Initializing PublishReport.Node: ' + identity)
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
            self.update()

        def getInfoDict(self):
            self.info_dict = {}
            if self.type=="Asset":
                self.info_dict = {"asset_name":self.assetName,"asset_type":self.assetType,"asset_category":self.assetCategory}
            if self.type =="Shot":
                self.info_dict = {"shot_name":self.shot, "seq_name":self.sequence,"episode_name":self.episode}
            return self.info_dict

        def update(self):
            logger.debug('Updating PublishReport.Node: ' + self.identity)
            if self.path:
                if os.path.exists(self.path) and os.path.isfile(self.path):
                    self.findType()
                    if self.type:
                        self.findAttributes()
                    if self.fetchJSON():
                        if self.data:
                            self.unwrap()

        def setTypeFromDict(self,input_dict={}):
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
            logger.debug('Finding type of PublishReport.Node: ' + self.identity)
            if os.path.exists(self.parent.folderPath):
                if self.parent.folderPath in self.path:
                    if CC.get_asset_publish_path() in self.path:
                        self.type = 'Asset'
                    elif CC.get_shot_publish_path() in self.path:
                        self.type = 'Shot'


        def findAttributes(self):
            logger.debug('Finding attributes of PublishReport.Node: ' + self.identity)
            if self.type == 'Asset':
                if os.path.exists(self.parent.folderPath):
                    if self.parent.folderPath in self.path:
                        _dictionary = CC.util.ComparePartOfPath(self.path, CC.get_asset_publish_report_file())
                        if 'asset_type' in _dictionary.keys():
                            self.assetType = _dictionary['asset_type']
                        if 'asset_category' in _dictionary.keys():
                            self.assetCategory = _dictionary['asset_category']
                        if 'asset_name' in _dictionary.keys():
                            self.assetName = _dictionary['asset_name']
            if self.type == 'Shot':
                if os.path.exists(self.parent.folderPath):
                    if self.parent.folderPath in self.path:
                        _dictionary = CC.util.ComparePartOfPath(self.path, CC.get_shot_publish_report_file())
                        if 'episode_name' in _dictionary.keys():
                            self.episode = _dictionary['episode_name']
                        if 'seq_name' in _dictionary.keys():
                            self.sequence = _dictionary['seq_name']
                        if 'shot_name' in _dictionary.keys():
                            self.shot = _dictionary['shot_name']


        def fetchJSON(self):
            logger.debug('Loading JSON data of PublishReport.Node: ' + self.identity)
            jsonData = loadJson(save_location=self.path)
            if self.data != jsonData:
                self.data = jsonData
                return True
            else:
                return False

        def unwrap(self):
            logger.debug('Unwrapping data of PublishReport.Node: ' + self.identity)
            self.references = {}
            self.textures = {}
            for key in self.data.keys():
                value = self.data[key]
                #if key not in scenePriorityList:
                if '_ref_paths' in key:
                    key = key.split("_ref_paths")[0]
                    for item in value: #item = ref_paths
                        if key in self.references.keys():
                            if item in self.references[key].keys():
                                self.references[key][item] = self.references[key][item] + 1
                            else:
                                self.references[key][item] = 1
                        else:
                            self.references[key] = {item:1}
                        self.parent.mention(key, item, self)

                elif '_texture_paths' in key:
                    for item in value:
                        if key in self.textures.keys():
                            if item in self.textures[key].keys():
                                self.textures[key][item] = self.textures[key][item] + 1
                            else:
                                self.textures[key][item] = 1
                        else:
                            self.textures[key] = {item: 1}

                elif '_OIDs' in key:
                    if key.split('_')[0] in ['Render', 'Light']:
                        self.OIDs = value

                elif '_MIDs' in key:
                    if key.split('_')[0] in ['Render', 'Light']:
                        self.MIDs = value


def cleanOIDList(shot_list, scope=None):
    list_of_sets = []
    for cur_shot in shot_list.values():
        list_of_sets.append(set(cur_shot))
    # all_assets = set()
    # for v in shot_list.values():
    #     all_assets |= set(v)
    flat_list = []
    for v in shot_list.values():
        flat_list.extend(v)
    all_assets = set(flat_list)

    # Make a dict of all the props in order of the most used one.
    counted = dict((i, flat_list.count(i)) for i in all_assets)
    most_use_list = list(reversed(sorted(counted.items(), key=lambda x: x[1])))

    # Make a dict of asset as keys, with a value thats a list of all other assets they don't share shots with.
    final_dict = {}
    for asset in all_assets:
        asset_set = {asset}
        for shot_set in list_of_sets:
            if asset in shot_set:
                asset_set |= shot_set
        result = all_assets.difference(asset_set)
        final_dict[asset] = result

    # Go through and eliminate all the re-occurences of the assets, in lists.
    final_list = []
    clean_dict = final_dict.copy()
    ignore_list = []

    for k, v in most_use_list:
        if not k in ignore_list:
            temp_list = [k]
            clean_dict, ignore_list = updateDict(clean_dict, k, ignore_list)
            loop_list = []  # list(temp_dict[k])
            for in_p, in_u in most_use_list:
                if in_p in clean_dict[k]:
                    loop_list.append(in_p)
            for i, asset in enumerate(loop_list):
                if not asset in ignore_list:
                    clear = True
                    for item in temp_list[1:]:
                        if asset in final_dict[item]:
                            clear = False
                    if clear:
                        temp_list.append(asset)
                        clean_dict, ignore_list = updateDict(clean_dict, asset, ignore_list)
            final_list.append(temp_list)


if __name__ == '__main__':
    pr = PublishReport()
    pr.getData('Char_Main_Mia')
    # pr.printReferenceOverview()
    _string = formatReferenceInfo(pr.data['Char_Main_Mia'])
    print(_string)

