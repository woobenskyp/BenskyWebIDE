import os

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QDialogButtonBox


class CreateNewFolderDialog(QDialog):
    def __init__(self, filePath):
        super().__init__()
        self.setWindowTitle("Create Folder")
        self.setWindowIcon(QIcon('../icon/openproject.svg'))
        self.folderPath = filePath
        self.successful = False

        layout = QVBoxLayout()
        self.folderNameField = QLineEdit()
        self.folderNameField.setPlaceholderText("Folder Name")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(self.folderNameField)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def accept(self):
        super().accept()
        try:
            os.mkdir(os.path.join(self.folderPath, self.folderNameField.text()))
            self.successful = True
        except FileExistsError:
            self.successful = False