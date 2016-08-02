from arc.arcpreferences import PreferenceManager as PM
from arctool import ARCTool
from Default.emailfilter import EmailFilterTable, EmailFilterLogicValidator
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import arc.arcclasses as arcclasses
import arc.arcgui as arcgui
import quopri
import re

class Plugin(arcclasses.Plugin):
	headers = '|'.join(
		['From','Date','Sent','To','Cc','Bcc','Subject','Importance']
	)

	def __init__(self,package):
		super(Plugin,self).__init__(None,package)

		self.__name__ = "emaildump"
		# Required
		self.name = "Email Dump"
		self.authors = ["unonu"]
		self.version = (0,0,1)
		self.description="Finds a group of emails and dumps their information."
		self.contexts = ['Date']

		self.emails = []
		self.emailIds = {}
		self.fragments = {}
		self.fetched = False

		self.contextFilters = []

		self.igHeader = False
		self.igReplies= False
		self.igDup 	  = False
		self.igFirstDup = False
		self.igImages = False
		self.igFormat = False
		self.igSpace = False

		self.delim = ''

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

		self.widget.tableLayout.addWidget(self.widget.emailFilterTable)
		self.widget.fetchButton.clicked.connect(self.makeRequest)
		self.widget.logicBox.setValidator(EmailFilterLogicValidator())
		self.widget.selectEdit.textChanged.connect(
			lambda x: self.widget.fetchButton.setEnabled(
				x != '' or len(self.widget.emailFilterTable) > 0
			)
		)

		#Options
		self.widget.contextCheck.stateChanged.connect(
			lambda x : self.widget.fetchButton.setEnabled(x > 0)
		)
		self.widget.headerCheck.stateChanged.connect(
			lambda x: self.setIgHeader(x > 0)
		)
		self.widget.quoteCheck.stateChanged.connect(
			lambda x: self.setIgReplies(x > 0)
		)
		self.widget.dupCheck.stateChanged.connect(
			lambda x: self.setIgDup(x > 0)
		)
		self.widget.firstCheck.stateChanged.connect(
			lambda x: self.setIgFirstDup(x > 0)
		)
		self.widget.imageCheck.stateChanged.connect(
			lambda x: self.setIgImages(x > 0)
		)
		self.widget.formatCheck.stateChanged.connect(
			lambda x: self.setIgFormat(x > 0)
		)
		self.widget.spaceCheck.stateChanged.connect(
			lambda x: self.setIgSpace(x > 0)
		)
		self.widget.delimeterEdit.textChanged.connect(
			lambda: self.updateDelim()
		)
		self.widget.dupCheck.stateChanged.connect(
			lambda x: self.widget.dupWidget.setEnabled(x > 0)
		)
		self.widget.dupStrength.valueChanged.connect(
			lambda x: self.widget.dupLabel.setText('%d Words' %(x))
		)

	#call super
	def update(self):
		super(Plugin,self).update()

		#updated from extras
		if 'filters' in self.extras:
			self.widget.emailFilterTable.fromSerial(self.extras['filters'])

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
		self.options['headerCheck'] =\
			(self.widget.headerCheck.isChecked(), 'checked')
		self.options['quoteCheck'] =\
			(self.widget.quoteCheck.isChecked(), 'checked')
		self.options['dupCheck'] =\
			(self.widget.dupCheck.isChecked(), 'checked')
		self.options['firstCheck'] =\
			(self.widget.dupCheck.isChecked(), 'checked')
		self.options['imageCheck'] =\
			(self.widget.imageCheck.isChecked(), 'checked')
		self.options['formatCheck'] =\
			(self.widget.formatCheck.isChecked(), 'checked')
		self.options['spaceCheck'] =\
			(self.widget.spaceCheck.isChecked(), 'checked')
		self.options['dupStrength'] =\
			(self.widget.dupStrength.value(), 'value')

		self.extras['filters'] = self.widget.emailFilterTable.serialize()

	#override
	def generate(self):
		if not self.fetched:
			r = self.makeRequest()
			if r < 0:
				return None

		doc = QTextDocument()
		cursor = QTextCursor(doc)

		_c = _b = None
		for message in self.emails:
			_c = cursor.charFormat()
			_b = cursor.blockFormat()
			text = ''
			for part in message.walk():
				typ = part.get_content_type()
				dis = part.get('Content-Disposition')
				if dis != 'attachment':
					if typ == 'text/plain':
						try:
							text = ('<p>'
									+ part.get_payload(decode=True)
										.decode('utf-8') + '</p>'
							)
						except UnicodeDecodeError:
							print("Couldn't decode this part")
							continue
					elif typ == 'text/html':
						try:
							text = part.get_payload(decode=True)\
								.decode('utf-8')
						except UnicodeDecodeError:
							print("Couldn't decode this part")
							continue
					elif 'image/' in typ and not self.igImages:
						# Embed image
						# print('embed image')
						dis = dis.split(';',1)
						# print(part.get('Content-ID'))
						# print(dis[1])
						if dis[0] == 'inline':
							img = QImage()
							img.loadFromData(part.get_payload(decode=True))
							doc.addResource(
								doc.ImageResource,
								QUrl('cid:'+part.get('Content-ID')[1:-1]),
								img
							)
			if self.igReplies:
				text = self.stripReplies(message,text)
			if self.igHeader:
				text = self.stripHeaders(message,text)
			cursor.insertHtml(text)
			if self.delim != '':
				cursor.insertHtml('<br/><p>' + self.delim + '</p><br/>')
			cursor.insertBlock()
			cursor.setCharFormat(_c)
			cursor.setBlockFormat(_b)

		if self.igFormat:
			cursor.select(cursor.Document)
			cursor.setCharFormat(_c)
			cursor.setBlockFormat(_b)
		if self.igImages:
			doc.setHtml(self.stripImages(doc.toHtml()))
		if self.igDup:
			doc.setHtml(self.stripDuplicate(doc.toHtml()))
		if self.igSpace:
			doc.setHtml(self.collapseSpace(doc.toHtml()))

		# print("generated")
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
				ARCTool.getStatusBar().showMessage(
					"Selecting mailbox"
				)
				mailbox = self.widget.selectEdit.text()
				if (mailbox == '' or mailbox.lower() =='inbox') and req == '':
					ARCTool.getStatusBar().showMessage(
						"Can't select Inbox without at least one filter."
					)
					return -1
				M.select(mailbox if mailbox != '' else 'INBOX',readonly=True)
				try:
					ARCTool.getStatusBar().showMessage(
						"Searching "+(mailbox if mailbox != '' else 'Inbox')
					)
					typ, data = M.search(None, req)
				except protocol.error as e:
					ARCTool.getStatusBar().showMessage(
						"Couldn't search mailbox: "+str(e)
					)
				else:
					ARCTool.getStatusBar().showMessage(
						"Fetching Messages"
					)
					self.emails = []
					for num in data[0].split():
						typ, data = M.fetch(num, '(RFC822)')
						self.emails.append(
							email.message_from_bytes(data[0][1])
						)
						id = self.emails[-1].get('Message-ID')
						if id:
							self.emailIds[id] = self.emails[-1]
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
		return 0

	def setIgHeader(self, b):
		self.igHeader = b

	def setIgReplies(self, b):
		self.igReplies = b

	def setIgDup(self, b):
		self.igDup = b

	def setIgFirstDup(self, b):
		self.igFirstDup = b

	def setIgImages(self, b):
		self.igImages = b

	def setIgFormat(self, b):
		self.igFormat = b

	def setIgSpace(self, b):
		self.igSpace = b

	def updateDelim(self):
		self.delim = self.widget.delimeterEdit.text()

	def stripHeaders(self,message,text):
		text = re.sub('(?P<p><p )?.*?(?:%s):.+(?(p)[^`]*?</p>)\n?'\
			%(self.headers),'',text)
		return text

	def stripImages(self,text):
		text = re.sub('(?s)<img .+?(?:/>|</img>)','',text)
		return text

	def collapseSpace(self,text):
		# print("hello")
		# Collapse Spaces
		text = re.sub('\xa0',' ',text)
		text = re.sub(' +',' ',text)

		# Collapse Breaks
		text = re.sub(r'<br>\s*</br>','<br/>',text)
		text = re.sub(r'(?<=>)\s*<br\s*/>\s*(?=</)', '',text)
		text = re.sub(r'\s*<span( [^>]+)?>\s*</span>\s*','',text)
		text = re.sub(r'\s*<p( [^>]+)?>\s*</p>\s*','',text)

		return text

	def stripReplies(self,message,text):
		ids = message.get("References")
		if ids:
			ids = re.split(',| ',ids)
			ids = [i.strip() for i in ids if i != '']
			# print(ids)
			for id in ids:
				if id in self.emailIds:
					# Remove this previous emails content from me
					ref = ''
					for part in self.emailIds[id].walk():
						typ = part.get_content_type()
						dis = part.get('Content-Disposition')
						if dis != 'attachment':
							if typ == 'text/plain' or typ == 'text/html':
								ref = part.get_payload(decode=True)\
									.decode('utf-8')
					# if self.igHeader:
					# 	ref = self.stripHeaders(self.emailIds[id[-2]],ref)

					bodyText = re.search('(?s)<body[^>]*?>(.+)</body>',text)
					bodyRef = re.search('(?s)<body[^>]*?>(.+)</body>',ref)
					if bodyText and bodyRef:
						bodyText = bodyText.group(1).strip()
						container = text.split(bodyText)
						bodyRef = bodyRef.group(1).strip()
						bodyText = re.sub('\xa0',' ',bodyText)
						bodyRef = re.sub('\xa0',' ',bodyRef)
						bodyTags = re.findall(r'\s*<.+?>\s*',bodyText)
						bodyText = re.sub(r'\s*<.+?>\s*',chr(1),bodyText)
						bodyRef = [re.escape(p) for p in \
							re.split(r'\s*<.+?>\s*',bodyRef) if p != '']
						bodyRef = '(?s)' + (chr(1)+'+').join(bodyRef)
						bodyRef = re.sub(r'(\\\s)+',r'\\s+',bodyRef)

						# Search for the original message within the reply
						partial = re.search(bodyRef,bodyText)
						if partial:
							excise = partial.group(0).count(chr(1))
							offset =\
								bodyText[:bodyText.find(partial.group(0))]\
								.count(chr(1))
							bodyText = bodyText.replace(partial.group(0),'')
							bodyTags = (bodyTags[:offset]
										+ bodyTags[offset+excise:])
							# Replace the tags
							for t in bodyTags:
								bodyText = bodyText.replace(chr(1),t,1)
							text = container[0] + bodyText + container[1]
						# We messed up? Impossible...
						# else:
						# 	print(bodyText)
						# 	print('-------vvvvvv------')
						# 	print(bodyRef)
		return text

	def stripDuplicate(self, text):
		num = self.widget.dupStrength.value()
		globs = {}
		body = re.search('(?s)<body[^>]*?>(.+)</body>',text).group(1)
		container = text.split(body)
		tags = re.findall(r'(?s)\s*<.+?>\s*',body)
		stripped = re.sub(r'(?s)\s*<.+?>\s*',chr(1),body)
		stripped = re.sub('\xa0',' ',stripped)
		stripped = re.sub(r'&nbsp;',' ',stripped)
		spaces = re.findall(r'\s+',stripped)
		stripped = re.sub(r'\s+',r' ',stripped)
		# print("stripped")
		_ = []
		for word in re.finditer(r'(?:^| )(.+?)(?:(?= )|$)',stripped):
			_.append((word.group(1),word.start(1),word.end(1)))
			if len(_) == num:
				hsh = ''.join(x[0].replace(chr(1),'') for x in _).__hash__()
				if hsh not in globs:
					globs[hsh] = []
				globs[hsh].append((_[0][1],_[-1][2]))
				_.pop(0)

		# print("globbed")
		chains = []
		ranges = []
		for d in globs:
			if len(globs[d]) > 1:
				ranges += [x for x in globs[d][1 if self.igFirstDup else 0:]]
		ranges.sort()
		for r in ranges:
			if len(chains) == 0:
				chains.append([r[0],r[1]])
				continue
			if r[0] <= chains[-1][1]:
				chains[-1][1] = r[1]
			else:
				chains.append([r[0],r[1]])
		# print("chained")
		# This is complicated... Only remove the text but keep the tags
		offset = 0
		for c in chains:
			# Could partition, but I want variable names
			chunk = stripped[c[0]-offset:c[1]-offset]
			head = stripped[:c[0]-offset]
			tail = stripped[c[1]-offset:]
			# print(chunk)
			# print(len(head), len(tail))
			tagsRemoved = chunk.count(chr(1))
			spaceRemoved = chunk.count(' ')
			offset += len(chunk) - tagsRemoved
			spaces = (spaces[head.count(' '):]
					  + spaces[head.count(' ')
					  + spaceRemoved:])

			stripped = head + chr(1)*tagsRemoved + tail
		# print("excised")

		for s in spaces:
			stripped = stripped.replace(' ',s,1)
		for t in tags:
			stripped = stripped.replace(chr(1),t,1)
		# print("replaced")

		return container[0] + stripped + container[1]