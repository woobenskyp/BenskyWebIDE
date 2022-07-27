from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor


class CssSyntaxHighlighter(QSyntaxHighlighter):
    inComment = 1

    def __init__(self, parent):
        super().__init__(parent)
        self.insideBrackets = False

    def highlightBlock(self, text):
        self.runHighlight(QRegularExpression("([\w-]+\s*):[^;{]*[;}]").globalMatch(text), QColor(211, 2, 58), 1) #properties
        self.runHighlight(QRegularExpression(":([^;{]*)[;}]").globalMatch(text), Qt.darkYellow, 1) #values
        self.runHighlight(QRegularExpression("[{},\.;\+:%\(\)\[\]/\*]").globalMatch(text), Qt.black) #punctiations
        self.runHighlight(QRegularExpression("((?<![\\\\])['\"])((?:.(?!(?<![\\\\])\g1))*.?)\g1?").globalMatch(text), Qt.darkGreen) #quotes

        self.setCurrentBlockState(-1)
        self.highlightComment(text)

    def highlightComment(self, text):
        commentStartPattern = QRegularExpression("/\*")
        commentEndPattern = QRegularExpression("\*/")

        commentStartPos = 0

        if not self.previousBlockState() == self.inComment:
            try:
                commentStartPos = text.index("/*")
            except ValueError:
                commentStartPos = -1

        while commentStartPos >= 0:
            match = commentEndPattern.match(text, commentStartPos)
            commentEndPos = match.capturedStart()
            if commentEndPos == -1:
                self.setCurrentBlockState(self.inComment)
                lastCommentLineLength = len(text) - commentStartPos
            else:
                lastCommentLineLength = commentEndPos - commentStartPos \
                                        + match.capturedLength()

            self.runCommentHighlight(commentStartPos, lastCommentLineLength)
            try:
                commentStartPos = text.index("/*", commentStartPos + lastCommentLineLength)
            except ValueError:
                commentStartPos = -1

    def runCommentHighlight(self, commentStartPos, length):
        myClassFormat = QTextCharFormat()
        myClassFormat.setForeground(Qt.darkGray)
        self.setFormat(commentStartPos, length, myClassFormat)

    def runHighlight(self, matches, color, pos=0):
        myClassFormat = QTextCharFormat()
        myClassFormat.setForeground(color)
        while matches.hasNext():
            match = matches.next()
            self.setFormat(match.capturedStart(pos), match.capturedLength(pos), myClassFormat)

