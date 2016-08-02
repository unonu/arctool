#http://thecodeinn.blogspot.com/2013/07/fully-functional-pyqt-text-editor.html

import sys
import time
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal

class TextEditor(QtWidgets.QWidget):
 
    textChanged = pyqtSignal()

    def __init__(self):
        super(TextEditor,self).__init__()
        self.initUI()
 
    def initUI(self):
#------- Toolbar --------------------------------------
 
        cutAction = QtWidgets.QAction(QtGui.QIcon("icons/cut.png"),"Cut to clipboard",self)
        cutAction.setStatusTip("Delete and copy text to clipboard")
        cutAction.setShortcut("Ctrl+X")
        cutAction.triggered.connect(self.Cut)
 
        copyAction = QtWidgets.QAction(QtGui.QIcon("icons/copy.png"),"Copy to clipboard",self)
        copyAction.setStatusTip("Copy text to clipboard")
        copyAction.setShortcut("Ctrl+C")
        copyAction.triggered.connect(self.Copy)
 
        pasteAction = QtWidgets.QAction(QtGui.QIcon("icons/paste.png"),"Paste from clipboard",self)
        pasteAction.setStatusTip("Paste text from clipboard")
        pasteAction.setShortcut("Ctrl+V")
        pasteAction.triggered.connect(self.Paste)
 
        undoAction = QtWidgets.QAction(QtGui.QIcon("icons/undo.png"),"Undo last action",self)
        undoAction.setStatusTip("Undo last action")
        undoAction.setShortcut("Ctrl+Z")
        undoAction.triggered.connect(self.Undo)
 
        redoAction = QtWidgets.QAction(QtGui.QIcon("icons/redo.png"),"Redo last undone thing",self)
        redoAction.setStatusTip("Redo last undone thing")
        redoAction.setShortcut("Ctrl+Y")
        redoAction.triggered.connect(self.Redo)
 
        self.toolbar = QtWidgets.QToolBar("Actions",self)
        self.toolbar.addAction(cutAction)
        self.toolbar.addAction(copyAction)
        self.toolbar.addAction(pasteAction)
        self.toolbar.addAction(undoAction)
        self.toolbar.addAction(redoAction)
 
        self.fontFamily = QtWidgets.QFontComboBox(self)
        self.primed = False
        self.fontFamily.currentFontChanged.connect(self.FontFamily)
        # self.fontFamily.activated.connect(self.pt)
 
        self.fontSize = QtWidgets.QComboBox(self)
        self.fontSize.setEditable(True)
        self.fontSize.setMinimumContentsLength(3)
        self.fontSize.activated.connect(self.FontSize)
        flist = [6,7,8,9,10,11,12,13,14,15,16,18,20,22,24,26,28,32,36,40,44,48,
                 54,60,66,72,80,88,96]
         
        for i in flist:
            self.fontSize.addItem(str(i))
 
        self.fontColor = QtWidgets.QToolButton(self)
        self.fontColor.setStyleSheet("background : black")
        self.fontColor.clicked.connect(self.FontColor)
 
        boldAction = QtWidgets.QAction(QtGui.QIcon("icons/bold.png"),"Bold",self)
        boldAction.setShortcut("Ctrl+B")
        boldAction.triggered.connect(self.Bold)
         
        italicAction = QtWidgets.QAction(QtGui.QIcon("icons/italic.png"),"Italic",self)
        italicAction.setShortcut("Ctrl+I")
        italicAction.triggered.connect(self.Italic)
         
        underlAction = QtWidgets.QAction(QtGui.QIcon("icons/underl.png"),"Underline",self)
        underlAction.setShortcut("Ctrl+U")
        underlAction.triggered.connect(self.Underl)
 
        alignLeft = QtWidgets.QAction(QtGui.QIcon("icons/alignLeft.png"),"Align left",self)
        alignLeft.triggered.connect(self.alignLeft)
 
        alignCenter = QtWidgets.QAction(QtGui.QIcon("icons/alignCenter.png"),"Align center",self)
        alignCenter.setShortcut("Ctrl+E")
        alignCenter.triggered.connect(self.alignCenter)
 
        alignRight = QtWidgets.QAction(QtGui.QIcon("icons/alignRight.png"),"Align right",self)
        alignRight.triggered.connect(self.alignRight)
 
        alignJustify = QtWidgets.QAction(QtGui.QIcon("icons/alignJustify.png"),"Align justify",self)
        alignJustify.triggered.connect(self.alignJustify)
 
        self.backColor = QtWidgets.QToolButton(self)
        self.backColor.setStyleSheet("background : #fffffe")
        self.backColor.clicked.connect(self.FontBackColor)
 
        bulletAction = QtWidgets.QAction(QtGui.QIcon("icons/bullet.png"),"Insert Bullet List",self)
        bulletAction.triggered.connect(self.BulletList)
 
        numberedAction = QtWidgets.QAction(QtGui.QIcon("icons/number.png"),"Insert Numbered List",self)
        numberedAction.triggered.connect(self.NumberedList)
 
        space1 = QtWidgets.QLabel("  ",self)
        space2 = QtWidgets.QLabel(" ",self)
        space3 = QtWidgets.QLabel(" ",self)
 
        self.toolbar.addWidget(self.fontFamily)
        self.toolbar.addWidget(space1)
        self.toolbar.addWidget(self.fontSize)
        self.toolbar.addWidget(space2)
         
        self.toolbar.addSeparator()
         
        self.toolbar.addAction(boldAction)
        self.toolbar.addAction(italicAction)
        self.toolbar.addAction(underlAction)
         
        self.toolbar.addSeparator()
 
        self.toolbar.addAction(alignLeft)
        self.toolbar.addAction(alignCenter)
        self.toolbar.addAction(alignRight)
        self.toolbar.addAction(alignJustify)
 
        self.toolbar.addSeparator()
 
        self.toolbar.addAction(bulletAction)
        self.toolbar.addAction(numberedAction)

        self.toolbar.addSeparator()
 
        self.toolbar.addWidget(self.fontColor)
        self.toolbar.addWidget(self.backColor)
         
#------- Text Edit -----------------------------------
 
        self.text = QtWidgets.QTextEdit(self)
        self.text.setTabStopWidth(12)
        self.text.cursorPositionChanged.connect(self.updateTools)
        self.text.textChanged.connect(self.textChanged.emit)  

#------- Box Layout -----------------------------------

        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.text)
        self.layout.setContentsMargins(0,0,0,0)
             
    def Undo(self):
        self.text.undo()
 
    def Redo(self):
        self.text.redo()
 
    def Cut(self):
        self.text.cut()
 
    def Copy(self):
        self.text.copy()
 
    def Paste(self):
        self.text.paste()
         
    def CursorPosition(self):
        line = self.text.textCursor().blockNumber()
        col = self.text.textCursor().columnNumber()
        linecol = ("Line: "+str(line)+" | "+"Column: "+str(col))
        self.status.showMessage(linecol)
 
    def FontFamily(self,font):
        # if self.primed:
        font = QtGui.QFont(self.fontFamily.currentFont())
        self.text.setCurrentFont(font)
            # self.primed = False
 
    def FontSize(self, fsize):
        size = (int(fsize))
        cursor = self.text.textCursor()
        fmt = QtGui.QTextCharFormat()
        fmt.setFontPointSize(size)
        cursor.mergeCharFormat(fmt)
 
    def FontColor(self):
        c = QtWidgets.QColorDialog.getColor()
        self.fontColor.setStyleSheet("background : %s" %(c.name()))
        self.text.setTextColor(c)
         
    def FontBackColor(self):
        c = QtWidgets.QColorDialog.getColor()
        self.backColor.setStyleSheet("background : %s" %(c.name()))
        self.text.setTextBackgroundColor(c)
 
    def Bold(self):
        w = self.text.fontWeight()
        if w == 50:
            self.text.setFontWeight(QtGui.QFont.Bold)
        elif w == 75:
            self.text.setFontWeight(QtGui.QFont.Normal)
         
    def Italic(self):
        i = self.text.fontItalic()
         
        if i == False:
            self.text.setFontItalic(True)
        elif i == True:
            self.text.setFontItalic(False)
         
    def Underl(self):
        ul = self.text.fontUnderline()
 
        if ul == False:
            self.text.setFontUnderline(True) 
        elif ul == True:
            self.text.setFontUnderline(False)
             
    def lThrough(self):
        lt = QtGui.QFont.style()
 
        print(lt)
 
    def alignLeft(self):
        self.text.setAlignment(Qt.AlignLeft)
 
    def alignRight(self):
        self.text.setAlignment(Qt.AlignRight)
 
    def alignCenter(self):
        self.text.setAlignment(Qt.AlignCenter)
 
    def alignJustify(self):
        self.text.setAlignment(Qt.AlignJustify)

    def BulletList(self):
        print("bullet connects!")
        self.text.insertHtml("<ul><li></li></ul>")
 
    def NumberedList(self):
        print("numbered connects!")
        self.text.insertHtml("<ol><li></li></ol>")

    def updateTools(self):
        cursor = self.text.textCursor()
        fmt = cursor.charFormat()
        # self.fontFamily.setCurrentFont(fmt.font())
        # self.fontSize.setCurrentIndex(-1)
        self.fontColor.setStyleSheet("background : %s" %(fmt.foreground().color().name()))
        self.backColor.setStyleSheet("background : %s" %(fmt.background().color().name()))

    def toHtml(self):
        return self.text.toHtml()

    def toPlainText(self):
        return self.text.toPlainText()

    def setPlainText(self,text):
        self.text.setPlainText(text)

    def setHtml(self,html):
        self.text.setHtml(html)

    def document(self):
        return self.text.document()

    # def pt(self):
    #     self.primed = True