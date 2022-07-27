from PySide6.QtCore import Signal
from PySide6.QtGui import Qt, QPixmap
from PySide6.QtWidgets import QTabWidget, QScrollArea, QMessageBox

from ProjectWindow.FileTab import FileTab
from ProjectWindow.CodeEditor.ImageViewer import ImageViewer
from pathlib import Path

class TabWidget(QTabWidget):
    tabCountChanged = Signal()
    sourceCodeChanged = Signal()

    def __init__(self, parent):
        super().__init__()
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.closeTab)
        self.setMovable(True)
        self.parent = parent


    def closeTab(self, index):
        self.removeTab(index)
        self.tabCountChanged.emit()

    def openFile(self, filePath):
        filePath = Path(filePath).__str__()
        if not self.openedFile(filePath):
            if FileTab.isSupported(filePath):
                if QPixmap(filePath).height():
                    fileTab = ImageViewer(filePath, self)
                    self.parent.screenResized.connect(fileTab.updateImageSize)
                else:
                    fileTab = FileTab(filePath)
                    fileTab.codeEditField.textChanged.connect(lambda: self.sourceCodeChanged.emit())
                    self.parent.screenResized.connect(fileTab.lineCount.updateLineCount)

                self.addTab(fileTab, filePath.split("\\")[-1])
                self.tabCountChanged.emit()
                self.setCurrentIndex(self.count()-1)
            else:
                QMessageBox.warning(self.parent, "Error opening file",
                                    "Unable to open file. This file isn't supported")
        else:
            self.setCurrentIndex(self.fileIndex(filePath))

    def fileIndex(self, filePath):
        for i in range(self.count()):
            if self.widget(i).file == filePath:
                return i
        return 0

    def openedFile(self, filePath):
        for i in range(self.count()):
            if (self.widget(i).file == filePath):
                return True
        return False

    def refactorFiles(self, oldPath, newPath):
        for i in range(self.count()):
            self.widget(i).file = Path(self.widget(i).file).__str__().replace(oldPath, newPath)
            self.setTabText(i, self.widget(i).file.split("\\")[-1])
