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
    zipFile = zipfile.ZipFile(zipName, 'w')

    for item in source:
        item = os.path.abspath(item)
        if os.path.isdir(item):
            for root, dirs, files in os.walk(item):
                for file in files:
                    parentFolder = os.path.abspath(os.path.join(item, '..'))
                    zipFile.write(os.path.join(root, file), arcname=os.path.join(
                        root.replace(parentFolder, ""), file), compress_type=compress_type)
        else:
            zipFile.write(item, arcname=os.path.basename(
                item), compress_type=compress_type)

    zipFile.close()
    return zipFile


if __name__ == '__main__':
    if len(sys.argv) > 2:
        zip(sys.argv[1:-1], sys.argv[-1])
