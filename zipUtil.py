import sys
import os
import zipfile


def zip(source, destination):
    if type(source) == str:
        source = [source]

    if not type(source) == list:
        raise TypeError

    zipName = os.path.basename(destination)
    destDir = os.path.dirname(destination)
    compress_type = zipfile.ZIP_DEFLATED

    os.chdir(destDir)
    zipFile = zipfile.ZipFile(zipName, "w")

    for item in source:
        item = os.path.abspath(item)
        if os.path.isdir(item):
            for root, dirs, files in os.walk(item):
                for file in files:
                    parentFolder = os.path.abspath(os.path.join(item, ".."))
                    zipFile.write(
                        os.path.join(root, file),
                        arcname=os.path.join(root.replace(parentFolder, ""), file),
                        compress_type=compress_type,
                    )
        else:
            zipFile.write(
                item, arcname=os.path.basename(item), compress_type=compress_type
            )

    zipFile.close()
    return zipFile


def unzip(source, destination=None, overwrite=False):
    if not destination:
        destination = os.path.dirname(source)
        
    with zipfile.ZipFile(source, "r") as compressed_data:
        if overwrite:
            compressed_data.extractall(destination)
        else:
            member_list = compressed_data.namelist()
            for member in member_list:
                file = os.path.abspath(os.path.join(destination, member))
                if not os.path.exists(file):
                    compressed_data.extract(member, path=destination)

    return compressed_data


if __name__ == "__main__":
    if len(sys.argv) > 3:
        if sys.argv[1] == 'zip':
            print('ZIPPING')
            zip(sys.argv[2:-1], sys.argv[-1])
        elif sys.argv[1] == 'unzip':
            print('UNZIPPING')
            overwrite = False
            if len(sys.argv) == 4:
                overwrite = sys.argv[4]
            unzip(sys.argv[2], destination=sys.argv[3], overwrite=overwrite)
