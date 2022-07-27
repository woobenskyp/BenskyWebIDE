import os
import re

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QPushButton, QMessageBox
from pathlib import Path

class RenameElementDialog(QDialog):
    def __init__(self, elementPath, elementName, elementType):
        super().__init__()

        self.elementPath = elementPath
        self.elementType = elementType
        self.elementName = elementName

        self.setWindowTitle("Rename")
        self.setWindowIcon(QIcon('icon/benskylogo.svg'))

        layout = QVBoxLayout()
        self.newNameField = QLineEdit()
        self.newNameField.setText(self.elementName)
        self.newNameField.setCursorPosition(self.cursorPosition())

        renameButton = QPushButton("Rename")
        buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttonBox.addButton(renameButton, QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        layout.addWidget(QLabel("Rename {} \"{}\" to:".format(self.elementType, self.elementName)))
        layout.addWidget(self.newNameField)
        layout.addWidget(buttonBox)

        self.setLayout(layout)

    def cursorPosition(self):

        regex = re.search('\.\w+$', self.elementName)
        if regex:
            return regex.start()
        else:
            return len(self.elementName)


    def accept(self):
        try:
            os.rename(self.elementPath, os.path.join(Path(self.elementPath).parent.__str__(),self.newNameField.text()))
            self.elementPath = os.path.join(Path(self.elementPath).parent.__str__(),self.newNameField.text())
            super().accept()
        except FileExistsError:
            QMessageBox.warning(self, "Path error", "File Name already exists.\nTry changing the name")
