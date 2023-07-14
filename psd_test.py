import os
import re
import sys

from psd_tools import PSDImage
from PySide6.QtWidgets import QApplication, QPushButton, QTextEdit, QVBoxLayout, QWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BG-O-Matic")

        self.main_layout = QVBoxLayout()

        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText(
            "Insert name of background, each name on their own line."
        )
        self.text_input.setAcceptRichText(False)
        self.button = QPushButton("Run")

        self.main_layout.addWidget(self.text_input)
        self.main_layout.addWidget(self.button)

        self.setLayout(self.main_layout)

        # FOR TESTING PURPOSES
        self.text_input.setText(
            """ElfGarden_EXT_0100
ElfGarden_EXT_0200
ElfGarden_EXT_0300"""
        )

        self.button.clicked.connect(self.run)

    def run(self):
        backgrounds = self.text_input.toPlainText().split("\n")
        files = find_files(
            backgrounds, base_path="P:\930462_HOJ_Project\Production\Asset\Environment"
        )
        for file in files:
            psd = PSDImage.open(file)
            groups = []
            for layer in psd:
                if layer.kind == "group":
                    if re.match("(S)\\d{3}(_SQ)\\d{3}(_SH)\\d{3}", layer.name, re.I):
                        groups.append(layer.name)
            print(groups)


def find_files(names=[], base_path=""):
    return_list = []
    for root, folder, files in os.walk(base_path):
        for cur_file in files:
            if any(name in cur_file for name in names):
                if "_v001" in cur_file.lower():
                    file_path = (
                        os.path.join(root, cur_file)
                        .replace(os.sep, "/")
                        .replace("//", "\\\\")
                    )
                    return_list.append(file_path)
    return return_list


# psd = PSDImage.open(test_file)
# for layer in psd:
#     if layer.name == 'STB':
#         layer.visible = True
#         comp = layer.composite()
#         size = 124, 124
#         comp.thumbnail(size)
#         comp.save('C:/Users/mha/Desktop/STB_thumbnail.png')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
