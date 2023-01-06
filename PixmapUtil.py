# try:
#     from PyQt5 import QtWidgets, QtCore, QtGui
# except:
from PySide2 import QtCore, QtGui
import os
from Log.CoboLoggers import getLogger
logger = getLogger()


# site.addsitedir("P:/tools/_Scripts/Production_scripts/KiwiStrit/Maya_Functions")
# import site
# site.addsitedir("P:/tools/_Scripts/pipeline_scripts/Bombay_Python_Classes")
from Multiplicity.ThreadPool import Worker
from ffmpeg_wrapper import FFMPEG

from getConfig import getConfigClass
CC = getConfigClass()


class PixmapUtil(object):
    def __init__(self, view_state="comp"):
        self.__view_state = view_state
        self.__small_thumbs = (80, 45)
        self.__medium_thumbs = (160, 90)
        self.__large_thumbs = (320, 180)
        self.__current_size = None
        self.setSize(size="large")

    def setSize(self, size="large"):
        if size == "large":
            self.__current_size = self.__large_thumbs
        elif size == "medium":
            self.__current_size = self.__medium_thumbs
        elif size == "small":
            self.__current_size = self.__small_thumbs


    def changeViewState(self, view_state="comp"):
        self.__view_state = view_state

    def convertPathToPixmap(self, cache_name=None, image_path=None, width=None, height=None, added_name="",
                            overwrite_cache=False):
        """Actual method for pixmap creation"""

        if not width or not height:
            width, height = self.__current_size

        if not cache_name:
            cache_name = image_path
        key_value = "%s%s" % (cache_name, added_name)

        check_path = False
        pixmap = QtGui.QPixmapCache.find(key_value)
        if not pixmap:
            if image_path:
                if os.path.exists(image_path):
                    key_value = "%s%s" % (cache_name, added_name)
                    check_path = True
            if not check_path:
                image_path = CC.get_no_thumb_icon_path() #cfg_util.CreatePathFromDict(cfg.thumbnail_paths["no_thumb_icon_path"])
                # image_path = "./resources/icon/No_Thumbnail.png"
                key_value = "no_thumb_icon%s" % added_name
            pixmap = QtGui.QPixmapCache.find(key_value)
        if pixmap and overwrite_cache:  # Remove the key value from the cache so it will refresh with a new pixmap
            QtGui.QPixmapCache.remove(key_value)
            pixmap = None

        if not pixmap:
            pixmap = QtGui.QPixmap(image_path)
            pixmap = pixmap.scaled(width, height, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
            QtGui.QPixmapCache.insert(key_value, pixmap)
            pixmap = QtGui.QPixmapCache.find(key_value)

        return QtGui.QPixmap(pixmap)

    def createFactoryThreads(self, parent_node):
        seqs = parent_node.getChildren()
        result = []
        for seq in seqs:
            shots = seq.getChildren()
            for shot in shots:
                # print("Making thread")
                result.append(PixmapUtil.PixmapFactory(instance=self, node=shot))
        return result

    def createFactoryThread(self, node, overwrite=False, overwrite_cache=False):
        return self.PixmapFactory(instance=self, node=node, overwrite=overwrite, overwrite_cache=overwrite_cache)

    def createPixMap(self, cur_node=None, overwrite=False, overwrite_cache=False):
        """Be aware, pixmap creation actually occur in self.convertPathToPixmap()"""

        shot_name = cur_node.getName()
        if overwrite_cache:
            pixmap = None
        else:
            pixmap = QtGui.QPixmapCache.find(shot_name)
        if not pixmap or overwrite:

            image_path = self.__findThumbs(cur_node=cur_node, overwrite=overwrite)
            cur_node.setThumbPath(image_path)

            pixmap = self.convertPathToPixmap(
                cache_name=shot_name,
                image_path=image_path,
                overwrite_cache=overwrite_cache
            )
        return pixmap

    def __findThumbs(self, cur_node=None, overwrite=False):
        shot_name = cur_node.getName()
        shot_dict = {}
        shot_dict["episode_name"], shot_dict["seq_name"], shot_dict["shot_name"] = shot_name.split("_")
        shot_dict["render_prefix"] = "FastA"
        if not "preview_dict" in CC.__dict__.keys():
            thumb_paths = {"comp": ["shot_comp_output_file"],
                           "render":["shot_passes_folder"],
                           "anim": ["shot_anim_preview_file"],
                           "animatic": ["shot_animatic_file"]}
        else:
            thumb_paths = CC.preview_dict
        thumb_order = ["comp", "render","anim", "animatic"]
        thumb_order = thumb_order[thumb_order.index(self.__view_state):]  # Remove elements by index to make a shorter list
        for cur_thumb_level in thumb_order:
            for cur_thumb in thumb_paths[cur_thumb_level]:
                thumb_path = "%s/Thumbnails/%s_thumbnail.jpg" % (CC.get_shot_path(**shot_dict),shot_name)
                if os.path.exists(thumb_path) and not overwrite:
                    return thumb_path

                thumb_base_func = getattr(CC,"get_{func_name}".format(func_name=cur_thumb))
                thumb_base = thumb_base_func(**shot_dict)

                if cur_thumb_level == "render": #adding padding and format to the end of path
                    thumb_base ="%s.0001.exr" % thumb_base
                    # logger.info("Creating thumb for %s : %s" % (shot_name, thumb_paths[cur_thumb][0]))

                if os.path.exists(thumb_base):
                    logger.info("Creating thumb for %s : %s" % (shot_name, cur_thumb))
                    self.__saveAsSmallThumb(thumb_base, thumb_path,cur_thumb_level)
                    return thumb_path

    def __saveAsSmallThumb(self, from_image_path, to_image_path,thumb_type):

        temp_wrapper = FFMPEG(None)
        check_folder = os.path.split(to_image_path)[0]
        if not os.path.exists(check_folder):
            os.mkdir(check_folder)
        if from_image_path.endswith(".exr"):
            temp_wrapper.scaleImage(from_image_path, to_image_path, 320, True)
            # if thumb_type == "comp":
            #     temp_wrapper.scaleImage(from_image_path, to_image_path, 320, True)
            # else:
            #     temp_wrapper.scaleImage(from_image_path, to_image_path, 320, True)
        elif from_image_path.endswith(".mov") or from_image_path.endswith(".mp4"):
            temp_wrapper.videoToImage(from_image_path, to_image_path, 320, 0.05)

    # \\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\
    # NESTED CLASSES ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # /////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    class PixmapFactory(Worker):
        """
        A Factory object for creating pixmaps with threads in the 'ThreadPool' module
        """

        def __init__(self, instance, node, overwrite=False, overwrite_cache=False):
            super(PixmapUtil.PixmapFactory, self).__init__()
            self.instance = instance
            self.__node = node
            self.__overwrite = overwrite
            self.__overwrite_cache = overwrite_cache


        def run(self):
            # self.signals.created.emit({"created":"Creating Pixmap for %s" % self.__node.getName()})
            self.instance.createPixMap(cur_node=self.__node, overwrite=self.__overwrite,overwrite_cache=self.__overwrite_cache)
            self.signals.finished.emit(self.output)
            # self.signals.result.emit({"result":self.__node})
