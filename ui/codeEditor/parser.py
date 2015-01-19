""" using clang to highlight keywords """
from PyQt4.QtGui import  QColor, QBrush, QTextCursor, QTextCharFormat
from clang.cindex import TranslationUnit, TokenKind
import logging

"""
SOLARIZED HEX     16/8 TERMCOL  XTERM/HEX   L*A*B      RGB         HSB
--------- ------- ---- -------  ----------- ---------- ----------- -----------
base03    #002b36  8/4 brblack  234 #1c1c1c 15 -12 -12   0  43  54 193 100  21
base02    #073642  0/4 black    235 #262626 20 -12 -12   7  54  66 192  90  26
base01    #586e75 10/7 brgreen  240 #585858 45 -07 -07  88 110 117 194  25  46 Comment
base00    #657b83 11/7 bryellow 241 #626262 50 -07 -07 101 123 131 195  23  51
base0     #839496 12/6 brblue   244 #808080 60 -06 -03 131 148 150 186  13  59 Normal
base1     #93a1a1 14/4 brcyan   245 #8a8a8a 65 -05 -02 147 161 161 180   9  63
base2     #eee8d5  7/7 white    254 #e4e4e4 92 -00  10 238 232 213  44  11  93
base3     #fdf6e3 15/7 brwhite  230 #ffffd7 97  00  10 253 246 227  44  10  99
yellow    #b58900  3/3 yellow   136 #af8700 60  10  65 181 137   0  45 100  71  Type
orange    #cb4b16  9/3 brred    166 #d75f00 50  50  55 203  75  22  18  89  80
red       #dc322f  1/1 red      160 #d70000 50  65  45 220  50  47   1  79  86  Special
magenta   #d33682  5/5 magenta  125 #af005f 50  65 -05 211  54 130 331  74  83
violet    #6c71c4 13/5 brmagenta 61 #5f5faf 50  15 -45 108 113 196 237  45  77
blue      #268bd2  4/4 blue      33 #0087ff 55 -10 -45  38 139 210 205  82  82  Identifier
cyan      #2aa198  6/6 cyan      37 #00afaf 60 -35 -05  42 161 152 175  74  63  Constant
green     #859900  2/2 green     64 #5f8700 60 -20  65 133 153   0  68 100  60  Keyword """


class Theme(object):
    """ define colors for different tokens """
    keyword = QTextCharFormat()
    keyword.setForeground(QBrush(QColor("#5f8700")))
    literal = QTextCharFormat()
    literal.setForeground(QBrush(QColor("#2aa198")))
    comment = QTextCharFormat()
    comment.setForeground(QBrush(QColor("#586e75")))
    normal = QTextCharFormat()
    normal.setForeground(QBrush(QColor("#808080")))

    formats = {TokenKind.KEYWORD : keyword,
               TokenKind.LITERAL : literal,
               TokenKind.COMMENT: comment,
               TokenKind.PUNCTUATION: normal,
               TokenKind.IDENTIFIER : normal}

    @staticmethod
    def get_format(kind):
        """ returns the QTextCharFormat for corresponding token kind """
        return Theme.formats[kind]


class Highlighter(object):
    """ parsing the source file and applying formats """
    def __init__(self, text):
        self.text = text
        self.doc = text.document()

    def highlight(self, filename):
        """ highlight the source file  """
        try:
            cursor = TranslationUnit.from_source(filename).cursor
        except:
            logging.warn('Unable to parse ' + filename)
            return
        children = cursor.get_children()
        for child in children:
            loc = child.location
            if str(loc.file) != filename:
                continue
            tokens = cursor.get_tokens()
            for token in tokens:
                if token.kind == TokenKind.IDENTIFIER or token.kind == TokenKind.PUNCTUATION:
                    continue
                self._hltext(token.kind, token.extent.start.line - 1, token.extent.start.column - 1,
                             token.extent.end.line - 1, token.extent.end.column - 1)

    def _hltext(self, kind, line, col, line2, col2):
        """ applying format """
        # moving to start
        cursor = QTextCursor(self.doc.findBlockByLineNumber(line))
        if col == 0:
            cursor.movePosition(QTextCursor.StartOfBlock)
        else:
            cursor.movePosition(QTextCursor.Right, QTextCursor.MoveAnchor, col)
        # moving to end
        if line == line2:
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, col2 - col)
        else:
            cursor.movePosition(QTextCursor.NextBlock, QTextCursor.KeepAnchor, line2 - line)
            cursor.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, col2)
        cursor.mergeCharFormat(Theme.get_format(kind))
