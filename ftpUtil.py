import os
from ftplib import FTP


def upload(files: list, host: str, username: str, password: str):
    """ Example of how to pass 'files' argument.
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
    """ Example of how to pass 'files' argument.
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
            destination_file = os.path.join(destination, filename).replace(os.sep, '/')
            ftp.cwd(source_folder)

            with open(destination_file, "wb") as f:
                print(f"Downloading {filename}")
                result = ftp.retrbinary(f'RETR {filename}', f.write)

            if result != "226 Transfer complete":
                successful = False

    return successful


if __name__ == "__main__":
    pass
    # files = [
    #     {
    #         "file": "_ANIMATION/Mads/FROM_CB/S102_SQ120_SH110.zip",
    #         "destination": "C:\Users\mha\Desktop\destination",
    #     }
    # ]
    # host = "192.168.0.6"
    # username = "HOJ_FTP"
    # password = "valhalla"
    # download(files, host, username, password)
