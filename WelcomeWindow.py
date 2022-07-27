import os
from pathlib import Path
from CreateNewProjectDialog import CreateProjectDialog
from ProjectWindow.ProjectWindow import ProjectWindow

from PySide6.QtGui import QIcon, QFont, Qt, QPixmap
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QHBoxLayout


class WelcomeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bensky Web IDE")
        self.setWindowIcon(QIcon("icon/benskylogo.svg"))

        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        self.setupUi()


    def setupUi(self):
        self.setStyleSheet("QPushButton{ padding: 12px 128px; margin-left: 8px; margin-right: 8px;}")

        logo = QSvgWidget()
        logo.load("icon/benskylogo.svg")
        logo.setFixedSize(156, 156)

        logoLayout = QHBoxLayout()
        logoLayout.addStretch()
        logoLayout.addWidget(logo)
        logoLayout.addStretch()

        appName = QLabel("Bensky Web IDE")
        appNameFont = QFont()
        appNameFont.setPointSize(24)
        appName.setFont(appNameFont)
        appName.setAlignment(Qt.AlignCenter)

        appVersion = QLabel("Version 1.0.0")
        appVersion.setStyleSheet("color: grey; margin-bottom: 24px")
        appVersion.setAlignment(Qt.AlignCenter)

        appInfoLayout = QVBoxLayout()
        appInfoLayout.setAlignment(Qt.AlignCenter)
        appInfoLayout.addLayout(logoLayout)
        appInfoLayout.addWidget(appName)
        appInfoLayout.addWidget(appVersion)

        createProjectButton = QPushButton("Create New Project")
        createProjectButton.setIcon(QPixmap("icon/newproject.svg"))
        createProjectButton.clicked.connect(self.createNewProject)

        openProjectButton = QPushButton("Open Project")
        openProjectButton.setIcon(QPixmap("icon/openproject.svg"))
        openProjectButton.setStyleSheet("margin-bottom: 12px")
        openProjectButton.clicked.connect(self.openProject)

        self.mainLayout.addLayout(appInfoLayout)
        self.mainLayout.addWidget(createProjectButton)
        self.mainLayout.addWidget(openProjectButton)
        self.mainLayout.setAlignment(Qt.AlignHCenter)

    def createNewProject(self):
        self.createBenskyProjectFolder()
        dialog = CreateProjectDialog()
        if dialog.exec():
            self.project = ProjectWindow(dialog.projectPath, self)
            self.project.show()
            self.hide()

    def createBenskyProjectFolder(self):
        try:
            os.mkdir(os.path.join(str(Path.home()), "Bensky IDE Projects"))
        except:
            return

    def openProject(self):
        projectPath = QFileDialog.getExistingDirectory(self, "Open Project", os.path.join(str(Path.home()), "Bensky IDE Projects"))
        self.project = ProjectWindow(projectPath, self)
        self.project.show()
        self.hide()