# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'timecontextwidget.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TimeContextWidget(object):
	def setupUi(self, TimeContextWidget):
		TimeContextWidget.setObjectName("TimeContextWidget")
		TimeContextWidget.resize(379, 27)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
		sizePolicy.setHorizontalStretch(0)
		sizePolicy.setVerticalStretch(0)
		sizePolicy.setHeightForWidth(TimeContextWidget.sizePolicy().hasHeightForWidth())
		TimeContextWidget.setSizePolicy(sizePolicy)
		self.horizontalLayout = QtWidgets.QHBoxLayout(TimeContextWidget)
		self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinimumSize)
		self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
		self.horizontalLayout.setSpacing(0)
		self.horizontalLayout.setObjectName("horizontalLayout")
		self.checkBegin = QtWidgets.QCheckBox(TimeContextWidget)
		self.checkBegin.setObjectName("checkBegin")
		self.horizontalLayout.addWidget(self.checkBegin)
		self.timeBegin = QtWidgets.QTimeEdit(TimeContextWidget)
		self.timeBegin.setCalendarPopup(False)
		self.timeBegin.setObjectName("timeBegin")
		self.horizontalLayout.addWidget(self.timeBegin)
		self.checkEnd = QtWidgets.QCheckBox(TimeContextWidget)
		self.checkEnd.setObjectName("checkEnd")
		self.horizontalLayout.addWidget(self.checkEnd)
		self.timeEnd = QtWidgets.QTimeEdit(TimeContextWidget)
		self.timeEnd.setCalendarPopup(False)
		self.timeEnd.setObjectName("timeEnd")
		self.horizontalLayout.addWidget(self.timeEnd)

		self.retranslateUi(TimeContextWidget)
		QtCore.QMetaObject.connectSlotsByName(TimeContextWidget)

	def retranslateUi(self, TimeContextWidget):
		_translate = QtCore.QCoreApplication.translate
		self.checkBegin.setText(_translate("TimeContextWidget", "Starting Time"))
		self.checkEnd.setText(_translate("TimeContextWidget", "Finishing Time"))

