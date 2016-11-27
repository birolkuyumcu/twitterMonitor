# -*- coding: utf-8 -*-
#
# Twitter Gözetleyici
# Programmed by : Birol Kuyumcu ( bluekid70@gmail.com )
#				: https://tr.linkedin.com/in/birol-kuyumcu-53798771
# License : GPL
# Requirements :
#   PySide : https://github.com/PySide
#   wordcloud : https://github.com/amueller/word_cloud
#   pattern : http://www.cnts.ua.ac.be/pattern

import sys

from PySide import QtCore, QtGui, QtWebKit
from pattern.web import Twitter, plaintext, hashtags
from wordcloud import WordCloud
import re
import numpy as np
import os
import webbrowser


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(823, 677)
        self.label = QtGui.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 10, 800, 400))
        self.label.setFrameShape(QtGui.QFrame.WinPanel)
        self.label.setText("")
        self.label.setObjectName("label")
        self.listWidget = QtGui.QListWidget(Dialog)
        self.listWidget.setGeometry(QtCore.QRect(10, 470, 801, 192))
        self.listWidget.setObjectName("listWidget")
        self.widget = QtGui.QWidget(Dialog)
        self.widget.setGeometry(QtCore.QRect(10, 429, 801, 25))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtGui.QLabel(self.widget)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.lineEdit = QtGui.QLineEdit(self.widget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.pushButton = QtGui.QPushButton(self.widget)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)
        #
        self.pushButton.clicked.connect(self.on_buttom_pressed)
        self.listWidget.doubleClicked.connect(self.goTweet)

        #
        self.alText = u''
        self.fullText = u''
        self.twitter = Twitter(language='tr')
        self.prevId = None
        self.timer = QtCore.QTimer(Dialog)
        self.timer.timeout.connect(self.on_timer)
        self.dialog = Dialog
        self.twIds = []


    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "Twitter Gözetleyici", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Dialog", "Anahtar Kelime :", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton.setText(QtGui.QApplication.translate("Dialog", "Gözetle", None, QtGui.QApplication.UnicodeUTF8))
    #
    def on_buttom_pressed(self):
        if self.timer.isActive() :
            self.timer.stop()
            self.pushButton.setText(u'Gözetle')
        else:
            self.listWidget.clear()
            self.twIds = []
            self.fullText = u''
            self.on_timer()
            self.timer.start(60000)
            self.pushButton.setText('Durdur !')

        return

    def on_timer(self):
        searchKey = self.lineEdit.text()
        self.getTwits(searchKey)
        self.filterWords()
        self.fullText = self.fullText + self.alText
        self.showWordCloud()


    def showWordCloud(self):
        wordcloud = WordCloud(width=800, height=400).generate(self.fullText)
        img = np.array(wordcloud.to_image())
        height, width, byteValue = img.shape
        byteValue = byteValue * width
        image = QtGui.QImage(img.data, width, height, byteValue, QtGui.QImage.Format_RGB888)
        pxmp = QtGui.QPixmap(image)
        self.label.setPixmap(pxmp)

    def filterWords(self):
        # sık geçen kelimeler filitreleniyor eksik elbette....
        flt = [u'https', u'nin', u'bir', u'daha', u'diye', u'için', u'gibi', u'işte', u'ile', u'değil', u'ben', u'sen',
               u'çok', u'ama', u'Sen',u'den',u'htt']
        derle = re.compile("\w*", re.UNICODE)
        wL = re.findall(derle, self.alText)
        temp = []
        for w in wL:
            if len(w) < 3:
                continue
            elif w in flt:
                continue
            else:
                #print w
                temp.append(w)
        self.alText = ' '.join(temp)

    def getTwits(self,keyWord):
        if len(keyWord) == 0:
            keyWord =u'"gündem"'
            self.lineEdit.setText(keyWord)
        self.alText = u''
        try :
            tList = self.twitter.search(keyWord, start=self.prevId, count=10, cached=False)

        except:
            message = "Twitter Aram Limiti Lütfen Biraz Bekleyin"
            QtGui.QMessageBox.information(self.dialog, "Information", "Python rocks!")

        for tweet in tList:
            self.listWidget.addItem(QtGui.QListWidgetItem(tweet.text))
            self.twIds.append(tweet.id)
            self.listWidget.setCurrentRow(self.listWidget.count()-1)
            tweet.text = self.filterRT(tweet.text)
            tweet.text = self.filterLink(tweet.text)
            self.alText = self.alText + plaintext(tweet.text) + u' '
            self.prevId = tweet.id

    def filterRT(self,tweet):
        # RT başlığı filtreleniyor
        buf = tweet[:2]
        if buf == u'RT':
            ix = tweet.find(':')
            tweet = tweet[ix:]
        return tweet

    def filterLink(self,tweet):
        regex = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        match = re.search(regex, tweet)
        buf = tweet
        if match:
            ixs= tweet.find(match.group())
            ixe= len(match.group())
            try:
                buf = tweet[:ixs]
            except:
                print "not removed"
        return buf

    def goTweet(self):
        i = self.listWidget.currentRow()
        urlTw = 'https:/'+'/twitter.com/statuses/'+ str(self.twIds[i])
        webbrowser.open(urlTw)

# Create the Qt Application
app = QtGui.QApplication(sys.argv)
# Create and show the form
form = Ui_Dialog()
Dialog = QtGui.QDialog()
form.setupUi(Dialog)
Dialog.show()
# Run the main Qt loop
sys.exit(app.exec_())
