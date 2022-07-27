from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon, Qt, QMouseEvent, QAction
from PySide6.QtWidgets import  QTreeView, QDialog, QMenu, QMessageBox

from ProjectWindow.CodeEditor.RenameElementDialog import RenameElementDialog
from ProjectWindow.CreateNewFileDialog import CreateNewFileDialog
from ProjectWindow.CreateNewFolderDialog import CreateNewFolderDialog
from pathlib import Path



class FileTree(QTreeView):
    doubleClick = Signal(str)
    fileDeleted = Signal(str)
    elementRenamed = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onContextMenu)

    def mouseDoubleClickEvent(self, event:QMouseEvent):
        if self.selectedIndexes():
            selectedIndex = self.selectedIndexes()[0]
        else:
            return 
        if self.model().sourceModel().isDir(self.model().mapToSource(selectedIndex)):
            if self.isExpanded(selectedIndex):
                self.collapse(selectedIndex)
            else:
                self.expand(selectedIndex)
        else:
            self.doubleClick.emit(Path(self.model().sourceModel().filePath(self.model().mapToSource(selectedIndex))).__str__())

    def onContextMenu(self, pos):
        selectedIndex = self.selectedIndexes()[0]

        if self.model().sourceModel().isDir(self.model().mapToSource(selectedIndex)):
            context = QMenu(self)

            createHtmlFileAction = QAction(QIcon("icon/newproject.svg"), "Create HTML File", self)
            createHtmlFileAction.triggered.connect(lambda: self.createFile('html'))

            createCssFileAction = QAction(QIcon("icon/newproject.svg"), "Create CSS File", self)
            createCssFileAction.triggered.connect(lambda: self.createFile('css'))

            createFolderAction = QAction(QIcon("icon/openproject.svg"), "Create Folder", self)
            createFolderAction.triggered.connect(self.createFolder)

            context.addAction(createHtmlFileAction)
            context.addAction(createCssFileAction)
            context.addAction(createFolderAction)

            if not self.model().sourceModel().filePath(self.model().mapToSource(selectedIndex)) == self.model().sourceModel().rootPath():
                deleteElementAction = QAction("Delete Folder", self)
                deleteElementAction.triggered.connect(self.deleteElement)

                rename = QAction("Rename", self)
                rename.triggered.connect(self.renameElement)

                context.addAction(rename)
                context.addAction(deleteElementAction)
            context.exec(self.mapToGlobal(pos))

        elif not self.model().sourceModel().filePath(self.model().mapToSource(selectedIndex)) == self.model().sourceModel().rootPath():
            context = QMenu(self)

            deleteElementAction = QAction("Delete File", self)
            deleteElementAction.triggered.connect(self.deleteElement)

            rename = QAction("Rename", self)
            rename.triggered.connect(self.renameElement)

            context.addAction(deleteElementAction)
            context.addAction(rename)
            context.exec(self.mapToGlobal(pos))

    def createFile(self, extension):
        selectedIndex = self.selectedIndexes()[0]
        dialog = CreateNewFileDialog(self.model().sourceModel().filePath(self.model().mapToSource(selectedIndex)), extension)
        result = dialog.exec()
        if not dialog.successful and result == QDialog.Accepted:
            QMessageBox.warning(self, "Create File", "File already exist")
        else:
            self.doubleClick.emit(dialog.filePath)


    def createFolder(self):
        selectedIndex = self.selectedIndexes()[0]
        dialog = CreateNewFolderDialog(self.model().sourceModel().filePath(self.model().mapToSource(selectedIndex)))
        result = dialog.exec()
        if not dialog.successful and result == QDialog.Accepted:
            QMessageBox.warning(self, "Create Folder", "Folder already exist")

    def deleteElement(self):
        selectedIndex = self.selectedIndexes()[0]
        if self.model().sourceModel().isDir(self.model().mapToSource(selectedIndex)):
            elementType = "Folder"
        else:
            elementType = "File"

        if QMessageBox.question(self, "Exit Bensky IDE", "Are you sure you want to delete this {}?".format(elementType)) == QMessageBox.Yes:
            self.model().sourceModel().remove(self.model().mapToSource(selectedIndex))
            self.fileDeleted.emit(self.model().sourceModel().filePath(self.model().mapToSource(selectedIndex)))

    def renameElement(self):
        selectedIndex = self.selectedIndexes()[0]
        if self.model().sourceModel().isDir(self.model().mapToSource(selectedIndex)):
            elementType = "Folder"
        else:
            elementType = "File"

        elementPath = self.model().sourceModel().filePath(self.model().mapToSource(selectedIndex))
        elementName = self.model().sourceModel().data(self.model().mapToSource(selectedIndex), Qt.DisplayRole)
        renameDialog = RenameElementDialog(elementPath, elementName, elementType)
        renameDialog.exec()
        self.elementRenamed.emit(Path(elementPath).__str__(), renameDialog.elementPath)



