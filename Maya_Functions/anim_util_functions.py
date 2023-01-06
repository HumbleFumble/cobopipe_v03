import maya.cmds as cmds
import maya.mel as mel

import os

from getConfig import getConfigClass
CC = getConfigClass()

from Log.CoboLoggers import getLogger
logger = getLogger()


def CleanUpAnimationScene(shot_name):
    import Maya_Functions.general_util_functions as gen_util
    import Maya_Functions.delete_and_clean_up_functions as del_util
    # get assets linked to shot.
    logger.info("CLEANING UP: %s" % shot_name)
    shot_assets = gen_util.GetAssetsinShot(shot_name)
    logger.info("%s linked with: %s" % (shot_name, shot_assets))
    # remove all assets not linked to shot.
    if shot_assets:
        gen_util.RemoveAssets(shot_assets)
    else:
        gen_util.RemoveAssets(["REMOVE_ALL"])
    # Delete all other shots
    logger.info("%s: Deleting other shots" % shot_name)
    all_shots = cmds.ls(type="shot")
    for cur_shot in all_shots:
        if not cur_shot == shot_name:
            logger.debug("Deleting cam for %s" % cur_shot)
            cur_shot_audio = cmds.shot(cur_shot, q=True, audio=True)
            if cur_shot_audio:
                if cmds.objExists(cur_shot_audio):
                    cmds.delete(cur_shot_audio)
            cmds.delete(cur_shot)
            cmds.delete("%s_Cam" % cur_shot)
    all_audio = cmds.ls(type="audio")
    for cur_a in all_audio:
        if not shot_name in cur_a:
            cmds.delete(cur_a)
    #Delete unconnected cameras
    logger.info("%s: Deleting other Cams" % shot_name)
    cams = cmds.ls("*_Cam")
    for c in cams:
        if not c == "%s_Cam" % shot_name:
            if cmds.listRelatives(c, type="camera"):
                logger.debug("Deleting cam: %s" % c)
                cmds.delete(c)

    # Set maya and sequence start time to 1
    shot_start = cmds.shot(shot_name, q=True, st=True)
    shot_duration = cmds.shot(shot_name, q=True, et=True) - shot_start
    cmds.shot(shot_name, e=True, st=1, et=shot_duration + 1, sst=1)

    logger.info("%s: Moving keys" % shot_name)
    # Move all animation keys back
    move_amount = 1 - shot_start
    MoveAnimation(-1000, 10000, move_amount)
    # Set the correct timeline range
    # cmds.modelPanel(self.focus_view, edit=True, camera="%s_Cam" %cur_shot)
    cmds.playbackOptions(minTime=1, maxTime=shot_duration + 1)

    c_cam_shape = "%s_CamShape" % shot_name
    c_cam = "%s_Cam" % shot_name

    if cmds.objExists(c_cam):
        cmds.camera(c_cam_shape, e=True, lt=False)
        cmds.currentTime(1)
        cmds.setKeyframe([c_cam,c_cam_shape], t=1)
        cmds.currentTime(shot_duration+1)
        cmds.setKeyframe([c_cam,c_cam_shape], t=shot_duration+1)
        cmds.camera(c_cam_shape, e=True, lt=True)

    logger.info("%s: correcting ImageShape" % shot_name)
    if cmds.objExists("%s_IMShape2" % shot_name):
        im = "%s_IMShape2" % shot_name
        cmds.setAttr("%s.frameOffset" % im, 0)
        cmds.setAttr("%s.frameIn" % im, 1)
        cmds.setAttr("%s.frameOut" % im, shot_duration + 1)
    #Delete keys outside of the time range
    del_util.DeleteKeyframes(time_start=-10000,time_end=-5)
    del_util.DeleteKeyframes(time_start=shot_duration+25,time_end=10000)
    del_util.DeleteUnknown()

    logger.info("%s: DONE!" % shot_name)


def MoveAnimation(start, end, amount):
    """
    Tries to move all animation keys within the range, the given amount. Can't move keys on referenced objects
    """
    anim_keys = cmds.ls(type=["animCurveTA", "animCurveTU", "animCurveTL"])
    if anim_keys != "" and anim_keys != []:
        cmds.scaleKey(anim_keys, time=(start, end), nst=(start + amount), net=(end + amount))

def CreateShotNode(name="", range=0, start=1, seq_start=1, ep="", seq="",cam=None):
    """
    Create a camera-sequencer node with camera, based on name and length given.
    """
    start_time = start + 1
    end_time = start + range
    seq_start_time = seq_start + 1

    animatic_clip = CC.get_shot_animatic_file(episode_name=ep,seq_name=seq,shot_name=name)
    sound_clip = CC.get_shot_sound_file(episode_name=ep, seq_name=seq, shot_name=name)

    image_plane_stack = "%s/ImagePlane/%s_%s_%s_ImagePlane.1.jpg" % (CC.get_shot_path(episode_name=ep,seq_name=seq,shot_name=name), ep, seq, name)

    if image_plane_stack.endswith(".mov"):
        single_movie = True
    else:
        single_movie = False
    logger.info("import animatic: %s \\n import sound: %s" % (animatic_clip, sound_clip))
    # Create shot node
    if os.path.exists(sound_clip):
        new_shot = cmds.shot(name, st=start_time, et=end_time, sst=seq_start_time, audio=sound_clip)
    else:
        new_shot = cmds.shot(name, st=start_time, et=end_time, sst=seq_start_time)

    if cam:
        new_camera = cmds.duplicate(cam, n="%s_Cam" % name, un=True)[0]

    else:
        new_camera = cmds.camera(n="%s_Cam" % name)
        new_camera = cmds.rename(new_camera[0], new_camera[0][0:-1])
    cam_shape = cmds.listRelatives(new_camera, type="camera")[0]

    for ip in cmds.ls(type="imagePlane"):
        if cmds.imagePlane(ip, q=True, camera=True)[0] == cam_shape:
            ip_p = cmds.listRelatives(ip, allParents=True)
            cmds.delete(ip_p)

    # set aspect ratio to 16:9
    cmds.camera(new_camera, e=True, aspectRatio=1.777777777777778)

    # IM_name = "SH010_IM"
    IM_name = name + "_IM"

    cur_plane = cmds.imagePlane(n=IM_name, c="%s_Cam" % name, fileName=image_plane_stack)
    cmds.imagePlane(cur_plane[0], e=True, sia=False, lt=new_camera)
    # if total_time:
    cmds.setAttr("%s.frameCache" % cur_plane[1], range)
    cmds.setAttr("%s.useFrameExtension" % cur_plane[1], 1)
    cur_offset = -1 * start

    if single_movie:
        cmds.setAttr("%s.type" % cur_plane[1], 2)
        cmds.setAttr("%s.frameIn" % cur_plane[1], start_time)
        cmds.setAttr("%s.frameOut" % cur_plane[1], end_time)
    else:
        cmds.setAttr("%s.type" % cur_plane[1], 0)
    cmds.setAttr("%s.frameOffset" % cur_plane[1], cur_offset)
    cmds.setAttr("%s.depth" % cur_plane[1], 1)

    cmds.addAttr(name, ln="assetlinks", dt="string")  # Add attribute to shot node

    cmds.connectAttr("%s.message" % cam_shape, "%s.currentCamera" % new_shot, f=True)