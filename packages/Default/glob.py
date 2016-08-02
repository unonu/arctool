''' HEY DON'T USE DISCONNECTED GLOBS UNTIL I FIGURE OUT HOW TO ACCOUNT
FOR THEM IN THE GLOBITEM OKAYTHANKSBYE
'''

from PyQt5.QtGui import QTextCursor
from math import sqrt, ceil

class Glob(object):
	def __init__(self,*curs):
		self.val = '' # Actual text
		self.sta = [] # [Start location, start location %]
		self.end = [] # [eEd location, end location %]
		self.gap = [] # [(gGp start, gap end),...]
		self.cla = 0 # 'Line','paragraph','list'
		self.sub = 0 # 'Short','medium','long'
		self.cov = 0.0
		self.wc = 1	# Word count
		self.lc = 1	# Line count
		self.dev = 0.0	# Deviation (stdev/mean)
		self.num = '0'*12 # Unique number, independant of text. 96 bits
		if len(curs) > 0:
			self.setValue(*curs)

	def __str__(self):
		return self.num

	def __lt__(self,a):
		return a.num > self.num

	@staticmethod
	def fromNum(num,val=''):
		g = Glob()

		g.val = val

		g.sta[0] = int(num[:4],16)

		g.end[0] = int(num[4:8],16)

		g.sta[1] = int(num[8:11],16) >> 2
		g.sta[1]/= 1000.

		g.end[1] = int(num[10:13],16) & 0x3ff
		g.end[1]/= 1000.

		g.cla = int(num[13],16) >> 2

		g.sub = int(num[13],16) & 0xc

		g.cov = int(num[14:17],16) >> 2
		g.cov /= 1000.

		g.wc = int(num[16:19],16) & 0x3ff

		g.lc = int(num[19:22],16) & 0xffc

		g.dev = int(num[21:],16) & 0x3ff
		g.dev /= 1000.

		g.calc()
		if g.num != num:
			print("messed up")
			return None

		return g

	def calc(self):
		# 96 bits:
		# 16  16  10  10   2   2  10  10  10  10
		#sta end sta end cla sub cov  wc  lc dev

		# Each of these is 16 bits
		a = (self.sta[0] & 65535)

		b = (self.end[0] & 65535)

		c = (int(self.sta[1]*1000) & 0x3ff) << 6
		c |= (int(self.end[1]*1000) & 0x3ff) >> 4

		d = (int(self.end[1]*1000) & 0xf) << 12
		d |= (self.cla & 3) << 10
		d |= (self.sub & 3) << 8
		d |= (int(self.cov*1000) & 0x3ff) >> 2 

		e = (int(self.cov*1000) & 0x3) << 14
		e |= (self.wc & 0x3ff) << 4
		e |= (self.lc & 0x3ff) >> 6

		f = (self.lc & 0x3f) << 10
		f |= (int(self.dev*1000) & 0x3ff)

		byt = bytearray(12)
		byt[0] = a >> 8
		byt[1] = a & 0xff
		byt[2] = b >> 8
		byt[3] = b & 0xff
		byt[4] = c >> 8
		byt[5] = c & 0xff
		byt[6] = d >> 8
		byt[7] = d & 0xff
		byt[8] = e >> 8
		byt[9] = e & 0xff
		byt[10] = f >> 8
		byt[11] = f & 0xff

		self.num = byt.hex().rjust(24,'0')

		return self.num

	def setValue(self,*curs):
		doc = curs[0].document()

		self.val = ''.join(c.selectedText() for c in curs).strip()
		if self.val == '':
			print('Empty glob')
			return

		spl = self.val.splitlines()
		self.sta = [curs[0].selectionStart(),
					curs[0].selectionStart()/doc.characterCount()]
		self.end = [curs[-1].selectionEnd(),
					curs[-1].selectionEnd()/doc.characterCount()]
		self.gap = [(c.selectionStart(),c.selectionEnd()) for c in curs]
		self.cla = 0 if (len(spl) == 0 and
						 len(self.val) <= doc.idealWidth() and
						 len(curs) == 1) else -1
		if self.cla < 0:
			self.cla = 1 if (len(self.val) > doc.idealWidth() and
							'' not in spl) else 2

		if self.cla == 0:
			l = len(self.val)/doc.idealWidth()
			self.cla = 0 if l < .25 else 1 if l < .66 else 2
		elif self.cla == 1:
			l = len(self.val)/doc.characterCount()
			self.cla = 0 if l < .25 else 1 if l < .66 else 2
		elif self.cla == 2:
			l = len(spl)/doc.lineCount()
			self.cla = 0 if l < .25 else 1 if l < .66 else 2

		self.cov = len(self.val)/doc.characterCount()
		self.wc  = len(self.val.split())
		self.lc  = len(spl)

		# split the words
		spl = self.val.split()
		# store their lengths
		les = [len(s) for s in spl]
		# get the occurances of each length
		cou = dict((les.count(l),l) for l in set(les))

		# mean of the lengths
		mea = sum(les)/len(les)
		var = sum((x-mea)**2 for x in les)/len(les)
		# stdev of the lengths from the mean
		dev = sqrt(var)
		
		# find the mode of 'les'
		mod = cou[max(cou)]
		# likelihood any lenth won't be the mode
		dif = (len(spl) - max(cou)) / len(spl)

		# figure out how to incorporate the dif
		self.dev = dev/mea

		return self.calc()

class GlobItem():
	def __init__(self):
		self.globs = []
		self.common = [] # common words
		self.sta = [[0,0],[0,0]] # start position
		self.end = [[0,0],[0,0]] # end position
		self.cla = 0 # class
		self.sub = 0 # subclass
		self.cov = (0.0,0.0) # coverage %
		self.wc  = (0,0) # word count
		self.lc  = (0,0) # line count
		self.dev = (0.0,0.0) # stdev
		self.gev = (0.0,0.0) # glob deviance
		self.dsi = (0,0) # extrapolated doc size in words

	def append(self,g):
		return self.__add__(g)

	def findCommon(self,gperc=.6,clen=3):
		ocu = {}
		for c in [g.val for g in self.globs if g.val != '']:
			for w in c.split():
				w = w.strip(' \n\r\t!?.()')
				if w == '': continue

				ocu[w] = ocu[w] + 1 if w in ocu else 1

		self.common = [
			ocu[w] for w in ocu if (ocu[w] >= gperc*len(self.globs) and
				len(w) >= clen)
		]

		return self.common

	def __add__(self,g):
		if type(g) != Glob: return

		self.globs.append(g)

		# These properties are the same as a single glob, just (mean,stdev)
		# Note the temprary type switch
		self.sta[0] = sum(g.sta[0] for g in self.globs)//len(self.globs)
		self.sta[0] = [ self.sta[0],
						int(sqrt(sum((g.sta[0]-self.sta[0])**2 for g in \
							self.globs)/len(self.globs)))]
		self.sta[1] = sum(g.sta[1] for g in self.globs)/len(self.globs)
		self.sta[1] = [ self.sta[1],
						int(sqrt(sum((g.sta[1]-self.sta[1])**2 for g in \
							self.globs)/len(self.globs)))]
		self.end[0] = sum(g.end[0] for g in self.globs)//len(self.globs)
		self.end[0] = [ self.end[0],
						int(sqrt(sum((g.end[0]-self.end[0])**2 for g in \
							self.globs)/len(self.globs)))]
		self.end[1] = sum(g.end[1] for g in self.globs)/len(self.globs)
		self.end[1] = [ self.end[1],
						int(sqrt(sum((g.end[1]-self.end[1])**2 for g in \
							self.globs)/len(self.globs)))]

		cou = ( sum( 1 for g in self.globs if g.cla == 0),
				sum( 1 for g in self.globs if g.cla == 1),
				sum( 1 for g in self.globs if g.cla == 2))
		self.cla = cou.index(max(cou))

		cou = ( sum( 1 for g in self.globs if g.sub == 0),
				sum( 1 for g in self.globs if g.sub == 1),
				sum( 1 for g in self.globs if g.sub == 2))
		self.sub = cou.index(max(cou))

		self.cov = sum(g.cov for g in self.globs)/len(self.globs)
		self.cov = (self.cov,sqrt(
			sum((g.cov-self.cov)**2 for g in self.globs)/len(self.globs)))
		self.wc = max(1,round(sum(g.wc for g in self.globs)/len(self.globs)))
		self.wc = (self.wc,ceil(sqrt(
			sum((g.wc-self.wc)**2 for g in self.globs)/len(self.globs))))
		self.lc = max(1,round(sum(g.lc for g in self.globs)/len(self.globs)))
		self.lc = (self.lc,ceil(sqrt(
			sum((g.lc-self.lc)**2 for g in self.globs)/len(self.globs))))

		self.dev = sum(g.dev for g in self.globs)/len(self.globs)
		self.dev = (self.dev,sqrt(
			sum((g.dev-self.dev)**2 for g in self.globs)/len(self.globs)))

		self.dsi = self.wc[0]/self.cov[0]

		return len(self.globs)

	def getText(self,doc,threshold=.3):
		cur = QTextCursor(doc)
		cer = 0.0 # certainty
		cha = doc.characterCount()

		# for gaps ...
		# This isn't using the stdev of the percentage
		# Also, I /could/ check if sta/end is within bounds, but it only errors
		sta = self.sta[1][0]*cha # get start relative to this doc
		if (sta >= self.sta[0][0]-self.sta[0][1] and
			sta <= self.sta[0][0]+self.sta[0][1]):
			cur.setPosition(sta) # use relative if within expectations
			cer += .1
		else:
			# use hard start. doesn't boost confidence
			cur.setPosition(self.sta[0][0])
		inb = cur.blockNumber() # cursor's starting block
		cur.movePosition(cur.StartOfWord)

		end = self.end[1][0]*cha
		if (end >= self.end[0][0]-self.end[0][1] and
			end <= self.end[0][0]+self.end[0][1]):
			cur.setPosition(end,cur.KeepAnchor)
			cer += .1
		else:
			cur.setPosition(self.end[0][0],cur.KeepAnchor)
		cur.movePosition(cur.EndOfWord,cur.KeepAnchor)

		# Match word count based on line sub classification
		if self.cla == 0:
			# print("I'm a line")
			if self.sub == 0:
				# print("I'm a short line")
				while cur.blockNumber() > inb:
					cur.movePosition(cur.PreviousBlock,cur.KeepAnchor)
					cur.movePosition(cur.EndOfBlock,cur.KeepAnchor)
					# print('b2',cur.selectedText(),cur.blockNumber(), inb, self.wc)
				while len(cur.selectedText().split()) < self.wc[0]-self.wc[1]:
					cur.movePosition(cur.NextWord,cur.KeepAnchor)
					cur.movePosition(cur.EndOfWord,cur.KeepAnchor)
					# print('a')
				while len(cur.selectedText().split()) > self.wc[0]+self.wc[1]:
					cur.movePosition(cur.PreviousWord,cur.KeepAnchor)
					cur.movePosition(cur.EndOfWord,cur.KeepAnchor)
					# print('b',cur.selectedText(),cur.blockNumber(), inb, self.wc)
			elif self.sub == 2:
				# print("I'm a long line")
				if cur.blockNumber() > inb:
					cur.movePosition(cur.PreviousBlock,cur.KeepAnchor)
				cur.movePosition(cur.EndOfBlock,cur.KeepAnchor)
		elif self.cla == 1:
			# print("I'm a paragraph")
			while cur.blockNumber() - inb < self.lc[0] - self.lc[1]:
				cur.movePosition(cur.NextBlock,cur.KeepAnchor)
				cur.movePosition(cur.EndOfBlock,cur.KeepAnchor)
				# print('c')
			while cur.blockNumber() - inb > self.lc[0] + self.lc[1]:
				cur.movePosition(cur.PreviousBlock,cur.KeepAnchor)
				cur.movePosition(cur.EndOfBlock,cur.KeepAnchor)
				# print('d')

		text = cur.selectedText() # go ahead and grab the text

		# check coverage, word count, line count and deviation, etc. for more confidence
		cov = len(text)/cha
		wc = len(text.split())
		lc = len(text.splitlines())
		if cur.selectionStart() <= cha*(1-self.cov[0]):
			cer += .1 # boost confidence if there are enough characters for a match, probably
		if cur.selectionEnd() <= cha*(1-self.cov[0]):
			cer += .1
		# print(cha,(sta/cha)-self.sta[1][0],self.sta[1][0])
		# adjust for how close the relative start was
		cer += (.05 / max(1,abs((sta/cha)-self.sta[1][0])
				/ zerocheck(self.sta[1][1], self.sta[1][0] )))
		cer += (.05 / max(1,abs((end/cha)-self.end[1][0])
				/ zerocheck(self.end[1][1], self.end[1][0] )))
		# coverage
		cer += (.12 / max(1,abs(cov-self.cov[0])
				/ zerocheck(self.cov[1], self.cov[0] )))
		# word count
		cer += (.12 / max(1,abs(wc-self.wc[0])
				/ zerocheck(self.wc[1], self.wc[0] )))
		# print(self.lc[0], self.lc[1],lc)
		# line count
		cer += (.08 / max(1,abs(lc-self.lc[0])
				/ zerocheck(self.lc[1], self.lc[0] )))
		cer += .08 # stdev of word lenth
		self.findCommon()
		for w in text.split(): # common words
			if w in self.common:
				cer += .1/wc

		return text, cer > threshold, cer

def zerocheck(i,rep=1):
	return (1 if rep == 0 else rep) if i == 0 else i