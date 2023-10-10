import os
import re
import sys

import pyperclip
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
        self.text_input.setText("""ElfGarden_EXT_0100
ElfGarden_EXT_0200
ElfGarden_EXT_0300"""
        )

        self.button.clicked.connect(self.run)

    def run(self):
        backgrounds = self.text_input.toPlainText().split("\n")
        _dict = {}
        files = find_files(
            backgrounds, base_path="P:\930462_HOJ_Project\Production\Asset\Environment"
        )
        for file in files:
            filename = file.split("/")[-1].replace(".psd", "")
            _dict[filename] = []
            psd = PSDImage.open(file)
            for layer in psd:
                if layer.kind == "group":
                    if re.match("(S)\\d{3}(_SQ)\\d{3}(_SH)\\d{3}", layer.name, re.I):
                        _dict[filename].append(layer.name)

        _string = ""
        for filename, groups in _dict.items():
            _string = _string + f"{filename}\t{groups[0]}\r\n"
            for group in groups[1:]:
                _string = _string + f"\t{group}\r\n"
        pyperclip.copy(_string)

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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
