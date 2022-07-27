import os
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QDialogButtonBox, QHBoxLayout, QFormLayout, \
    QFileDialog, QMessageBox


class CreateProjectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create New Project")
        self.setMinimumWidth(400)
        self.setWindowIcon(QIcon("icon/benskylogo.svg"))

        self.layout = QVBoxLayout()
        self.projectNameField = QLineEdit("Untitled")
        self.projectPathField = QLineEdit(os.path.join(str(Path.home()), "Bensky IDE Projects"))

        self.setLayout(self.layout)
        self.setupUi()

    def setupUi(self):
        createButton = QPushButton("Create")
        buttonBox = QDialogButtonBox(QDialogButtonBox.Cancel)
        buttonBox.addButton(createButton, QDialogButtonBox.AcceptRole)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        pathfinder = QPushButton()
        pathfinder.setIcon(QIcon('icon/openproject.svg'))
        pathfinder.clicked.connect(self.findPath)
        projectPathLayout = QHBoxLayout()
        projectPathLayout.addWidget(self.projectPathField)
        projectPathLayout.addWidget(pathfinder)

        formLayout = QFormLayout()
        formLayout.addRow("Project Name", self.projectNameField)
        formLayout.addRow("Project Path", projectPathLayout)

        self.layout.addLayout(formLayout)
        self.layout.addWidget(buttonBox)


    def findPath(self):
        path = QFileDialog.getExistingDirectory(self, "Project Path", self.projectPathField.text())
        self.projectPathField.setText(path)

    def accept(self):
        self.projectPath = os.path.join(self.projectPathField.text(), self.projectNameField.text())
        try:
            os.mkdir(self.projectPath)
            open(os.path.join(self.projectPath, "index.html"), "x").write("<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n\t<meta charset=\"UTF-8\">\n\t<title>Title</title>\n</head>\n<body>\n</body>\n</html>")
            super().accept()
        except FileNotFoundError:
            QMessageBox.warning(self, "Path error", "The system cannot find the path specified\nMake sure the path you write exists")
        except FileExistsError:
            QMessageBox.warning(self, "Path error", "Project Name already exists.\nTry changing the name")
