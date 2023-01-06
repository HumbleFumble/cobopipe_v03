import maya.cmds as cmds
def createOCIOCorrection():
    sel = cmds.ls(sl=True)
    for vn in sel:
        node_type = cmds.nodeType(sel)
        if node_type == "lambert":
            dif_plug = "%s.color" % vn
        else:
            dif_plug = "%s.diffuseColor" % vn
        my_cons = cmds.listConnections(dif_plug, p=True, d=True)
        my_ocio = cmds.shadingNode("VRayTexOCIO", asTexture=True)

        if my_cons:
            for cur_con in my_cons:
                print(cur_con)
                cmds.connectAttr(cur_con, "%s.baseTexture" % my_ocio, f=True)
                cmds.connectAttr("%s.outColor" % my_ocio, dif_plug, f=True)
                cmds.setAttr("%s.inColorSpace" % my_ocio, "Utility - sRGB - Texture", type="string")
                cmds.setAttr("%s.outColorSpace" % my_ocio, "ACES - ACEScg", type="string")
        else:
            dif_color = cmds.getAttr(dif_plug)
            cmds.setAttr("%s.baseTexture" % my_ocio, *dif_color[0], type="double3")
            cmds.setAttr("%s.inColorSpace" % my_ocio, "Utility - sRGB - Texture", type="string")
            cmds.setAttr("%s.outColorSpace" % my_ocio, "ACES - ACEScg", type="string")

            multi = cmds.shadingNode("multiplyDivide", asTexture=True)

            cmds.connectAttr("%s.outColor" % my_ocio, "%s.input1" % multi, f=True)
            cmds.setAttr("%s.mode" % my_ocio, 1)
            cmds.setAttr("%s.mode" % my_ocio, 0)

            ocio_color = cmds.getAttr("%s.input1" % multi)
            cmds.setAttr(dif_plug, *ocio_color[0], type="double3")

            cmds.delete([multi,my_ocio])

def removeGammas():
    """
    Meant to remove multiplyDivide nodes and GammaNodes that Vray generates with its linear workflow migrate tool.
    :return:
    """
    selection = cmds.ls(sl=True)
    for sel in selection:
        check_dict = {"gammaCorrect":{"input":"value","output":"outValue"},"multiplyDivide":{"input":"input2X","output":"output"}}
        #my_cons = cmds.listConnections(sel,plugs=True,scn=True)
        cur_type = cmds.nodeType(sel)
        if cur_type in check_dict:
            output_list = cmds.connectionInfo("%s.%s" % (sel,check_dict[cur_type]["output"]), dfs=True)
            input = cmds.connectionInfo("%s.%s" % (sel,check_dict[cur_type]["input"]), sfd=True)
            if input.endswith(".outAlpha"):
                input = input.replace(".outAlpha",".outColor")
            for output in output_list:
                print("Connection: %s ->%s" %(input,output))
                try:
                    cmds.connectAttr(input,output,f=True)
                except:
                    print("CAN'T CONNECT: %s -> %s" % (input,output))