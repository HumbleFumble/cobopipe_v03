import os
import ffmpeg
import subprocess

def create_comp_compare(anim_file, comp_file, output_file):
    comp_stream = ffmpeg.input(comp_file)
    
    anim_stream = ffmpeg.input(anim_file).video
    anim_stream = anim_stream.filter("format", "gbrp")
    anim_stream = anim_stream.crop(width=1920, height=1080, x=96, y=54)
    anim_stream = anim_stream.filter("blend", all_mode='difference')
    
    combined = ffmpeg.overlay(comp_stream, anim_stream)
    
    out = ffmpeg.output(combined, output_file, pix_fmt='yuv420p')
    cmd = ffmpeg.compile(out, overwrite_output=True)
    subprocess.check_output(cmd)
    return