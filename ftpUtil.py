import os
from ftplib import FTP


def upload(files: list, host: str, username: str, password: str):
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
    successful = True

    with FTP() as ftp:
        ftp.connect(host, 2121)
        ftp.login(username, password)

        for file_object in files:
            # file = file_object.get("file")
            # destination = file_object.get("destination")
            # if not file and not destination:
            #     continue

            # ftp.cwd(destination)
            # filename = os.path.basename(file)

            # with open(file, "rb") as f:
            #     print(f"Uploading {filename}")
            #     result = ftp.storbinary(f"STOR {filename}", f)

            if result != "226 Transfer complete":
                successful = False

    return successful


if __name__ == "__main__":
    files = [
        {
            "file": r"C:\Users\mha\Desktop\641c0c982b1ba0b134035baa_jobInfo.job",
            "destination": "_ANIMATION/Mads/FROM_CB",
        }
    ]
    host = "192.168.0.6"
    username = "HOJ_FTP"
    password = "valhalla"
    upload(files, host, username, password)
