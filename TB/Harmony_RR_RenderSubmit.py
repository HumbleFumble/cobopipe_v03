import subprocess
try:
    from Log.CoboLoggers import getLogger
    logger = getLogger()
except:
    logger = None

def RenderSubmitInfo(render_file,return_cmd=False,project_name="MiasMagic2",user_name="mmcb_tb"):
    """
    Mostly hardcoded submitter for toonboom. For some reason only works with console submitter.
    :param render_file: The harmony file we want to render (.xstage)
    :param return_cmd: Only if we want the cmd line returned, nice for testing manually.
    :return:
    """
    # f = "C:/Temp/TB_Test2.txt"
    # fo = open(f,"w")
    # fo.write("WORKS=???")
    # fo.close()
    project_name = "%s_TB" % project_name
    if logger:
        logger.info("SUBMIT TB-FILE TO RR: %s" % render_file)
    #project_name = "MiasMagic2_TB"
    client_pool = "Toonboom"
    # user_name = "mmcb_tb"
    overwrite = True
    priority = 75
    software = "Harmony"
    software_version = "20"
    # render_file = "P:/930444_SprinterGalore_Animated_S01/Production/Film/E110/sq020/sh070/sh070/sh070_V001.xstage" #Testing
    # rr_submitter = "P:/tools/RoyalRender/bin/win64/rrSubmitter.exe" #Testing, can't make it submit properly without using the console :/
    rr_submitter = "%RR_Root%/bin/win64/rrSubmitterconsole.exe"
    rr_cmd = "%s %s" % (rr_submitter, render_file)  # Set scene
    # FLAGS
    # rr_cmd = '%s -NoAutoSceneRead' % (rr_cmd)  # set flag that so rr doesn't parse through maya scene
    if overwrite:
        rr_cmd = "%s -AutoDeleteEnabled" % (rr_cmd)  # set flag so rr deletes all files before rendering

    # SCENE INFO
    rr_cmd = "%s -S %s" % (rr_cmd, software)  # set software
    # rr_cmd = "%s -R %s" % (rr_cmd, render_software)  # set render plugin
    rr_cmd = "%s -V %s" % (rr_cmd, software_version)  # set software version
    rr_cmd = "%s -SOS win" % (rr_cmd)  # set os
    # rr_cmd = '%s -DB %s' % (rr_cmd, project_path)  # set project
    # rr_cmd = "%s -SLO Top" % (rr_cmd)  # set layer
    # rr_cmd = "%s -C %s" % (rr_cmd, "Camera")  # set camera
    # # Submitter flags:
    # rr_cmd = '%s "CSCN=0~%s"' % (rr_cmd, episode)  # set height
    # rr_cmd = '%s "CSHN=0~%s"' % (rr_cmd, sequence)  # set height
    # rr_cmd = '%s "CVN=0~%s"' % (rr_cmd, shot)  # set height
    rr_cmd = '%s "RenderPreviewFirst=1~0"' % (rr_cmd)  # Preview off
    rr_cmd = '%s "CropEXR=1~0"' % (rr_cmd)  #Crop EXR on off
    rr_cmd = '%s "CPN=0~%s"' % (rr_cmd, project_name)  # set project "nice" name
    rr_cmd = '%s "DCG=0~%s"' % (rr_cmd, client_pool)  # set client pool
    rr_cmd = '%s "UN=0~%s"' % (rr_cmd, user_name)  # set user name
    rr_cmd = '%s "Priority=1~%s"' % (rr_cmd, priority)  # set user name
    rr_cmd = '%s "PPSequenceCheck=1~0"' % (rr_cmd)  # sequenceCheck Off
    rr_cmd = '%s "PPCreateSmallVideo=1~0"' % (rr_cmd)  # create small video off
    if logger:
        logger.info(rr_cmd)
    #print(rr_cmd)
    # print("Scene Submitted to RoyalRender!")
    # with open('C:/Temp/SubmitLog.txt', 'w+') as log_file:
    # 	log_file.write(rr_cmd)
    # log_file.close()
    if return_cmd and return_cmd != "False":
        logger.info("Returning:" + rr_cmd)
        return rr_cmd
    subprocess.Popen(rr_cmd)

# if __name__ == '__main__':
#     CreateSceneSetup("test","","","",res_multi=1.1)