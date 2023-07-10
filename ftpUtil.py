import os
import shutil
from ftplib import FTP
from getConfig import getConfigClass
from file_util import load_json, save_json


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


def download(files: list, host: str, username: str, password: str, ftp: FTP):
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


def get_directories():
    ftp_item_list = []
    ftp.retrlines("LIST", ftp_item_list.append)

    dir_list = []
    for i, item in enumerate(ftp_item_list):
        if item.upper().startswith("D"):
            dir_list.append(item.split()[-1])

    return dir_list


def ftp_walk(directory):
    try:
        ftp.cwd(directory)
    except:
        return

    ftp_item_list = []
    ftp.retrlines("LIST", ftp_item_list.append)

    dirnames = []
    filenames = []
    for i, item in enumerate(ftp_item_list):
        if item.upper().startswith("D"):
            dirnames.append(" ".join(item.split()[8:]))
        elif item.upper().startswith("-"):
            filenames.append(" ".join(item.split()[8:]))

    yield directory, dirnames, filenames

    for dirname in dirnames:
        new_directory = (
            os.path.join(directory, dirname).replace("\\", "/").replace("//", "\\\\")
        )
        yield from ftp_walk(new_directory)


def mirror_folder_tree_to_FTP(
    server_dir: str,
    ftp_dir: str,
    host: str,
    username: str,
    password: str,
    port: int,
    run_local: bool,
):
    if run_local:
        for directory, dirnames, filenames in os.walk(server_dir):
            if directory == server_dir:
                continue

            if directory.lower().endswith(("_archive", "_automated_history")):
                continue

            current_ftp_dir = (
                directory.replace(server_dir, ftp_dir)
                .replace("\\", "/")
                .replace("//", "\\\\")
            )

            if not os.path.exists(current_ftp_dir):
                print(f" > Creating {current_ftp_dir}")
                os.makedirs(current_ftp_dir)

            # else:
            #     print(f".. {current_ftp_dir}")

    else:
        with FTP() as ftp:
            ftp.connect(host, port)
            ftp.login(username, password)

            for directory, dirnames, filenames in os.walk(server_dir):
                current_ftp_dir = directory.replace(server_dir, ftp_dir).replace(
                    "\\", "/"
                )

                ftp.cwd(current_ftp_dir)

                ftp_item_list = []
                ftp.retrlines("LIST", ftp_item_list.append)

                dir_list = []
                for i, item in enumerate(ftp_item_list):
                    if item.upper().startswith("D"):
                        dir_list.append(" ".join(item.split()[8:]))

                for dirname in dirnames:
                    if dirname.lower() == "_archive":
                        continue

                    if dirname not in dir_list:
                        print(f" > Creating {current_ftp_dir}/{dirname}")
                        ftp.mkd(dirname)

                    # else:
                    #     print(f"... {current_ftp_dir}/{dirname}")


def fetch_from_mirror_folder_tree(
    server_dir: str,
    ftp_dir: str,
    host: str,
    username: str,
    password: str,
    port: int,
    run_local: bool,
):
    if run_local:
        for directory, dirnames, filenames in os.walk(ftp_dir):
            if directory == server_dir:
                continue

            if directory.lower().endswith(("_archive", "_automated_history")):
                continue

            for filename in filenames:
                if filename.endswith((".DS_Store")):
                    # print(f".. Skipping {filename} as file type is blacklisted.")
                    continue

                server_dirname = directory.replace(ftp_dir, server_dir)

                ftp_filepath = ftp_filepath = (
                    os.path.join(directory, filename)
                    .replace("\\", "/")
                    .replace("//", "\\\\")
                )
                server_filepath = (
                    os.path.join(server_dirname, filename)
                    .replace("\\", "/")
                    .replace("//", "\\\\")
                )

                if os.path.exists(server_filepath):
                    # print(f".. Skipping {filename} as it already exists on the server.")
                    continue

                print(f" > Downloading {ftp_filepath}")
                shutil.copy2(ftp_filepath, server_filepath)
                ftp_archive_dir = (
                    os.path.join(directory, "_AUTOMATED_HISTORY")
                    .replace("\\", "/")
                    .replace("//", "\\\\")
                )

                if os.path.exists(ftp_archive_dir):
                    continue

                os.makedirs(ftp_archive_dir)
                ftp_archive_filepath = (
                    os.path.join(ftp_archive_dir, filename)
                    .replace("\\", "/")
                    .replace("//", "\\\\")
                )
                shutil.move(ftp_filepath, ftp_archive_filepath)

    else:
        with FTP() as ftp:
            ftp.connect(host, port)
            ftp.login(username, password)

            failed_transfers = []
            for directory, dirnames, filenames in ftp_walk(ftp_dir):
                if os.path.dirname(directory).lower != "_archive":
                    for filename in filenames:
                        server_dirname = directory.replace(ftp_dir, server_dir)

                        if not os.path.exists(server_dirname):
                            os.makedirs(server_dirname)

                        ftp_filepath = (
                            os.path.join(directory, filename)
                            .replace("\\", "/")
                            .replace("//", "\\\\")
                        )
                        server_filepath = (
                            os.path.join(server_dirname, filename)
                            .replace("\\", "/")
                            .replace("//", "\\\\")
                        )

                        if os.path.exists(server_filepath):
                            print(
                                f".. Skipping {filename} as it already exists on the server."
                            )
                            continue

                        if filename.endswith((".DS_Store")):
                            # print(
                            #     f".. Skipping {filename} as file type is blacklisted."
                            # )
                            continue

                        with open(server_filepath, "wb") as f:
                            print(f" > Downloading {filename}.")
                            result = ftp.retrbinary(f"RETR {filename}", f.write)

                        if result != "226 Transfer complete":
                            print(f" <!> Download of {filename} failed.")
                            failed_transfers.append((ftp_filepath, result))
                        else:
                            # Moving to _Archive folder
                            ftp_archive_dir = (
                                os.path.join(directory, "_Archive")
                                .replace("\\", "/")
                                .replace("//", "\\\\")
                            )
                            if "_Archive" not in dirnames:
                                ftp.mkd(ftp_archive_dir)
                            ftp_archive_filepath = (
                                os.path.join(ftp_archive_dir, filename)
                                .replace("\\", "/")
                                .replace("//", "\\\\")
                            )
                            ftp.rename(ftp_filepath, ftp_archive_filepath)


def maintain_ftp_mirror(
    ftp_local_host: str,
    ftp_port: int,
    ftp_username: str,
    ftp_password: str,
    server_dir: str,
    ftp_dir: str,
    run_local: bool,
):
    print('.. Fetching from FTP Mirror\n')
    fetch_from_mirror_folder_tree(
        server_dir=server_dir,
        ftp_dir=ftp_dir,
        host=ftp_local_host,
        username=ftp_username,
        password=ftp_password,
        port=ftp_port,
        run_local=run_local,
    )

    print('\n.. Updating FTP Mirror')
    mirror_folder_tree_to_FTP(
        server_dir=server_dir,
        ftp_dir=ftp_dir,
        host=ftp_local_host,
        username=ftp_username,
        password=ftp_password,
        port=ftp_port,
        run_local=run_local,
    )

    print(' > Done!')


def maintain_ftp_mirrors():
    for dictionary in load_json(
        "T:/_Pipeline/cobopipe_v02-001/ftp_mirrors.json"
    ):
        maintain_ftp_mirror(**dictionary)


if __name__ == "__main__":
    maintain_ftp_mirrors()
    # x = load_json(r"C:\Users\mha\Projects\cobopipe_v02-001\ftp_mirrors.json")
    # save_json(r"C:\Users\mha\Projects\cobopipe_v02-001\ftp_mirrors.json", x)
