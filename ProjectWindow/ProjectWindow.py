import os
from pathlib import Path

from PySide6.QtWebEngineWidgets import QWebEngineView

from AboutPage import AboutPage
from CreateNewProjectDialog import CreateProjectDialog
from ProjectWindow.FileTree import FileTree
from ProjectWindow.TabWidget import TabWidget

from PySide6.QtCore import QDir, QSize, Signal, QSortFilterProxyModel, QPersistentModelIndex
from PySide6.QtGui import QIcon, Qt, QAction, QCloseEvent, QResizeEvent
from PySide6.QtWidgets import QMainWindow, QSplitter, QFileSystemModel, QLabel, QDockWidget, QToolBar, QFileDialog, \
    QMessageBox


class ProjectWindow(QMainWindow):
    screenResized = Signal()

    def __init__(self, projectPath, welcomePage):
        super().__init__()
        self.welcomePage = welcomePage
        self.projectPath = projectPath
        self.projectName = self.projectPath.replace('\\', '/').split("/")[-1]
        self.setWindowTitle("Bensky Web IDE - " + self.projectName)
        self.setWindowIcon(QIcon('icon/benskylogo.svg'))
        self.setGeometry(50, 50, 800, 500)
        #self.setWindowState(Qt.WindowMaximized)

        self.toolBar = QToolBar("Preview Panel")
        self.toolBar.setIconSize(QSize(20, 20))
        self.toolBar.setMovable(False)

        self.previewPanelAction = QAction(QIcon('icon/previewPanelIcon.svg'), "Preview Panel", self)
        self.previewPanelAction.triggered.connect(self.previewPanelActionClicked)
        self.toolBar.addAction(self.previewPanelAction)

        self.addToolBar(Qt.RightToolBarArea, self.toolBar)

        self.mainSplitter = QSplitter()
        self.projectFiles = FileTree()
        self.tabWidget = TabWidget(self)
        self.previewPanel = PreviewPanel(self)
        self.previewPanel.setWindowTitle("Preview Panel")
        self.webEngineView = QWebEngineView()
        self.previewPanel.setWidget(self.webEngineView)
        self.previewPanel.setFeatures(QDockWidget.DockWidgetClosable)
        self.previewPanel.visibilityChanged.connect(lambda: self.toolBar.setVisible(True))

        self.tabWidget.currentChanged.connect(lambda index: self.previewPanel.changeCodeSource(self.tabWidget.widget(index)))
        self.tabWidget.sourceCodeChanged.connect(self.previewPanel.updateCode)

        self.noFileIsOpen = QLabel("You haven't opened any files")

        self.setupUi()
        self.setCentralWidget(self.mainSplitter)
        self.createDotBenskyProjectFolder()
        self.setProjectMemory()

    def setProjectMemory(self):
        file = open(os.path.join(str(Path.home()),Path('Bensky IDE Projects/.bensky/projectMemory.bensky').__str__()), 'w')
        file.write("currentProject:"+self.projectPath)
        file.close()

    def createDotBenskyProjectFolder(self):
        try:
            os.mkdir(os.path.join(str(Path.home()), Path("Bensky IDE Projects/.bensky").__str__()))
        except:
            return

    def setupUi(self):
        menu = self.menuBar()
        fileMenu = menu.addMenu("&File")

        newProjectAction = QAction(QIcon('icon/newproject.svg'), "Create New Project", self)
        newProjectAction.triggered.connect(self.createNewProject)
        fileMenu.addAction(newProjectAction)

        openProjectAction = QAction(QIcon('icon/openproject.svg'), "Open Project", self)
        openProjectAction.triggered.connect(self.openProject)
        fileMenu.addAction(openProjectAction)

        closeProjectAction = QAction(QIcon('icon/closeproject.svg'), "Close Project", self)
        closeProjectAction.triggered.connect(self.closeProject)
        fileMenu.addAction(closeProjectAction)

        fileMenu.addSeparator()

        exitAction = QAction("Exit", self)
        exitAction.triggered.connect(self.exitApp)
        fileMenu.addAction(exitAction)

        aboutAction = QAction("About", self)
        aboutAction.triggered.connect(self.showAboutPage)
        menu.addAction(aboutAction)

        fileSection = QDockWidget(self)
        fileSection.setWindowTitle('Project Files')
        fileSection.setFeatures(QDockWidget.NoDockWidgetFeatures)
        fileSection.setWidget(self.projectFiles)


        model = QFileSystemModel()
        model.setRootPath(QDir(self.projectPath).path())

        proxy = FileProxyModel(self.projectFiles)
        proxy.setSourceModel(model)
        proxy.setIndexPath(QPersistentModelIndex(model.index(self.projectPath)))

        self.projectFiles.setModel(proxy)

        self.projectFiles.setMinimumWidth(200)
        self.projectFiles.setRootIndex(proxy.mapFromSource(model.index(self.projectPath).parent()))
        self.projectFiles.hideColumn(1)
        self.projectFiles.hideColumn(2)
        self.projectFiles.hideColumn(3)
        self.projectFiles.setHeaderHidden(True)
        self.projectFiles.doubleClick.connect(self.tabWidget.openFile)
        self.projectFiles.expand(proxy.mapFromSource(model.index(model.rootPath())))
        self.projectFiles.fileDeleted.connect(lambda filePath: self.tabWidget.closeTab(self.tabWidget.fileIndex(filePath)))
        self.projectFiles.elementRenamed.connect(self.tabWidget.refactorFiles)
        self.tabWidget.tabCountChanged.connect(self.manageQSplitter)

        self.noFileIsOpen.setStyleSheet("background: #d1d1d1v; color: #b6b6b6")
        self.noFileIsOpen.setAlignment(Qt.AlignCenter)

        self.mainSplitter.addWidget(fileSection)
        self.mainSplitter.addWidget(self.noFileIsOpen)
        self.manageQSplitter()
        self.mainSplitter.setSizes([200, 1000])

    def createNewProject(self):
        self.createBenskyProjectFolder()
        dialog = CreateProjectDialog()
        if dialog.exec():
            self.project = ProjectWindow(dialog.projectPath, self.welcomePage)
            self.project.show()
            self.close()

    def createBenskyProjectFolder(self):
        try:
            os.mkdir(os.path.join(str(Path.home()), "Bensky IDE Projects"))
        except:
            return

    def openProject(self):
        projectPath = QFileDialog.getExistingDirectory(self, "Open Project", os.path.join(str(Path.home()), "Bensky IDE Projects"))
        self.project = ProjectWindow(projectPath, self.welcomePage)
        self.project.show()
        self.close()

    def closeProject(self):

        file = open(os.path.join(str(Path.home()),Path('Bensky IDE Projects/.bensky/projectMemory.bensky').__str__()), 'w')
        file.write("currentProject:None")
        file.close()
        print('closed')
        self.close()
        self.welcomePage.show()

    def exitApp(self):
        self.close()

    def closeEvent(self, event:QCloseEvent):
        if QMessageBox.question(self, "Exit Bensky Web IDE", "Are you sure you want to exit?") == QMessageBox.Yes:
            self.close()
        else:
            event.ignore()

    def showAboutPage(self):
        aboutPage = AboutPage()
        aboutPage.exec()

    def previewPanelActionClicked(self):
        self.previewPanel.setVisible(True)
        self.mainSplitter.addWidget(self.previewPanel)
        self.previewPanel.updateCode()
        self.toolBar.setVisible(False)
        self.manageQSplitter()


    def manageQSplitter(self):
        if self.tabWidget.count():
            self.mainSplitter.replaceWidget(1, self.tabWidget)
        else:
            self.mainSplitter.replaceWidget(1, self.noFileIsOpen)
        if self.mainSplitter.count()>2:
            self.mainSplitter.setSizes([200, 650, 350])
        else:
            self.mainSplitter.setSizes([200, 1000])

    def resizeEvent(self, e:QResizeEvent):
        super().resizeEvent(e)
        if not e.oldSize() == e.size():
            self.screenResized.emit()


class PreviewPanel(QDockWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.sourceCode = None
        self.dockLocationChanged.connect(self.fixPositionError)

    def fixPositionError(self, area):
        if area == QDockWidget.NoDockWidgetFeatures:
            geometry = self.geometry()
            self.setGeometry(geometry.x(), geometry.y()+300, geometry.width(), geometry.height())

    def closeEvent(self, event:QCloseEvent):
        self.setVisible(False)

    def changeCodeSource(self, fileTab):
        try:
            if fileTab.file.split('.')[-1] == "html":
                self.sourceCode = fileTab
                url = fileTab.file.replace(' ', '%20').replace("\\", "/")
                self.widget().setUrl(url)
        except AttributeError:
            pass


    def updateCode(self):
        if self.isVisible() and self.sourceCode:
            self.widget().reload()

class FileProxyModel(QSortFilterProxyModel, QFileSystemModel):
    def setIndexPath(self, index):
        self._index_path = index
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow, sourceParent):
        if hasattr(self, "_index_path"):
            ix = self.sourceModel().index(sourceRow, 0, sourceParent)
            if self._index_path.parent() == sourceParent and self._index_path != ix:
                return False
        return super(FileProxyModel, self).filterAcceptsRow(sourceRow, sourceParent)



