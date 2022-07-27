import re

from PySide6.QtCore import QPoint, QRect, Qt, QEvent
from PySide6.QtGui import QKeyEvent, QAction, QIcon, QCursor
from PySide6.QtWidgets import QPlainTextEdit, QMenu, QCompleter
from ProjectWindow.CodeEditor.htmlElements import elements
from ProjectWindow.CodeEditor.HtmlSyntaxHighlighter import HtmlSyntaxHighlighter


class HtmlCodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.setTabStopDistance(30)
        self.shiftHeld = False
        self.suggestionList = SuggestionList(elements, self)
        self.suggestionList.setWidget(self)
        self.suggestionList.setCompletionMode(QCompleter.PopupCompletion)
        self.highlighter = HtmlSyntaxHighlighter(self.document())

    def keyPressEvent(self, e:QKeyEvent):
        if self.suggestionList.popup().isVisible():
            self.suggestionList.keyPressEvent(e)
            if e.key() == 16777220: #enter key
                return
        self.currentBlock = self.textCursor().block()
        self.currentBlockText = self.currentBlock.text()
        super().keyPressEvent(e)
        if e.text() == '>':
            self.insertClosingTag()
        elif e.text() == '<':
            cr = self.cursorRect()
            self.suggestionList.setCursorRect(cr)
            self.suggestionList.popup().setVisible(True)
        elif e.key()==16777220: #enterkey
            if self.suggestionList.popup().isVisible():
                return
            if self.shiftHeld:
                self.jumpToNewLine()
            else:
                self.insertIndentation()
        elif e.key()==16777219: #backspacekey
            if not self.textCursor().selectedText():
                self.doIndentationAwareBackspace()
        elif e.key() == 16777248:
            self.shiftHeld = True

    def keyReleaseEvent(self, e:QKeyEvent):
        if e.key() == 16777248:
            self.shiftHeld = False

    def jumpToNewLine(self):
        self.textCursor().deletePreviousChar()
        cursor = self.textCursor()
        blockEndPos = cursor.block().position() + len(cursor.block().text())
        cursor.setPosition(blockEndPos)
        self.setTextCursor(cursor)
        self.insertPlainText(" ")
        self.textCursor().insertBlock()
        self.insertIndentation()

    def doIndentationAwareBackspace(self):
        indentations = re.search("^\\t+", self.currentBlockText)
        if indentations:
            if self.textCursor().block().position() == self.textCursor().position()-len(indentations.group())+1:
                for i in range(len(indentations.group())):
                    self.textCursor().deletePreviousChar()

    def insertIndentation(self):
        text = self.toPlainText()
        pos = self.textCursor().position()
        pos -= 1
        indentation = self.currentBlockIndentation()
        if text[pos - 1] == '>':
            tagText = ""
            foundOpenBracket = False
            steps = 0
            while foundOpenBracket == False and pos >= 0:
                pos -= 1
                steps += 1
                currentChar = text[pos]
                if currentChar == '<':
                    foundOpenBracket = True
                    tagText = "<" + tagText
                elif currentChar == " ":
                    tagText = ">"
                else:
                    tagText = currentChar + tagText
            if not tagText in ["<>", "<area>", "<base>", "<br>", "<col>", "<embed>", "<hr>", "<img>", "<input>",
                               "keygen>", "<link>", "<meta>", "<param>", "<source>", "<track>", "<wbr>"] \
                    and not "</" in tagText and text[pos+steps+1] == "<":
                self.textCursor().insertText('\t'*(indentation+1))
                if text[pos+steps+1 : pos+steps + len(tagText)+2] == '</' + tagText[1:]:
                    self.textCursor().insertText('\n'+'\t'*indentation)
                    cursor = self.textCursor()
                    cursor.setPosition(pos + steps + 2 + indentation)
                    self.setTextCursor(cursor)
            elif "</" in tagText or tagText in ["<>", "<area>", "<base>", "<br>", "<col>", "<embed>", "<hr>", "<img>", "<input>",
                               "keygen>", "<link>", "<meta>", "<param>", "<source>", "<track>", "<wbr>"] or tagText.startswith("<!--"):
                self.textCursor().insertText("\t" * indentation)
            else:
                nextNonSpacePos = self.nextNonSpaceCharacterPos(text, pos+steps+1)
                if text[nextNonSpacePos] == '<':
                    cursor = self.textCursor()
                    cursor.setPosition(nextNonSpacePos)
                    if nextNonSpacePos - (pos+steps+1)>1:
                        for i in range(nextNonSpacePos - (pos+steps+1)):
                            cursor.deletePreviousChar()
                    else:
                        self.textCursor().insertText('\t' * (indentation+1))
                    self.textCursor().insertText("\t" * indentation)
                else:
                    self.textCursor().insertText('\t' * (indentation+1))

        else:
            nextNonSpacePos = self.nextNonSpaceCharacterPos(text, pos)
            if not text[pos - 1] == ">" and not text[nextNonSpacePos] == '<':
                foundCloseBracket = False
                steps = 0
                while foundCloseBracket == False and pos >= 0:
                    pos -= 1
                    steps += 1
                    currentChar = text[pos]
                    if currentChar == ">":
                        foundCloseBracket = True
                        foundOpenBracket = False
                        tagText = ""
                        while foundOpenBracket == False and pos >= 0:
                            currentChar = text[pos]
                            if currentChar == '<':
                                foundOpenBracket = True
                                tagText = "<" + tagText
                            elif currentChar == " ":
                                tagText = ">"
                            else:
                                tagText = currentChar + tagText
                            pos -= 1
                            steps += 1
                        if not tagText in ["<>", "<area>", "<base>", "<br>", "<col>", "<embed>", "<hr>", "<img>", "<input>",
                               "keygen>", "<link>", "<meta>", "<param>", "<source>", "<track>", "<wbr>"] and not "</" in tagText and not tagText.startswith("<!--"):
                            cursor = self.textCursor()
                            cursor.setPosition(pos)
                            self.currentBlock = cursor.block()
                            indentation = self.currentBlockIndentation()
                            self.textCursor().insertText("\t" * (indentation+1))
                        else:
                            self.textCursor().insertText("\t" * indentation)

            else:
                cursor = self.textCursor()
                cursor.setPosition(nextNonSpacePos)
                for i in range(nextNonSpacePos - pos - 1):
                    cursor.deletePreviousChar()
                self.textCursor().insertText("\t"* indentation)


    def nextNonSpaceCharacterPos(self, text, pos):
        lineCount = 0
        while pos < len(text):
            if text[pos] == '\n':
                lineCount += 1
                if lineCount > 1:
                    break
            if not text[pos] in " \t\n":
                break
            pos += 1
        return pos

    def deleteWhiteSpaceBeforeClosingBracket(self):
        pass

    def currentBlockIndentation(self):
        text = self.currentBlock.text()
        tabs = re.search("^\\t*", text)
        return len(tabs.group())

    def insertClosingTag(self):
        text = self.toPlainText()
        pos = self.textCursor().position()
        foundOpenBracket = False
        tagText = ""
        steps = 0
        if text[pos:pos + 2] == "</":
            return
        while foundOpenBracket == False and pos >= 0:
            pos -= 1
            steps += 1
            currentChar = text[pos]
            if currentChar == '<':
                foundOpenBracket = True
                tagText = "</" + tagText
            elif currentChar == " ":
                tagText = ">"
            else:
                tagText = currentChar + tagText
        if not tagText in ["</>", "</area>", "</base>", "</br>", "</col>", "</embed>", "</hr>", "</img>", "</input>",
                           "/keygen>", "</link>", "</meta>", "</param>", "</source>", "</track>", "</wbr>"] \
                and not "<//" in tagText and not tagText.startswith("</!--"):
            self.textCursor().insertText(tagText)
        cursor = self.textCursor()
        cursor.setPosition(pos + steps)
        self.setTextCursor(cursor)


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
        print(e.text())
        if e.text():
            if e.text().lower() in "abcdefghigklmnopqrstuvwxyz123456":
                self.tag += e.text()
                self.suggest()
                print(self.tag)
            elif e.key() == 16777220:
                if self.currentIndex():
                    self.parent().insertPlainText(self.popup().selectedIndexes()[0].data(Qt.DisplayRole)[len(self.tag):])
                    print(self.currentIndex().data(Qt.DisplayRole))
                    self.tag = ""
                    self.popup().setVisible(False)
            elif e.key() == 16777219: #backspace
                self.tag = self.tag[:-1]
                if not self.tag:
                    self.suggest()
            elif e.text() in " !":
                self.popup().setVisible(False)



