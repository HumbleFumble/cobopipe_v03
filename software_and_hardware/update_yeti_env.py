import os
# Yeti:
server_yeti_path = r"P:\tools\_Software\Yeti\Yeti372"
# create Bat file for running as admin from desktop manually

def WriteFile(save_location,save_content):
    with open(save_location, 'w+') as saveFile:
        saveFile.write(save_content)
    saveFile.close()

def run():

    path_parts = os.environ["PATH"].split(os.pathsep)
    final_parts = []
    for cur_path in path_parts:
        if os.path.dirname(server_yeti_path) in cur_path:
            final_parts.append(r"%s\bin" % server_yeti_path)
        else:
            final_parts.append(cur_path)
    new_path = os.pathsep.join(final_parts)

    if server_yeti_path in os.environ["VRAY_FOR_MAYA2020_PLUGINS"]:
        VRAY_FOR_MAYA2020_PLUGINS_parts = os.environ["VRAY_FOR_MAYA2020_PLUGINS"].split(os.pathsep)
        VRAY_FOR_MAYA2020_PLUGINS_final_parts = []
        for cur_v_path in VRAY_FOR_MAYA2020_PLUGINS_parts:
            if os.path.dirname(server_yeti_path) in cur_v_path:
                VRAY_FOR_MAYA2020_PLUGINS_final_parts.append(r"%s\bin" % server_yeti_path)
            else:
                VRAY_FOR_MAYA2020_PLUGINS_final_parts.append(cur_v_path)
        new_VRAY_FOR_MAYA2020_PLUGINS_final_parts = os.pathsep.join(VRAY_FOR_MAYA2020_PLUGINS_final_parts)
    else:
        new_VRAY_FOR_MAYA2020_PLUGINS_final_parts = r"%s;%s\bin" % (os.environ["VRAY_FOR_MAYA2020_PLUGINS"],server_yeti_path)



    bat_string = r"""setx YETI_HOME "{yeti_path}" /m
    setx VRAY_FOR_MAYA2020_PLUGINS  "{new_VRAY_FOR_MAYA2020_PLUGINS_final_parts}" /m
    setx peregrinel_LICENSE "5053@CPHBOM-AP01" /m
    setx YETI_INTERACTIVE_LICENSE "5053@CPHBOM-AP01" /m
    setx VRAY_PLUGINS "{yeti_path}\bin" /m
    setx MAYA_MODULE_PATH "{yeti_path}" /m
    ECHO "REMEMBER TO SET YETI BIN IN THE PATH ENV MANUALLY!!!"
    PAUSE
    """.format(yeti_path=server_yeti_path,new_VRAY_FOR_MAYA2020_PLUGINS_final_parts=new_VRAY_FOR_MAYA2020_PLUGINS_final_parts)
    # Save in set_yeti_env.bat
    cur_user = (os.environ['USERPROFILE']).replace("\\", "/")
    yeti_bat_file_path = "{}/Desktop/UPDATE_YETI_ENV.BAT".format(cur_user)
    WriteFile(yeti_bat_file_path, bat_string)

if __name__ == "__main__":
    run()
    print("REMEMBER TO SET YETI BIN IN THE PATH ENV MANUALLY!!!")