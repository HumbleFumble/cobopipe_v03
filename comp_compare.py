from subprocess import PIPE, Popen

import ffmpeg

from getConfig import getConfigClass
from Preview.ffmpeg_util import CropIn

CC = getConfigClass()


def create_comp_compare(anim_file, comp_file, output_file):
    comp_stream = ffmpeg.input(comp_file)

    anim_stream = ffmpeg.input(anim_file).video
    anim_stream = anim_stream.filter(
        "format", "gbrp"
    )  # Do this or shit will be green. And you don't want shit to be green. mmmmKay?

    width = CC.project_settings.get("tb_width")
    height = CC.project_settings.get("tb_height")
    anim_stream = CropIn(anim_file, anim_stream, width=width, height=height)
    anim_stream = anim_stream.filter("blend", all_mode="difference")

    combined = ffmpeg.overlay(comp_stream, anim_stream)

    out = ffmpeg.output(combined, output_file, pix_fmt="yuv420p")
    cmd = ffmpeg.compile(out, overwrite_output=True)
    process = Popen(cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()
    return output_file


if __name__ == "__main__":
    comp_file = "P:/930462_HOJ_Project/Production/Film/S112/S112_SQ010/S112_SQ010_SH060/_CompOutput/S112_SQ010_SH060_CompOutput.mov"
    anim_file = "P:/930462_HOJ_Project/Production/Film/S112/S112_SQ010/S112_SQ010_SH060/Passes/BaseFile_%4d.tga"
    output_file = "P:/930462_HOJ_Project/Production/Film/S112/S112_SQ010/S112_SQ010_SH060/CompCompare/S112_SQ010_SH060_CompCompare.mov"
    create_comp_compare(anim_file, comp_file, output_file)
