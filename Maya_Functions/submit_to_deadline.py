import os
import random
import string
import Deadline.util as deadutil
from getConfig import getConfigClass
import maya.cmds as cmds

CC = getConfigClass()


def submit(jobName="", pool='', priority=50, output_file_path=""):
    scene_file = cmds.file(query=True, sceneName=True)
    if jobName == "":
        jobName = os.path.basename(scene_file).replace(".ma", "").replace(".mb", "")
    if not output_file_path:
        output_file_path = get_output_directory()
    output_directory = os.path.dirname(output_file_path)
    output_filename = os.path.basename(output_file_path)
    output_file_prefix = os.path.splitext(output_filename)[0]
    workspace = cmds.workspace(query=True, fullName=True)

    group = cmds.getAttr("defaultRenderGlobals.currentRenderer")
    if not pool:
        pool = CC.project_settings.get("deadline_pool")
    is_animated_on = cmds.getAttr("defaultRenderGlobals.animation")
    frame_range = get_frame_range(is_animated_on)
    renderable_cameras = get_renderable_cameras()
    render_camera = renderable_cameras[0]
    number_of_renderable_cameras = len(renderable_cameras)
    image_height = cmds.getAttr("defaultResolution.height")
    image_width = cmds.getAttr("defaultResolution.width")
    renderer = cmds.getAttr("defaultRenderGlobals.currentRenderer")
    maya_version = cmds.about(version=True)

    tempFolder = deadutil.callDeadlineCommand("-GetCurrentUserHomeDirectory")
    tempFolder = trim(tempFolder)
    tempFolder = os.path.join(tempFolder, "temp")
    random_string = ''.join(random.choice(string.ascii_lowercase + '0123456789') for i in range(6))
    

    jobInfoFilePath = jobInfoFile(
        tempFolder,
        random_string,
        jobName,
        output_directory,
        output_filename,
        group,
        pool,
        priority,
        frame_range,
    )

    pluginInfoFilePath = pluginInfoFile(
        tempFolder,
        random_string,
        is_animated_on,
        render_camera,
        number_of_renderable_cameras,
        image_height,
        image_width,
        output_directory,
        output_file_prefix,
        workspace,
        renderer,
        scene_file,
        maya_version,
    )

    deadutil.callDeadlineCommand(jobInfoFilePath, pluginInfoFilePath)


def jobInfoFile(
    tempFolder,
    random_string,
    jobName,
    output_directory,
    output_filename,
    group,
    pool,
    priority,
    frame_range,
):
    jobInfoFilePath = os.path.join(tempFolder, f"maya_submit_info_{random_string}.job")

    lines = [
        f"Name={jobName}",
        f"Frames={frame_range}",
        f"Pool={pool}",
        f"Group={group}",
        f"Priority={priority}",
        f"OutputDirectory0={output_directory}",
        f"OutputFilename0={output_filename}",
        f"OverrideTaskExtraInfoNames=False",
        f"Plugin=MayaBatch",
    ]

    with open(jobInfoFilePath, "w") as f:
        for line in lines:
            f.write(f"{line}\n")

    return jobInfoFilePath


def pluginInfoFile(
    tempFolder,
    random_string,
    is_animated_on,
    render_camera,
    number_of_renderable_cameras,
    image_height,
    image_width,
    output_directory,
    output_file_prefix,
    workspace,
    renderer,
    scene_file,
    maya_version,
):
    pluginInfoFilePath = os.path.join(tempFolder, f"maya_plugin_info_{random_string}.job")

    lines = [
        f"Animation={is_animated_on}",
        f"Camera={render_camera}",
        f"CountRenderableCameras={number_of_renderable_cameras}",
        f"ImageHeight={image_height}",
        f"ImageWidth={image_width}",
        f"LocalRendering=0",
        f"MaxProcessors=0",
        f"OutputFilePath={output_directory}",
        f"OutputFilePrefix={output_file_prefix}",
        f"ProjectPath={workspace}",
        f"RenderHalfFrames=0",
        f"RenderLayer=",
        f"RenderSetupIncludeLights=1",
        f"Renderer={renderer}",
        f"SceneFile={scene_file}",
        f"SelectGPUDevices=",
        f"StartupScript=",
        f"StrictErrorChecking=1",
        f"UseLegacyRenderLayers=0",
        f"UseLocalAssetCaching=0",
        f"UsingRenderLayers=0",
        f"VRayAutoMemoryBuffer=500",
        f"VRayAutoMemoryEnabled=0",
        f"Version={maya_version}"
    ]

    with open(pluginInfoFilePath, "w") as f:
        for line in lines:
            f.write(f"{line}\n")

    return pluginInfoFilePath


def trim(_string):
    return _string.replace("\n", "").replace("\r", "")


def get_output_directory():
    renderer = cmds.getAttr("defaultRenderGlobals.currentRenderer")
    if renderer == "vray":
        output_directory = cmds.getAttr("vraySettings.fileNamePrefix")

    elif renderer == "arnold":
        output_directory = cmds.getAttr("defaultRenderGlobals.imageFilePrefix")
        print(output_directory)

    if not output_directory:
        workspace_directory = cmds.workspace(query=True, fullName=True)
        scene_name = os.path.basename(cmds.file(query=True, sceneName=True))
        for scene_extension in [".ma", ".mb"]:
            scene_name = scene_name.replace(scene_extension, "")

        if renderer == "vray":
            file_extension = cmds.getAttr("vraySettings.imageFormatStr")
        elif renderer == "arnold":
            file_extension = cmds.getAttr("defaultArnoldDriver.ai_translator")

        output_directory = os.path.join(
            workspace_directory, f"{scene_name}.{file_extension}"
        )

    return output_directory


def get_frame_range(is_animated_on):
    renderer = cmds.getAttr("defaultRenderGlobals.currentRenderer")

    if not is_animated_on:
        return int(cmds.currentTime(query=True))

    if renderer == "vray":
        vray_anim_type = cmds.getAttr("vraySettings.animType")
        if vray_anim_type == 2:
            frame_list = cmds.getAttr("vraySettings.animFrames")
            # VRay frame list format = "from-to;increment,from-to;increment,..."
            # Deadline frame list format = "from - to x increment, from - to x increment,;..."
            frame_list = frame_list.replace(';', ' x ').replace(',', ', ')
            return frame_list

    start_frame = int(cmds.getAttr('defaultRenderGlobals.startFrame'))
    end_frame = int(cmds.getAttr('defaultRenderGlobals.endFrame'))
    by_step = int(cmds.getAttr('defaultRenderGlobals.byFrameStep'))

    if start_frame == end_frame:
        return start_frame

    if not by_step > 1:
        return f'{start_frame} - {end_frame}'

    return f'{start_frame} - {end_frame} x {by_step}'
        


def get_renderable_cameras():
    return [
        cmds.listRelatives(camera_shape, parent=True)[0]
        for camera_shape in cmds.ls(exactType="camera")
        if is_camera_renderable(camera_shape)
    ]


def is_camera_renderable(camera_shape):
    if cmds.attributeQuery("renderable", node=camera_shape, exists=True):
        return cmds.getAttr(f"{camera_shape}.renderable")
    return False
