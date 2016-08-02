'''
	Need to check labels in Format Tab and tell user if they're wrong
	# Need to serialise all of this somehow
	Colours for different groups?
	oauth support?
'''

from arc.arcpreferences import PreferenceManager as PM
from arctool import ARCTool
from Default.emailfilter import EmailFilterTable, EmailFilterLogicValidator
from Default.glob import *
from Default.textedit import TextEditor
from arc.num2word import num2word
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import arc.arcclasses as arcclasses
import arc.arcgui as arcgui
import quopri
import re

class Plugin(arcclasses.Plugin):
	def __init__(self,package):
		super(Plugin,self).__init__(None,package)

		self.__name__ = "emailscrapebasic"
		# Required
		self.name = "Email Scrape (Basic)"
		self.authors = ["unonu"]
		self.version = (0,0,1)
		self.description =\
			"Finds a group of emails and re-presents their information."
		self.contexts = ['Date']

		self.emails = []
		self.groups = {}
		self.fetched = False
		self.groupColors = [] #https://en.wikipedia.org/wiki/Web_colors
		self.currentGroup = None
		self.items = {}
		self.fragments = {}

		self.igHeader = False
		self.igReplies= False
		self.igDup 	  = False
		self.igImages = False

		self.delim = ''

		self.contextFilters = []

	#needed
	def setupUi(self):
		#Filter
		self.widget.emailFilterTable = EmailFilterTable()
		self.widget.emailFilterTable.tableChanged.connect(
			lambda x: self.widget.fetchButton.setProperty('enabled',(x > 0 or
				self.widget.contextCheck.isChecked()))
		)
		self.widget.emailFilterTable.tableChanged.connect(
				ARCTool.signalProfileChanged
		)

		self.widget.filterTableLayout.addWidget(self.widget.emailFilterTable)
		self.widget.fetchButton.clicked.connect(self.makeRequest)
		self.widget.logicBox.setValidator(EmailFilterLogicValidator())
		self.widget.selectEdit.textChanged.connect(
			lambda x: self.widget.fetchButton.setEnabled(
				x != '' or len(self.widget.emailFilterTable) > 0
			)
		)

		#Group
		self.widget.mailBrowser.setUndoRedoEnabled(True)
		self.widget.mailSelector.currentIndexChanged.connect(
			self.updateMailBrowser
		)
		self.widget.groupList.currentItemChanged.connect(self.setGroup)
		self.widget.groupList.itemChanged.connect(
			lambda x: self.renameGroup(self.currentGroup,x.text())
		)
		self.widget.groupList.itemActivated.connect(
			self.widget.groupList.editItem
		)
		self.widget.addGroup.setIcon(QIcon("icons/list-add.png"))
		self.widget.addGroup.clicked.connect(lambda: self.addGroup())
		self.widget.removeGroup.setIcon(QIcon("icons/list-remove.png"))
		self.widget.removeGroup.clicked.connect(lambda: self.removeGroup())
		self.widget.selectGroup.clicked.connect(lambda: self.selectGroup())
		self.widget.clearGroup.clicked.connect(lambda: self.clearGroup())
		self.widget.addSelection.clicked.connect(lambda: self.addToGroup())
		self.widget.removeSelection.clicked.connect(
			lambda: self.removeFromGroup()
		)
		self.widget.mailBrowser.copyAvailable.connect(
			lambda x: self.widget.selectionBox.setEnabled(
				x and self.widget.groupBox.isEnabled()
			)
		)
		# self.widget.groupList.currentTextChanged

		#Format
		self.widget.formatEdit = TextEditor()
		self.widget.formatLayout.addWidget(self.widget.formatEdit)

		#Options
		self.widget.contextCheck.stateChanged.connect(
			lambda x : self.widget.fetchButton.setProperty('enabled',x > 0)
		)
		self.widget.imageCheck.stateChanged.connect(
			lambda x: self.setIgImages(x > 0)
		)
		self.widget.delimeterEdit.textChanged.connect(
			lambda: self.updateDelim()
		)

	#call super
	def update(self):
		super(Plugin,self).update()

		#updated from extras
		if 'filters' in self.extras:
			self.widget.emailFilterTable.fromSerial(self.extras['filters'])
		if 'format' in self.extras:
			self.widget.formatEdit.setHtml(self.extras['format'])
		if 'groups' in self.extras:
			for g in self.extras['groups'].split(','):
				self.addGroup(g)

	#needed
	def storeOptions(self):
		self.options['logicBox'] =\
			(self.widget.logicBox.text(),'text')
		self.options['selectEdit'] =\
			(self.widget.logicBox.text(),'text')
		self.options['delimeterEdit'] =\
			(self.widget.delimeterEdit.text(), 'text')
		self.options['contextCheck'] =\
			(self.widget.contextCheck.isChecked(), 'checked')
		self.options['imageCheck'] =\
			(self.widget.imageCheck.isChecked(), 'checked')

		self.extras['filters'] = self.widget.emailFilterTable.serialize()
		self.extras['format'] = self.widget.formatEdit.toHtml()
		self.extras['groups'] = ','.join(self.groups.keys())

	#override
	def generate(self):
		if not self.fetched:
			r = self.makeRequest()
			if r < 0:
				return None
		doc = QTextDocument()
		cursor = QTextCursor(doc)

		self.constructItems()
		self.constructFragments()

		_c = _b = None
		for f in self.fragments:
			_c = cursor.charFormat()
			_b = cursor.blockFormat()
			cursor.insertFragment(QTextDocumentFragment(f))
			if self.delim != '':
				cursor.insertHtml('<br/><p>' + self.delim + '</p><br/>')
			cursor.insertBlock()
			cursor.setCharFormat(_c)
			cursor.setBlockFormat(_b)

		return doc

	def makeRequest(self):
		# make async? or at least talk to the user

		import imaplib, email

		# Logic
		req, r, i = self.widget.emailFilterTable.getRequest(
			self.widget.logicBox.text()
		)

		if not req and r == 2:
			ARCTool.getStatusBar().showMessage(
				"Couldn't find filter label '%s'" %(i)
			)
			self.widget.logicBox.setSelection(
				self.widget.logicBox.text().find(i),len(i)
			)
			return -1

		if req == '':
			req = 'ALL'
			
		# Context
		if self.widget.contextCheck.isChecked():
			b = ARCTool.getContext().getBegin("d-MMM-yyyy")
			e = ARCTool.getContext().getEnd()
			if b:
				req += ' SINCE %s' %(b)
			if e:
				e = e.addDays(1)
				e = e.toString("d-MMM-yyyy")
				req += ' BEFORE %s' %(e)

		print(req)

		protocol = imaplib.IMAP4_SSL if PM.getPreference('Default Package',
														 'emailssl')\
									 else imaplib.IMAP4

		with protocol(
			PM.getPreference('Default Package','emailserver'),
			int(PM.getPreference('Default Package','emailport') or 993)
		) as M:
		
			passDialog = arcgui.LoginDialog(self.widget)
			try:
				passDialog.credentials.connect(
					lambda x, y: M.login(x,y) if not(x==y=='') else print('abort')
				)
			except:
				ARCTool.getStatusBar().showMessage(
					"Couldn't login to IMAP server."
				)
				return -1

			passDialog.exec()

			try:
				mailbox = self.widget.selectEdit.text()
				if (mailbox == '' or mailbox.lower() =='inbox') and req == '':
					ARCTool.getStatusBar().showMessage(
						"Can't select Inbox without at least one filter."
					)
					return -1
				M.select(mailbox if mailbox != '' else 'INBOX',readonly=True)
				try:
					typ, data = M.search(None, req)
				except protocol.error as e:
					ARCTool.getStatusBar().showMessage(
						"Couldn't search mailbox: "+str(e)
					)
				else:
					self.emails = []
					for num in data[0].split():
						typ, data = M.fetch(num, '(RFC822)')
						self.emails.append(
							email.message_from_bytes(data[0][1])
						)
					M.close()
			except protocol.error as e:
				ARCTool.getStatusBar().showMessage(
					"Couldn't login to IMAP server: "+str(e)
				)
				return -1

		ARCTool.getStatusBar().showMessage(
			"Fetched %d message%s" %(len(self.emails),
				'' if len(self.emails) == 1 else 's'
			)
		)
		self.fetched = True
		self.updateMailList()
		self.widget.setCurrentIndex(1)
		return 0

	def updateMailList(self):
		self.widget.mailSelector.clear()
		for m in self.emails:
			self.widget.mailSelector.addItem(
				str(quopri.decodestring(m.__getitem__('subject'))) or 'No Subject'
			)

	def updateMailBrowser(self):
		if len(self.emails) == 0:
			self.widget.mailBrowser.setPlainText('')
			self.widget.browserWidget.setEnabled(False)
			return
		self.widget.browserWidget.setEnabled(True)

		message = self.emails[self.widget.mailSelector.currentIndex()]
		self.widget.mailBrowser.setDocument(
			emailToQTD(message,not self.igImages)
		)

	def addGroup(self,name='Group'):
		# Assure no duplicates
		if name in self.groups:
			i = 1
			dup = ''
			while name+dup in self.groups:
				dup = ' ' + num2word(i).capitalize()
				i += 1
			name += dup
		# Map emails to list of position tupples with dist > 0
		self.groups[name] = {}
		item = QListWidgetItem(name)
		item.setFlags(item.flags() | Qt.ItemIsEditable)
		self.widget.groupList.addItem(item)
		self.widget.groupList.setCurrentRow(len(self.groups)-1)
		self.setGroup()
		# if a highlighted section exactly matches a range then remove that
		# whole range and only that range if no exact matches are found, then
		# remove from all partial matches (splitting as necessary) no
		# duplicates, no mistakes

	def setGroup(self):
		item = self.widget.groupList.currentItem()
		if item:
			self.currentGroup = item.text()
			self.widget.groupBox.setEnabled(True)
		else:
			self.widget.groupBox.setEnabled(False)

	def removeGroup(self,name=None):
		if not name:
			name = self.widget.groupList.takeItem(
				self.widget.groupList.currentRow()
			).text()
		if name not in self.groups: return
		del self.groups[name]

		self.widget.groupList.setCurrentRow(0)
		self.setGroup()

	def renameGroup(self,old,new):
		if new == old or old not in self.groups: return
		if new in self.groups or new == '':
			self.widget.groupList.currentItem().setText(old)
			return
		self.groups[new] = self.groups[old]
		del self.groups[old]
		self.setGroup()

	def addToGroup(self,name=None,beg=None,end=None):
		cursor = self.widget.mailBrowser.textCursor()
		if not beg:
			beg = cursor.selectionStart()
		if not end:
			end = cursor.selectionEnd()
		if beg == end : return

		# get the group name
		# Maybe the user might not want to create a new group? ehhhh w/e
		if not name:
			name = self.widget.groupList.currentItem().text()
		if name not in self.groups:
			self.groups[name] = {}

		email = self.emails[self.widget.mailSelector.currentIndex()]
		set = [None]
		if email in self.groups[name]:
			set = self.groups[name][email]
		else:
			self.groups[name][email] = set

		if (beg,end) in set: return

		# I'm taking out multiple sections in a group. uncomment to add back
		# set.append((beg,end)) <===\\
		set[0] = (beg,end) #    <===//

	def removeFromGroup(self,name=None,beg=None,end=None):
		cursor = self.widget.mailBrowser.textCursor()
		if not beg:
			beg = cursor.selectionStart()
		if not end:
			end = cursor.selectionEnd()
		if beg == end : return

		# get the group name
		if not name:
			name = self.widget.groupList.currentItem().text()
		# Maybe the user might not want to create a new group? eh w/e
		if name not in self.groups: return

		email = self.emails[self.widget.mailSelector.currentIndex()]
		if email not in self.groups[name]: return

		set = self.groups[name][email]

		if (beg,end) in set:
			set.remove((beg,end))
			return

		matches = []
		for s in set:
			if ((beg >= s[0] and beg < s[1]) or (end <= s[1] and end > s[0]) or
					(s[0] >= beg and s[1] <= end)):
				matches.append(s)

		for m in matches:
			set.remove(m)
			if beg-m[0] > 0:
				set.append((m[0],beg))
			if m[1]-end > 0:
				set.append((end,m[1]))

	def clearGroup(self,name=None):
		if not name:
			name = self.widget.groupList.currentItem().text()

		email = self.emails[self.widget.mailSelector.currentIndex()]
		# self.groups[name][email] = []
		self.groups[name][email] = [None]

	def selectGroup(self,name=None):
		if not name:
			name = self.widget.groupList.currentItem().text()

		email = self.emails[self.widget.mailSelector.currentIndex()]
		if email not in self.groups[name]: return

		set = self.groups[name][email]
		cursor = self.widget.mailBrowser.textCursor()
		self.widget.mailBrowser.setTextCursor(cursor)
		self.widget.mailBrowser.undo()
		cursor.beginEditBlock()
		highlight = QTextCharFormat()
		brush = QBrush(QColor('#00e34b'))
		highlight.setBackground(brush)
		for s in set:
			cursor.setPosition(s[0])
			cursor.setPosition(s[1],cursor.KeepAnchor)
			cursor.mergeCharFormat(highlight)
		cursor.endEditBlock()

	def constructItems(self):
		self.items = {}
		for g in self.groups:
			item = GlobItem()
			for message in self.groups[g]:
				doc = QTextDocument()

				for part in message.walk():
					typ = part.get_content_type()
					dis = part.get('Content-Disposition')
					if dis != 'attachment':
						if typ == 'text/plain':
							body = ''
							try:
								body = part.get_payload(decode=True).decode('utf-8')
							except UnicodeDecodeError:
								body = quopri.decodestring(part.get_payload())
							doc.setPlainText(body)
						elif typ == 'text/html':
							body = ''
							try:
								body = part.get_payload(decode=True).decode('utf-8')
							except UnicodeDecodeError:
								body = quopri.decodestring(part.get_payload())
							doc.setHtml(body)
				curs = []
				for p in self.groups[g][message]:
					curs.append(QTextCursor(doc))
					curs[-1].setPosition(p[0])
					curs[-1].setPosition(p[1],curs[-1].KeepAnchor)
				if len(curs) > 0:
					item + Glob(*curs)
			self.items[g] = item

	def constructFragments(self):
		self.fragments = []
		ref = QTextDocument()
		for message in self.emails:
			doc = self.widget.formatEdit.document().clone()

			# for part in message.walk():
			# 	typ = part.get_content_type()
			# 	dis = part.get('Content-Disposition')
			# 	if dis != 'attachment':
			# 		if typ == 'text/plain':
			# 			ref.setPlainText(
			# 				part.get_payload(decode=True).decode('utf-8')
			# 			)
			# 		elif typ == 'text/html':
			# 			ref.setHtml(
			# 				part.get_payload(decode=True).decode('utf-8')
			# 			)

			body = ''
			resources = {}
			parts = [p for p in message.walk()]
			i=0
			for part in parts:
				typ, dis = part.get_content_type(), part.get('Content-Disposition')
				if part.is_multipart():
					for sp in reversed([s for s in part.walk()]):
						if sp not in parts:
							parts.insert(i+1,sp)
				i += 1

				# Prefer HTML
				if typ == 'text/html' and dis == None:
					try:
						body = part.get_payload(decode=True).decode('utf-8')
					except UnicodeDecodeError:
						body = str(quopri.decodestring(part.get_payload()))
				elif typ == 'text/plain' and dis == None and body == '':
					try:
						body = part.get_payload(decode=True).decode('utf-8')
					except UnicodeDecodeError:
						body = str(quopri.decodestring(part.get_payload()))
				elif typ[:typ.find('/')] == 'image' and self.igImages:
					# Embed image
					dis = dis.split(';',1)
					if dis[0] == 'inline':
						# print(part.get('Content-ID'))
						# print("\nimage:",part.get_filename())
						resources['cid:'+part.get('Content-ID')[1:-1]] =\
							part.get_payload(decode=True)
			ref.setHtml(body)

			for group in self.groups:
				i=0
				cur = doc.find('$%s$'%(group),0,
							   options=doc.FindCaseSensitively
				)
				# print('find $%s$: %s' %(group, 'FAIL' if cur.isNull() else 'OK'))
				text, ok, perc = self.items[group].getText(ref)
				# print('find starting at %d: %s %f' %(i,text,perc))
				while not cur.isNull():
					# Use the GlobItem to get text from the ref document
					if not ok:
						cur.insertHtml(
							('<span style="color:red; font-weight:bold">%s '\
							+ '[%0.1f%% certainty]</span>') %(text,perc*100))
					elif perc < .6:
						cur.insertHtml(
							('<span style="color:red">%s [%0.1f%% certainty]<'\
							+ '/span>') %(text,perc*100))
					else:
						cur.insertText(text)

					i = cur.selectionEnd()
					cur = doc.find('$%s$'%(group),cur,
								   options=doc.FindCaseSensitively)
			# 		print('looking for next match')
			# 	print('i is now',i)
			# print('appended fragment',doc.toPlainText())
			self.fragments.append(doc)

	def setIgImages(self, b):
		self.igImages = b
		self.updateMailBrowser()

	def updateDelim(self):
		self.delim = self.widget.delimeterEdit.text()

def emailToQTD(message,showImages=True):
	body = ''
	resources = {}
	
	parts = [p for p in message.walk()]
	i=0
	for part in parts:
		typ, dis = part.get_content_type(), part.get('Content-Disposition')
		if part.is_multipart():
			for sp in reversed([s for s in part.walk()]):
				if sp not in parts:
					parts.insert(i+1,sp)
		i += 1

		# Prefer HTML
		if typ == 'text/html' and dis == None:
			try:
				body = part.get_payload(decode=True).decode('utf-8')
			except UnicodeDecodeError:
				body = str(quopri.decodestring(part.get_payload()))
		elif typ == 'text/plain' and dis == None and body == '':
			try:
				body = part.get_payload(decode=True).decode('utf-8')
			except UnicodeDecodeError:
				body = str(quopri.decodestring(part.get_payload()))
		elif typ[:typ.find('/')] == 'image' and showImages:
			# Embed image
			dis = dis.split(';',1)
			if dis[0] == 'inline':
				# print(part.get('Content-ID'))
				# print("\nimage:",part.get_filename())
				resources['cid:'+part.get('Content-ID')[1:-1]] =\
					part.get_payload(decode=True)
			
	doc = QTextDocument()
	doc.setHtml(body)
	# print(body)
	for r in resources:
		img = QImage()
		img.loadFromData(resources[r])
		doc.addResource(doc.ImageResource, QUrl(r), img)

	return doc