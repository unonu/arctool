from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtPrintSupport import *

PANDOC = False
try:
	import pypandoc
	PANDOC = True
except ImportError:
	pass

class Document(QTextDocument):
	realHtml = ('<html><head><meta http-equiv="Content-Type"'
				'content="text/html; charset=utf-8"/></head><body>')
	def __init__(self,title="Untitled Document"):
		super(Document,self).__init__()
		self.title = title
		# self.sections = []
		self.cursor = QTextCursor(self)

	def addSection(self,section):
		# self.sections.append(section)
		content = section.getContent()
		if not content:
			return -1

		if section.showTitle:
			# These format options should be grabbed from preferences
			title = QTextCharFormat()
			font = QFont("Noto Sans", 12)
			font.setUnderline(True)
			font.setBold(True)
			title.setFont(font)

			self.realHtml += ('<h1>'
							  + section.getTitle()
							  + '</h1>')
			self.cursor.insertText(section.getTitle(), title)
			self.cursor.insertBlock()

		_c = self.cursor.charFormat()
		_b = self.cursor.blockFormat()
		self.realHtml += content.toHtml()
		self.cursor.insertFragment(QTextDocumentFragment(content))
		self.cursor.insertBlock()
		self.cursor.setCharFormat(_c)
		self.cursor.setBlockFormat(_b)

		return 0

	def setTitle(self,title):
		self.title = title

	def getTitle(self):
		return self.title

def textExport(document,title=''):
	path = QFileDialog.getSaveFileName(
		None,"Export Report",title+'.txt',
		"Plain Text (*.txt)"
	)
	if path is None or path[0] == '':
		return

	writer = QTextDocumentWriter(path[0],b"plaintext")
	writer.write(document)

def htmlExport(document,title=''):
	path = QFileDialog.getSaveFileName(
		None,"Export Report",title+'.html',
		"Hyper-Text Markup Language (*.html)"
	)
	if path is None or path[0] == '':
		return

	writer = QTextDocumentWriter(path[0],b"HTML")
	writer.write(document)

def pdfExport(document):
	printer = QPrinter()
	dlg = QPrintDialog(printer)
	if (dlg.exec() != QDialog.Accepted):
		return

	document.print(printer);

def docxExport(document,title=''):
	if not PANDOC: return

	path = QFileDialog.getSaveFileName(
		None,"Export Report",title+'.docx',
		"Microsoft Word Document 2007/2010/2013 (*.docx)"
	)
	if path is None or path[0] == '':
		return

	pypandoc.convert(document.realHtml + '</body>', 'docx',
					 outputfile=path[0], format='html',
					 extra_args=['-s','-S','--email-obfuscation=none'])

def odtExport(document,title=''):
	if not PANDOC: return

	path = QFileDialog.getSaveFileName(
		None,"Export Report",title+'.odt',
		"OpenDocument Text (*.odt)"
	)
	if path is None or path[0] == '':
		return

	pypandoc.convert(document.realHtml + '</body>', 'odt',
					 outputfile=path[0], format='html',
					 extra_args=['-s','-S','--email-obfuscation=none'])