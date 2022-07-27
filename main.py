import os

from PySide6 import QtGui
from PySide6.QtWidgets import QApplication
from WelcomeWindow import WelcomeWindow
from PySide6.QtSvgWidgets import QSvgWidget

from ProjectWindow.ProjectWindow import ProjectWindow
from pathlib import Path

app = QApplication([])
QtGui.QFontDatabase.addApplicationFont('fonts/codeFont.ttf')

try:
    fileProject = open(os.path.join(str(Path.home()),Path('Bensky IDE Projects/.bensky/projectMemory.bensky').__str__()), 'r')
    projectPath = fileProject.read()[15:]
    fileProject.close()
    if not projectPath == "None" and Path(projectPath).exists():
        window = ProjectWindow(projectPath, WelcomeWindow())
        window.show()
    else:
        welcomeWindow = WelcomeWindow()
        welcomeWindow.show()
except FileNotFoundError:
    welcomeWindow = WelcomeWindow()
    welcomeWindow.show()

app.exec()