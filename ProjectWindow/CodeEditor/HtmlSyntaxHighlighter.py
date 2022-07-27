from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor


class HtmlSyntaxHighlighter(QSyntaxHighlighter):
    inComment = 1
    withinCssStyle = 2

    def __init__(self, parent):
        super().__init__(parent)

    def highlightBlock(self, text):
        self.runHighlight(QRegularExpression("<([^<>]*)>?").globalMatch(text), QColor(24, 83, 228), 1) #parameters
        self.runHighlight(QRegularExpression("((?<![\\\\])['\"])((?:.(?!(?<![\\\\])\g1))*.?)\g1?").globalMatch(text), Qt.darkGreen) #values
        self.runHighlight(QRegularExpression("<([/!]?\w*)").globalMatch(text),QColor(2, 53, 180), 1) #tags

        self.setCurrentBlockState(-1)
        self.highlightComment(text)
        self.highlightCss(text)

    def highlightCss(self, text):
        cssStartPattern = QRegularExpression("<style>")
        cssEndPattern = QRegularExpression("</style>")

        cssStartPos = 0

        if not self.previousBlockState() == self.withinCssStyle:
            try:
                cssStartPos = text.index(cssStartPattern.pattern())
            except ValueError:
                cssStartPos = -1

        while cssStartPos >= 0:
            match = cssEndPattern.match(text, cssStartPos)
            cssEndPos = match.capturedStart()
            if cssEndPos == -1:
                self.setCurrentBlockState(self.withinCssStyle)
                lastCssLineLength = len(text) - cssStartPos
            else:
                lastCssLineLength = cssEndPos - cssStartPos \
                                        + match.capturedLength()
            self.runHighlight(QRegularExpression("([\w-]+\s*):[^;{]*[;}]").globalMatch(text[cssStartPos:cssStartPos+lastCssLineLength]), QColor(211, 2, 58),1)  # properties
            self.runHighlight(QRegularExpression(":([^;{]*)[;}]").globalMatch(text[cssStartPos:cssStartPos+lastCssLineLength]), Qt.darkYellow, 1)  # values
            self.runHighlight(QRegularExpression("[{},\.;\+:%\(\)\[\]/\*]").globalMatch(text[cssStartPos:cssStartPos+lastCssLineLength]), Qt.black)  # punctiations
            self.runHighlight(QRegularExpression("((?<![\\\\])['\"])((?:.(?!(?<![\\\\])\g1))*.?)\g1?").globalMatch(text[cssStartPos:cssStartPos+lastCssLineLength]),Qt.darkGreen)  # quotes
            try:
                cssStartPos = text.index(cssStartPattern.pattern(), cssStartPos + lastCssLineLength)
            except ValueError:
                cssStartPos = -1

    def highlightComment(self, text):
        commentStartPattern = QRegularExpression("<!--")
        commentEndPattern = QRegularExpression("-->")

        commentStartPos = 0

        if not self.previousBlockState() == self.inComment:
            try:
                commentStartPos = text.index(commentStartPattern.pattern())
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
                commentStartPos = text.index(commentStartPattern.pattern(), commentStartPos+lastCommentLineLength)
            except ValueError:
                commentStartPos = -1

    def runCommentHighlight(self, commentStartPos, length):
        myClassFormat = QTextCharFormat()
        myClassFormat.setForeground(Qt.darkGray)
        self.setFormat(commentStartPos, length, myClassFormat)

    def runHighlight(self, matches, color, group=0, position=None):
        myClassFormat = QTextCharFormat()
        myClassFormat.setForeground(color)
        while matches.hasNext():
            match = matches.next()
            if position:
                self.setFormat(position[0], position[1], myClassFormat)
            else:
                self.setFormat(match.capturedStart(group), match.capturedLength(group), myClassFormat)