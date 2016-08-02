from PyQt5 import QtCore, QtGui, QtWidgets
import re

class EmailFilterLogicValidator(QtGui.QValidator):
	def __init__(self):
		super(EmailFilterLogicValidator,self).__init__()

	def validate(self,str,pos):

		if re.search('(?:&|\|){3,}',str):
			return (self.Invalid,str,pos)
		if str.count(')') > str.count('('):
			return (self.Invalid,str,pos)

		str = re.sub('!+','!',str)
		str = re.sub(' +',' ',str)
		# Invalid characters
		non = [x for x in re.split('[ ()&!|\w]+',str) if x != '']
		# Operands
		pat = [x for x in re.split('''(?ix)[&|]{1,2}|
									(?:^|(?<=\ ))and(?=\W)|
									(?:^|(?<=\ ))or(?=\W)|
									(?<!^not)(?<!\ not)
									(?<!\(not)(?<!\()(?<!!)\ +(?!\))''',str)\
									if x != '']
		ops = re.findall('''(?ix)&{1,2}|\|{1,2}|(?:^|(?<=\ ))and(?=\W)|
							(?:^|(?<=\ ))or(?=\W)''',str)
		end = re.search('([\w]+) *\)*? *$',str) # the last word is an operand?
		if end:
			end = end.group(1).lower() not in ['and','or','not']
		pre = str.count('(') == str.count(')') # parentheses match?
		par = len(pat)-1 == len(ops) # odd parity of operators and operands?

		# print(non,pat,ops,end,pre,par)

		if str == '' or (pre and end and par and len(non) == 0):
			return (self.Acceptable,str,pos)
			
		if len(non) == 0:
			return (self.Intermediate,str,pos)

		# if (pre and end and par) and len(non) == 0:
		# 	return (self.Intermediate,str,pos)

		return (self.Invalid,str,pos)

	@staticmethod
	def fixup(str):
		str = re.sub(r'(?i)(?:(^|(?<= ))and(?:[! ]))|&{1,2}',
						'',str)
		str = re.sub(r'(?i)(?:(^|(?<= ))or(?:[! ]))|\|{1,2}',
						' OR ',str)
		str = re.sub(r'(?i)(?:(^|(?<= ))not(?:[! ]))|!',
						' NOT ',str)
		str = re.sub(r'(?i)(?:^| |\()not +not(?=[! ])',' ',str)
		str = re.sub(r'!+',' !',str)
		str = re.sub(r'(?i)(?:^| |\()not *!','!',str)
		str = re.sub(r'(?i)! *not ','!',str)
		# str = re.sub(r'(?i)\( *(and |or |&{1,2}|\|{1,2})', '(',str)
		str = re.sub(r'(?i)((?:^| )and |(?:^| )or |&{1,2}|\|{1,2}) *\)'
					 ,')',str)
		str = re.sub(r'(?i)(?:^| )and +and(?= )',' and',str)
		str = re.sub(r'(?i)(?:^| )or +or(?= )',' or',str)
		str = re.sub(r'(?:^| )([&|]{1,2}) +[&|]{1,2}',r' \1 ',str)
		str += ')'*(str.count('(') - str.count(')'))
		str = re.sub(r'\( *\)',' ',str)
		str = re.sub(r'([\w!])(?=\()',r'\1 ',str)
		str = re.sub(r'(?<=\()([\w!])',r' \1',str)
		str = re.sub(r'([\w!]) *(?=\))',r'\1 ',str)
		str = re.sub(r'(?<=\))([\w!])',r'\1',str)
		str = re.sub(r' {2,}',' ',str)
		str = re.sub(r'\( ','(',str)
		str = re.sub(r' \)',')',str)

		# if not re.match('^(.)$',str):
		# 	str = '('+str+')'
		return re.sub(r' +',' ',str)

class EmailFilterLabelValidator(QtGui.QValidator):
	def __init__(self):
		super(EmailFilterLabelValidator,self).__init__()

	def validate(self,str,pos):
		non = len(re.findall('[\W]',str))
		if str.lower() in ['and','or','not']:
			return (self.Intermediate,str,pos)
		return (self.Invalid,str,pos) if non > 0 else (self.Acceptable,str,pos)

	@staticmethod
	def fixup(str):
		str = re.sub('[\W]+','',str)
		str = re.sub('(?i)^and$','',str)
		str = re.sub('(?i)^or$','',str)
		str = re.sub('(?i)^not$','',str)
		return str

class EmailFilterTable(QtWidgets.QTableWidget):
	tableChanged = QtCore.pyqtSignal([int])

	def __init__(self,parent=None):
		super(EmailFilterTable,self).__init__(1,6,parent)
		self.resize(100,100)
		self.filters = []
		self.button = QtWidgets.QToolButton()
		self.button.clicked.connect(self.add)
		self.setCellWidget(0,5,self.button)
		self.setProperty('showGrid',False)
		self.setProperty('cornerButtonEnabled',False)
		self.verticalHeader().hide()
		self.setHorizontalHeaderLabels(
			['Label','Criterea','','Value','Inverted','']
		)
		self.horizontalHeader().setSectionsClickable(False)
		self.horizontalHeader().setSectionResizeMode(
			3,QtWidgets.QHeaderView.Stretch
		)
		self.button.setIcon(QtGui.QIcon("icons/list-add.png"))
		self.setSizePolicy(
			QtWidgets.QSizePolicy.MinimumExpanding,
			QtWidgets.QSizePolicy.Minimum
		)
		self.resizeColumnsToContents()
		self.setSelectionMode(QtWidgets.QTableWidget.NoSelection)

	def __len__(self):
		return len(self.filters)

	def remove(self,filter):
		row = self.filters.index(filter)
		self.filters.pop(row)
		self.removeRow(row)
		self.resizeColumnsToContents()
		self.horizontalHeader().setSectionResizeMode(
			3,QtWidgets.QHeaderView.Stretch
		)
		self.tableChanged.emit(len(self.filters))

	def add(self,filter=None):
		length = len(self.filters)
		self.insertRow(length)
		self.setItem(5,length+1,self.takeItem(5,length))
		self.filters.append(filter or EmailFilter(length+1,self))
		i = 0
		for w in self.filters[-1].widgets:
			self.setCellWidget(length,i,w)
			i += 1
		self.resizeColumnsToContents()
		self.horizontalHeader().setSectionResizeMode(
			3,QtWidgets.QHeaderView.Stretch
		)
		self.tableChanged.emit(len(self.filters))

	def getRequest(self,logic=''):
		if len(self.filters) == 0:
			return '', 0, None

		req = ''
		crits = dict(
			[(x.label,(x.getCrit(),x.getValue())) for x in self.filters]
		)
		# ops = []

		if logic == '':
			logic = ' AND '.join(crits.keys())

		logic = EmailFilterLogicValidator.fixup(logic)

		for label in crits:
			inv = crits[label][1][1]
			logic = re.sub(label,'%s %s'%((' NOT' if inv else ''),label),logic)

		
		logic = EmailFilterLogicValidator.fixup(logic)

		# It's been 'fixup'ed so we can expect a certain structure.
		# No symbols, only ors and nots (and labels and p'rens)
		pat = [x for x in re.split('''(?ix)[&|]{1,2}|(?:^|(?<=\ ))and(?=\W)|
									(?:^|(?<=\ ))or(?=\W)|(?<!^not)(?<!\ not)
									(?<!\(not)(?<!\()(?<!!)\ +(?!\))''',logic)\
									if x != '']
		labels = re.findall('(\w+) *(?:\)+)?(?=,|$)',','.join(pat))

		# gotta move ors over
		split = re.split('(?i)(?<!\bnot) +',logic)
		# print(split)
		for i in [x for x in range(len(split)) if split[x].lower() == 'or']:
			op = split.pop(i)
			pren = 0
			j = i
			while (pren > 0 or i == j) and i > 0:
				if ')' in split[i-1]:
					pren += split[i-1].count(')')
				if '(' in split[i-1]:
					pren -= split[i-1].count('(')
				i -= 1
			if pren != 0:
				_ = split[i].split('(',1)
				split[i] = _[1]
				op = '(' + op
			split.insert(i,op)

		# print(split)

		parts = [p for p in\
			re.split('|'.join(['(?:^|(?<= |\())%s(?:$|(?= |\)))' %(x) for x in\
				set(labels)]),' '.join(split)) if p != None and p != '']

		# print(pat)
		# print(labels)
		# print(ops)
		# print(parts)

		# Check if lead
		if len(parts) < len(labels):
			try:
				req += parts.pop(0)
			except:
				pass

		# Stitch together
		# print(crits)
		for x in range(len(labels)):
			if labels[x] not in crits:
				print("bad label in logic")
				return None, 2, labels[x]
			req += parts[x]
			req += ' ' + crits[labels[x]][0] 
			req += ((' ' + crits[labels[x]][1][0])\
					if crits[labels[x]][1][0] != '' else '')

		# Check if lag
		if len(parts) > len(labels):
			req += parts.pop(-1)


		req = EmailFilterLogicValidator.fixup(req)
		req = req.strip()
		# print(req)
		return req, 0, None

	def serialize(self):
		data = ''
		for f in self.filters:
			v = [*f.getValue()]
			if v[0] != '' and v[0][0] == v[0][-1] == '"':
				v[0] = v[0][1:-1]
			data += '%d,%s,"%s",%d,'\
				%(f.crit,f.label,v[0].replace('"','\\"'),v[1])

		return data[:-1]

	def fromSerial(self,data):
		filters = re.findall(r'\d+,\w+,".*?(?<!\\)",(?:0|1)',data)
		filters = [f.split(',') for f in filters]
		for f in filters:
			self.add(EmailFilter(f[1],self,int(f[0]),bool(int(f[3]))))
		for f in range(len(filters)):
			self.filters[f].setValue(filters[f][2][1:-1].replace('\\"','"'))

class EmailFilter():
	_crit = [
		('ANSWERED','bool'),('BCC','string'),('BEFORE','date'),
		('BODY','string'),('CC','string'),('DELETED','bool'),
		('DRAFT','bool'),('FLAGGED','bool'),('FROM','string'),
		('KEYWORD','string'),('LARGER','number'),('NEW','bool'),
		('OLD','bool'),('ON','date'),('RECENT','bool'),
		('SEEN','bool'),('SENTBEFORE','date'),('SENTON','date'),
		('SENTSINCE','date'),('SINCE','date'),('SMALLER','number'),
		('SUBJECT','string'),('TEXT','string'),('TO','string'),
		('UID','string')
	]
	_critNice = [
		'Answered','BCC','Before','Body','CC','Deleted',
		'Draft','Flagged','From','Keyword','Larger','New',
		'Old','On','Recent','Seen','Sent Before','Sent On',
		'Sent Since','Since','Smaller','Subject','Text','To',
		'UID'
	]
	_ops = {
		'string' : ('contains', 0),
		'bool' : ('is', 1),
		'number' : ('than', 2),
		'date' : ('the day of', 3)
	}

	_validator = EmailFilterLabelValidator()

	def __init__(self,label='1',parent=None,crit=None,inverted=False):
		self.crit = -1
		self.op = None
		self.label = str(label)
		self.widgets = [
			QtWidgets.QLineEdit(self.label),
			QtWidgets.QComboBox(),
			QtWidgets.QWidget(),
			QtWidgets.QStackedWidget(),
			QtWidgets.QWidget(),
			QtWidgets.QToolButton()
		] 
		self.widgets[0].setValidator(self._validator)
		self.widgets[1].addItems(self._critNice)
		# String
		self.widgets[3].addWidget(QtWidgets.QLineEdit())
		self.widgets[3].widget(0).textChanged.connect(
			lambda: self.parent.tableChanged.emit(len(self.parent)) \
				if self.parent is not None else ()

		)
		# Bool
		self.widgets[3].addWidget(QtWidgets.QComboBox())
		self.widgets[3].widget(1).addItem('True')
		self.widgets[3].widget(1).addItem('False')
		self.widgets[3].widget(1).currentIndexChanged.connect(
			lambda: self.parent.tableChanged.emit(len(self.parent)) \
				if self.parent is not None else ()
		)
		# Number
		self.widgets[3].addWidget(QtWidgets.QSpinBox())
		self.widgets[3].widget(2).valueChanged.connect(
			lambda: self.parent.tableChanged.emit(len(self.parent)) \
				if self.parent is not None else ()
		)
		# Date
		self.widgets[3].addWidget(QtWidgets.QDateEdit())
		self.widgets[3].widget(3).setCalendarPopup(True)
		self.widgets[3].widget(3).setDate(QtCore.QDate.currentDate())
		self.widgets[3].widget(3).dateChanged.connect(
			lambda: self.parent.tableChanged.emit(len(self.parent)) \
				if self.parent is not None else ()
		)

		self.inverted = inverted
		self.parent = parent

		self.widgets[0].textChanged.connect(self.updateLabel)
		self.widgets[1].currentIndexChanged.connect(self.changeCrit)
		self.widgets[5].clicked.connect(self.remove)
		self.widgets[5].setIcon(QtGui.QIcon("icons/list-remove.png"))
		l = QtWidgets.QHBoxLayout(self.widgets[2])
		l.setAlignment(QtCore.Qt.AlignCenter)
		lbl = QtWidgets.QLabel('is')
		l.addWidget(lbl)
		self.widgets[2].setLayout(l)
		self.widgets[2].setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
									  QtWidgets.QSizePolicy.Expanding
		)
		self.labelWidget = lbl

		l = QtWidgets.QHBoxLayout(self.widgets[4])
		l.setAlignment(QtCore.Qt.AlignCenter)
		chk = QtWidgets.QCheckBox()
		chk.stateChanged.connect(lambda x : self.invert(x>0))
		l.addWidget(chk)
		self.widgets[4].setLayout(l)
		self.widgets[4].setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
									  QtWidgets.QSizePolicy.Expanding
		)
		self.checkWidget = chk

		self.changeCrit(crit or 0)
		self.updateLabel()

	def remove(self):
		if not self.parent: return;

		self.parent.remove(self)

	def updateLabel(self):
		_ = self.label
		self.label = self.widgets[0].text()
		if self.label == '':
			self.label = _
		self.checkWidget.setChecked(self.inverted)
		if self.parent:
			self.parent.tableChanged.emit(len(self.parent))

	def changeCrit(self,i):
		if i < 0: return;

		self.op = self._crit[i][1]
		op = self._ops[self.op]

		self.crit = i
		self.labelWidget.setText(op[0])
		self.widgets[1].setCurrentIndex(i)
		self.widgets[3].setCurrentIndex(op[1])
		if self.parent:
			self.parent.tableChanged.emit(len(self.parent))

	def getCrit(self):
		return self._crit[self.crit][0]

	def getValue(self):
		if self.op == 'string' :
			return ('"' + self.widgets[3].widget(0).text().replace('"','\\"')
					+ '"'), self.inverted
		elif self.op == 'bool' :
			return '',\
				self.inverted if self.widgets[3].widget(1).currentText() \
					== 'True' else not self.inverted
		elif self.op == 'number' :
			return self.widgets[3].widget(2).text(), self.inverted
		elif self.op == 'date' :
			return self.widgets[3].widget(3).date().toString("d-MMM-yyyy"),\
				self.inverted

	def setValue(self,v):
		if self.op == 'string' :
			self.widgets[3].widget(0).setText(v)
		# elif self.op == 'bool' :
		# 	self.widgets[3].widget(1).setIndex(abs(v-1))
		elif self.op == 'number' :
			self.widgets[3].widget(2).setValue(int(v))
		elif self.op == 'date' :
			self.widgets[3].widget(3).setDate(
				QtCore.QDate.fromString(v,"d-MMM-yyyy")
			)
		if self.parent:
			self.parent.tableChanged.emit(len(self.parent))

	def invert(self,value=None):
		self.inverted = value if value != None else (not self.inverted)
		if self.parent:
			self.parent.tableChanged.emit(len(self.parent))