import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox
from ProjectWindow.CodeEditor.initialCode import initialCode


class CreateNewFileDialog(QDialog):
    def __init__(self, filePath, fileExtension:str):
        super().__init__()

        self.setWindowTitle("Create {} File".format(fileExtension.capitalize()))
        self.setWindowIcon(QIcon('../icon/newproject.svg'))
        self.filePath = filePath
        self.fileExtension = fileExtension
        self.successful = False

        layout = QVBoxLayout()
        self.fileNameField = QLineEdit()
        self.fileNameField.setPlaceholderText("File Name")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(self.fileNameField)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def accept(self):
        super().accept()
        try:
            file = open(os.path.join(self.filePath, self.fileNameField.text()+"."+self.fileExtension), "x")
            file.write(initialCode[self.fileExtension])
            file.close()
            self.filePath = os.path.join(self.filePath, self.fileNameField.text()+ "."+ self.fileExtension)
            self.successful = True
        except FileExistsError:
            self.successful = False
