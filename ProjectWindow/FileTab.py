from PySide6.QtCore import QSize
from PySide6.QtGui import Qt, QFont, QPaintEvent, QTextBlock, QImageReader, QPixmap
from PySide6.QtWidgets import QLabel, QWidget, QHBoxLayout, QPlainTextEdit, QScrollArea, QMessageBox

from ProjectWindow.CodeEditor.CssCodeEditor import CssCodeEditor
from ProjectWindow.CodeEditor.HtmlCodeEditor import HtmlCodeEditor
from pathlib import Path


class FileTab(QWidget):
    def __init__(self, file):
        super().__init__()
        self.file = Path(file).__str__()

        self.layout = QHBoxLayout()

        self.codeEditField = self.getCodeEditor()
        self.lineCount = LineCount('1', self.codeEditField)
        scrollArea = QScrollArea()
        self.lineCount.setScrollArea(scrollArea)
        scrollArea.setWidget(self.lineCount)
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet('border: 0px;')
        scrollArea.verticalScrollBar().setEnabled(False)
        scrollArea.horizontalScrollBar().setEnabled(False)
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.layout.addWidget(scrollArea)
        self.layout.addWidget(self.codeEditField)

        self.setLayout(self.layout)
        self.setupUI()

    def getCodeEditor(self):
        extension = self.file.split(".")[-1]
        if extension in ["html", "htm"]:
            return HtmlCodeEditor()
        elif extension == "css":
            return CssCodeEditor()
        else:
            return QPlainTextEdit()

    def setupUI(self):
        font = QFont("JetBrains Mono NL", 10)

        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.codeEditField.setFont(font)
        self.codeEditField.updateRequest.connect(self.lineCount.updateLineCount)
        self.lineCount.setFont(self.codeEditField.font())
        self.codeEditField.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.codeEditField.textChanged.connect(self.lineCount.updateLineCount)
        self.codeEditField.textChanged.connect(self.saveFile)
        self.codeEditField.insertPlainText(self.readFile())

    def saveFile(self):
        file = open(self.file, 'w')
        file.write(self.codeEditField.toPlainText())

    def readFile(self):
        file = open(self.file, "r")
        content = file.read()
        file.close()
        return content

    @staticmethod
    def isSupported(filePath):
        try:
            open(filePath, 'r').read()
            return True
        except:
            if QPixmap(filePath).height():
                return True
            return False


class LineCount(QLabel):
    def __init__(self, text, editor:QPlainTextEdit):
        super().__init__(text)
        self.codeEditField = editor

        self.setStyleSheet("padding-top: 5px; padding-left: 16px; padding-right: 8px; background: #d1d1d1v; color: #b6b6b6")
        self.setAlignment(Qt.AlignRight)
        self.blockHeight = self.codeEditField.blockBoundingGeometry(self.codeEditField.firstVisibleBlock()).height()

    def updateLineCount(self):
        lineCount = ""
        firstVisibleNumber = self.codeEditField.firstVisibleBlock().blockNumber()
        blockVisible = self.codeEditField.height()/self.blockHeight
        for i in range(self.codeEditField.blockCount()):
            if firstVisibleNumber+i+1 == self.codeEditField.blockCount():
                break
            lineCount += str(firstVisibleNumber+i+1)
            lineCount += '\n'
        self.setText(lineCount)
        text = str(self.codeEditField.blockCount())
        self.scrollArea.setMaximumWidth(16+8+8+self.fontMetrics().boundingRect(text).width())

    def setScrollArea(self, scrollArea):
        self.scrollArea = scrollArea

