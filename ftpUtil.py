import os
import time
from ftplib import FTP
from getConfig import getConfigClass


def upload(files: list, host: str, username: str, password: str):
    """Example of how to pass 'files' argument.
    files = [
        {
            "file": "P:/930462_HOJ_Project/Production/Film/S102/S102_SQ120/S102_SQ120_SH110/S102_SQ120_SH110.zip",
            "destination": "_ANIMATION/Mads/FROM_CB/"
        }
    ]
    """

    successful = True

    with FTP() as ftp:
        ftp.connect(host, 2121)
        ftp.login(username, password)

        for file_object in files:
            file = file_object.get("file")
            destination = file_object.get("destination")
            if not file and not destination:
                continue

            ftp.cwd(destination)
            filename = os.path.basename(file)

            with open(file, "rb") as f:
                print(f"Uploading {filename}")
                result = ftp.storbinary(f"STOR {filename}", f)

            if result != "226 Transfer complete":
                successful = False

    return successful


def download(files: list, host: str, username: str, password: str):
    """Example of how to pass 'files' argument.
    files = [
        {
            "file": "_ANIMATION/Mads/FROM_CB/S102_SQ120_SH110.zip",
            "destination": "P:/930462_HOJ_Project/Production/Film/S102/S102_SQ120/S102_SQ120_SH110"
        }
    ]
    """

    successful = True

    with FTP() as ftp:
        ftp.connect(host, 2121)
        ftp.login(username, password)

        for file_object in files:
            file = file_object.get("file")
            destination = file_object.get("destination")
            if not file and not destination:
                continue

            source_folder = os.path.dirname(file)
            filename = os.path.basename(file)
            destination_file = os.path.join(destination, filename).replace(os.sep, "/")
            ftp.cwd(source_folder)

            with open(destination_file, "wb") as f:
                print(f"Downloading {filename}")
                result = ftp.retrbinary(f"RETR {filename}", f.write)

            if result != "226 Transfer complete":
                successful = False

    return successful


def mirror_folder_tree_to_FTP(
    server_root: str, ftp_root: str, host: str, username: str, password: str
):
    with FTP() as ftp:
        ftp.connect(host, 2121)
        ftp.login(username, password)

        for directory, dirnames, filenames in os.walk(SERVER_ROOT):
            current_ftp_dir = directory.replace(SERVER_ROOT, FTP_ROOT).replace(
                "\\", "/"
            )

            ftp.cwd(current_ftp_dir)

            ftp_item_list = []
            ftp.retrlines("LIST", ftp_item_list.append)

            dir_list = []
            for i, item in enumerate(ftp_item_list):
                if item.upper().startswith("D"):
                    dir_list.append(item.split()[-1])

            for dirname in dirnames:
                if dirname.lower == "_archive":
                    continue

                if dirname not in dir_list:
                    ftp.mkd(dirname)


if __name__ == "__main__":
    CC = getConfigClass(project_name="Hoj")
    SERVER_ROOT = "P:/930462_HOJ_Project/Production/Asset/Environment"
    FTP_ROOT = "/_LAYOUT_and_BACKGROUND/Testing_Mads"
    host = CC.project_settings.get("ftp_local_host")
    username = CC.project_settings.get("ftp_username")
    password = CC.project_settings.get("ftp_password")
    mirror_folder_tree_to_FTP(
        server_root=SERVER_ROOT,
        ftp_root=FTP_ROOT,
        host=host,
        username=username,
        password=password,
    )

    # filelist = []
    # ftp.retrlines('LIST', filelist.append)
    # print(filelist)

    # ftp.mkd(dirname)
    # ftp.cwd(FTP_ROOT)
    # print(directory_exists('test01'))
