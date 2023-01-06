def run():
    import os
    import shutil
    print("RUNNING")
    desktop_ffmpeg = os.path.expanduser("~/Desktop/ffmpeg").replace(os.sep, "/")
    find_ffmpeg = shutil.which("ffmpeg")
    if find_ffmpeg:
        find_ffmpeg = os.path.dirname(os.path.dirname(find_ffmpeg))
    else:
        find_ffmpeg = "C:/Program Files/ffmpeg/"
    print(find_ffmpeg)
    if os.path.exists(find_ffmpeg):
        shutil.rmtree(find_ffmpeg)
    shutil.copytree(desktop_ffmpeg, find_ffmpeg)
run()