import re

from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QPlainTextEdit, QCompleter
from ProjectWindow.CodeEditor.CssSyntaxHighlighter import CssSyntaxHighlighter
from PySide6.QtCore import QPoint, QRect, Qt, QEvent
from ProjectWindow.CodeEditor.cssProperties import properties



class CssCodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setTabStopDistance(20)
        self.setStyleSheet("color: rgb(2, 53, 180)")
        self.highlighter = CssSyntaxHighlighter(self.document())
        self.suggestionList = SuggestionList(properties, self)
        self.suggestionList.setWidget(self)
        self.suggestionList.setCompletionMode(QCompleter.PopupCompletion)
        self.shiftHeld = False


    def keyPressEvent(self, e:QKeyEvent):
        if self.suggestionList.popup().isVisible():
            self.suggestionList.keyPressEvent(e)
            if e.key() == 16777220:  # enter key
                return
        if e.text() == "{":
            super().keyPressEvent(e)
            self.insertClosingBracket()
        elif e.key() == 16777220: #enterkey
            if self.shiftHeld:
                self.jumpToNewLine()
            else:
                self.executeEnterKey()
        elif e.text().lower() in "abcdefghijklmnopqrstuvwxyz-" and self.toPlainText()[self.previousBracketPos()] == "{" and self.toPlainText()[self.textCursor().position()-1] == "\t":
            super().keyPressEvent(e)
            cr = self.cursorRect()
            self.suggestionList.setCursorRect(cr)
            self.suggestionList.popup().setVisible(True)
            self.suggestionList.tag = e.text()
            self.suggestionList.suggest()
        elif e.key() == 16777248:
            self.shiftHeld = True
        else:
            super().keyPressEvent(e)

    def keyReleaseEvent(self, e: QKeyEvent):
        if e.key() == 16777248:
            self.shiftHeld = False

    def jumpToNewLine(self):
        cursor = self.textCursor()
        blockEndPos = cursor.block().position() + len(cursor.block().text())
        cursor.setPosition(blockEndPos)
        self.setTextCursor(cursor)
        self.insertPlainText("\n" + "\t" * self.currentBlockIndentation())

    def insertClosingBracket(self):
        self.insertPlainText('}')
        self.moveCursorPos(-1)


    def moveCursorPos(self, steps):
        cursor = self.textCursor()
        cursor.setPosition(cursor.position() + steps)
        self.setTextCursor(cursor)

    def executeEnterKey(self):
        text = self.toPlainText()
        if text[self.prevNonSpacePosInLine()] == '{' and text[self.nextNonSpacePosInLine()]=="}":
            self.insertPlainText("\n" + "\t"*(self.currentBlockIndentation()+1) + "\n" + "\t"*self.currentBlockIndentation())
            self.moveCursorPos(-(len("\n"+"\t"*self.currentBlockIndentation())))
        else:
            self.insertPlainText("\n"+ "\t"*self.currentBlockIndentation())

    def prevNonSpacePosInLine(self):
        nonSpacePos = -1
        pos = self.textCursor().position()-1
        while nonSpacePos == -1 and pos>0:
            if not self.toPlainText()[pos] == " ":
                nonSpacePos = pos
            else:
                pos -= 1
        return nonSpacePos

    def nextNonSpacePosInLine(self):
        nonSpacePos = -1
        pos = self.textCursor().position()
        while nonSpacePos == -1 and pos < len(self.toPlainText()):
            if not self.toPlainText()[pos] == " ":
                nonSpacePos = pos
            else:
                pos += 1
        return pos

    def previousBracketPos(self):
        bracketPos = -1
        pos = self.textCursor().position()
        while bracketPos == -1 and pos > 0:
            if self.toPlainText()[pos] in "{}":
                bracketPos = pos
            else:
                pos -= 1
        return bracketPos

    def nextBracketPos(self):
        bracketPos = -1
        pos = self.textCursor().position()
        while bracketPos == -1 and pos < len(self.toPlainText()):
            if self.toPlainText()[pos] in "{}":
                bracketPos = pos
            else:
                pos += 1
        return bracketPos

    def currentBlockIndentation(self):
        text = self.textCursor().block().text()
        tabs = re.search("^\\t*", text)
        return len(tabs.group())


class SuggestionList(QCompleter):
    def __init__(self, suggestions, parent):
        super().__init__(suggestions, parent)
        self.tag = ""

    def setCursorRect(self, cursorRect):
        self.cursorRect = cursorRect
        self.suggest()

    def suggest(self):
        self.setCompletionPrefix(self.tag)
        cr = self.cursorRect
        cr.setWidth(150)
        self.complete(cr)
        if not self.completionCount():
            self.tag = ""
        else:
            self.popup().setCurrentIndex(self.currentIndex())


    def keyPressEvent(self, e:QKeyEvent):
        if e.text():
            if e.text().lower() in "abcdefghigklmnopqrstuvwxyz-":
                self.tag += e.text()
                self.suggest()
            elif e.key() == 16777220:
                if self.currentIndex():
                    self.parent().insertPlainText(self.popup().selectedIndexes()[0].data(Qt.DisplayRole)[len(self.tag):]+ ": ;")
                    self.parent().moveCursorPos(-1)
                    self.tag = ""
                    self.popup().setVisible(False)
            elif e.key() == 16777219: #backspace
                self.tag = self.tag[:-1]
                if not self.tag:
                    self.popup().setVisible(False)
            elif e.text() in " !":
                self.popup().setVisible(False)



