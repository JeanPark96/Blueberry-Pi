#!/usr/bin/python
# -*- coding: utf-8 -*-
# Adapted from www.linuxuser.co.uk/tutorials/emulate-a-bluetooth-keyboard-with-the-raspberry-pi
# Applied YAPTB Bluetooth keyboard emulation service to PyQt5
#
# Lubomir Rintel <lkundrak@v3.sk>
# License: GPL
#
# Ported to a Python module by Liam Fraser.
#
# Adpated from https://github.com/mlabviet/BL_keyboard_RPI/
#
import sys

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot  
from functools import *

import os #used to all external commands
import sys # used to exit the script
import dbus
import dbus.service
import dbus.mainloop.glib
import time
import keymap 

import database

def switch(value):
    return {
        'i1' : '<',
        'i2' : '>',
        'number_1' :'1',
        'number_2' :'2',
        'number_3' :'3',
        'number_4' :'4',
        'number_5' :'5',
        'number_6' :'6',
        'number_7' :'7',
        'number_8' :'8',
        'number_9' :'9',
        'number_0' :'0',
        'left' : '←',
        'right' : '→',
        'up' : '↑',
        'down' : '↓',
        'dot' : '.',
        'comma' : ',',
        'backspace' : 'Backs',
        'capslock' : 'caps'
    }.get(value, 'default')

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):

        # selected_keys: 현재 추가하려는 button에 지정하려고 하는 key들을 저장
        # defined_buttons: 단축키로 지정된 button을 저장
        # all_buttons: 전제 key 저장
        # undefined_buttons: 아직 단축키로 지정되지 않은 button을 저장
        # toggled_keys: 현재 눌려있는 key들 저장

        global selected_keys , defined_buttons, all_buttons, undefined_buttons, toggled_keys, keys
        self.numButton = 0
        self.pageNum = 1
        self.maxPage = 2
        all_buttons = []

        # MainWindow & stacked Widget 생성
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 415)
        MainWindow.setFixedSize(800,415)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # stackwidget 생성
        self.keywindow = QtWidgets.QStackedWidget(self.centralwidget)
        self.keywindow.setGeometry(QtCore.QRect(0, 40, 800, 340))
        self.keywindow.setFrameShape(QtWidgets.QFrame.Panel)
        self.keywindow.setFrameShadow(QtWidgets.QFrame.Raised)
        self.keywindow.setObjectName("keywindow")
        self.keywindow.setStyleSheet("background-color:skyblue")

        self.makeStartWindow()  # page index=0: start window
        self.makeAddKeyWindow() # page index=1: Add key window

        self.insertPageButton = QtWidgets.QPushButton('New Page', self.centralwidget)
        self.insertPageButton.setGeometry(QtCore.QRect(400, 0, 100, 31))
        self.insertPageButton.setObjectName("insertButton")
        self.insertPageButton.clicked.connect(self.insertPages)

        self.deletePageButton = QtWidgets.QPushButton('Delete Page', self.centralwidget)
        self.deletePageButton.setGeometry(QtCore.QRect(500, 0, 100, 31))
        self.deletePageButton.setObjectName("deleteButton")
        self.deletePageButton.clicked.connect(self.deletePages)

        self.makeKeyWindows()   # page index = 2, Key Window 1
        self.makeKeyWindows()   # page index = 3, Key Window 2
        self.makeKeyWindows()   # page index = 4, Key Window 3
        self.makeKeyWindows()   # page index = 5, Key Window 4
        self.makeKeyWindows()   # page index = 6, Key Window 5

        database.startDatabase()
        self.maxPage=int(database.setDatabase('0'))
        ##
        defined_buttons = []
        undefined_buttons = []
        for button in all_buttons:        
            objectLabel = database.setDatabase(button.objectName())
            if objectLabel != 0:
                defined_buttons.append(button)
            else:
                undefined_buttons.append(button)

        # page 이동용 button
        self.pageButton = []
        for i in range(1,6):
            self.btn = QPushButton('{}'.format(i), MainWindow)
            self.btn.setGeometry(QtCore.QRect(50*i,380,40,40))
            self.btn.clicked.connect(partial(self.goto_keywindow,i+1))
            self.pageButton.append(self.btn)
            if (i>self.maxPage):
                self.btn.setEnabled(False)
        
        self.windowlabel = QLabel("START WINDOW", MainWindow)
        self.windowlabel.setGeometry(QtCore.QRect(300, 380, 131, 31))
        self.previous = QtWidgets.QPushButton(MainWindow)
        self.previous.setGeometry(QtCore.QRect(120, 5, 100, 35))
        self.previous.setObjectName("previous")
        self.previous.setText("<")
        self.next = QtWidgets.QPushButton(MainWindow)
        self.next.setGeometry(QtCore.QRect(280, 5, 100, 35))
        self.next.setObjectName("next")
        self.next.setText(">")
        self.next.setEnabled(False)
        self.previous.setEnabled(False)
        self.previous.clicked.connect(self.goto_previouswindow)
        self.next.clicked.connect(self.goto_nextwindow)
        
        self.disable_keys = QtWidgets.QCheckBox(self.centralwidget)
        self.disable_keys.setGeometry(QtCore.QRect(10, 10, 100, 26))
        self.disable_keys.setObjectName("disable_keys")
        MainWindow.setCentralWidget(self.centralwidget)

        # button list
        selected_keys = []
        toggled_keys = []
        keys = [self.F1,
                self.F2,
                self.F3,
                self.F4,
                self.F5,
                self.F5,
                self.F6,
                self.F7,
                self.F8,
                self.F9,
                self.F10,
                self.F11,
                self.F12,
                self.number_1,
                self.number_2,
                self.number_3,
                self.number_4,
                self.number_5,
                self.number_6,
                self.number_7,
                self.number_8,
                self.number_9,
                self.number_0,
                self.a,
                self.b,
                self.c,
                self.d,
                self.e,
                self.f,
                self.g,
                self.h,
                self.i,
                self.j,
                self.k,
                self.l,
                self.m,
                self.n,
                self.o,
                self.p,
                self.q,
                self.r,
                self.s,
                self.t,
                self.u,
                self.v,
                self.w,
                self.x,
                self.y,
                self.z,
                self.esc,
                self.capslock,
                self.backspace,
                self.enter,
                self.shift,
                self.ctrl,
                self.alt,
                self.space,
                self.dot,
                self.comma,
                self.left,
                self.right,
                self.up,
                self.down,
                self.i1,
                self.i2]
        
        for key in keys:
            toggled_keyname = key.objectName()
            a = switch(toggled_keyname)
            if (a == 'default'):
                key.setText(toggled_keyname)
            else:
                key.setText(a)
            key.setCheckable(True)
            key.clicked.connect(partial(self.midkey_tolistWidget, key))
        
        self.retranslateUi(MainWindow)
        self.keywindow.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        #slot connection
        self.startbutton.clicked.connect(partial(self.goto_keywindow, 2))
        self.exitButton.clicked.connect(self.exit_addkeywindow)
        self.keyAddButton.clicked.connect(self.add_shortcut)
        self.disable_keys.stateChanged.connect(self.disable_Keys)
        self.deleteButton.clicked.connect(self.add_shortcut)
    
    #selected keys, list widget, line edit, toggled keys reset
    def reset_elements(self):
        selected_keys.clear()
        self.listWidget.clear()
        self.lineEdit.setText("")
        
        for button in toggled_keys:
            button.setChecked(False)
            
    # key 사용하는 페이지로 바로 이동하는 slot
    def goto_keywindow(self, page):
        if page==2:
            self.next.setEnabled(True)
            self.previous.setEnabled(True)
        self.keywindow.setCurrentIndex(page)
        self.windowlabel.setText("KEY WINDOW {}".format(self.keywindow.currentIndex()-1))

    # 이전 페이지로 이동하는 slot (시작화면 제외)
    def goto_previouswindow(self):
        if self.keywindow.currentIndex() != 2:
            self.keywindow.setCurrentIndex(self.keywindow.currentIndex()-1)
            self.windowlabel.setText("KEY WINDOW {}".format(self.keywindow.currentIndex()-1))


    # 다음 페이지로 이동하는 slot
    def goto_nextwindow(self):
        if self.keywindow.currentIndex() < self.maxPage+1:
            self.keywindow.setCurrentIndex(self.keywindow.currentIndex()+1)
            self.windowlabel.setText("KEY WINDOW {}".format(self.keywindow.currentIndex()-1))


    # key를 추가하는 화면으로 이동하는 slot
    def goto_addkeywindow(self, button_a):
        global previous_i, key # key: 작업중인 button
        key = button_a
        self.windowlabel.setText("Add Key Window")
        previous_i = self.keywindow.currentIndex()
        self.keywindow.setCurrentIndex(1)

    # key 추가하는 화면 exit (이전 화면으로 돌아간다)
    def exit_addkeywindow(self):
        self.reset_elements()
        self.keywindow.setCurrentIndex(previous_i)
        self.windowlabel.setText("KEY WINDOW {}".format(self.keywindow.currentIndex()-1))

    # add key window에서 키보드를 눌렀다 뗐다 했을 때 할 수 있는 slot
    def midkey_tolistWidget(self, button):
        toggled_keyname = button.objectName()
        a = switch(toggled_keyname)

        # a: object name을 사용자가 알기 쉬운 형태로 저장할 수 없는 경우
        # switch 문을 통해 사용자가 알기 쉬운 형태(키보드에 나타나있는 형태)로
        # 변환시켜 저장해준다.

        # button을 누를 때
        if button.isChecked():
            if (a == 'default'):
                self.listWidget.addItem(toggled_keyname)
                selected_keys.append(toggled_keyname)
            else:
                self.listWidget.addItem(a)
                selected_keys.append(a)
            toggled_keys.append(button)

        # 눌려있던 button을 해제했을 때
        else:
            index = 0
            while(index<self.listWidget.count()):
                if a == selected_keys[index]:
                    self.listWidget.takeItem(index)
                    selected_keys.remove(a)
                    break
                elif toggled_keyname == selected_keys[index]:
                    self.listWidget.takeItem(index)
                    selected_keys.remove(toggled_keyname)
                    break
                else:
                    index = index + 1
            toggled_keys.remove(button)
            
    # button에 단축키를 추가하는 add button에 연결된 slot
    def add_shortcut(self):
        buttonName = self.lineEdit.text()
        
        delete=False
        #Database
        if database.storageDatabase(selected_keys, buttonName, key.objectName()) == 1:
            key.setText('+')
            delete=True
        else:
            key.setText(buttonName)

        flag = True
        for button in defined_buttons:
            if (key == button):
                flag = False
                break

        if flag:
            defined_buttons.append(key)
            undefined_buttons.remove(key)
        if delete:
            defined_buttons.remove(key)
            undefined_buttons.append(key)
        
        self.exit_addkeywindow()
        
    # undefined key들 disable
    def disable_Keys(self):
        kb = Keyboard()
        if self.disable_keys.isChecked():
            for button in undefined_buttons:
                button.setEnabled(False)
            for button in all_buttons:
                button.disconnect()
                button.pressed.connect(partial(kb.event_loop,button,1))
                button.released.connect(partial(kb.event_loop,button,0))
            self.insertPageButton.setEnabled(False)
                
        else:
            for button in undefined_buttons:
                button.setEnabled(True)
            for button in all_buttons:
                button.disconnect()
                button.clicked.connect(partial(self.goto_addkeywindow, button))
            self.insertPageButton.setEnabled(True)

    def insertPages(self):
        if self.maxPage < 5:
            self.maxPage = self.maxPage+1
            database.storageDatabase('0', str(self.maxPage), '0')
            self.pageButton[self.maxPage-1].setEnabled(True)

    def deletePages(self):
        if self.maxPage > 1:
            self.maxPage = self.maxPage-1
            database.storageDatabase('0', str(self.maxPage), '0')
            self.pageButton[self.maxPage-1].setEnabled(False)
  
    def makeKeyWindows(self):
        self.page = QtWidgets.QWidget()
        self.page.setObjectName('page_{}'.format(self.pageNum))
        for i in range(8):
            #self.label = QLabel('KEY WINDOW {}'.format(self.pageNum), self.page)
            #self.label.setGeometry(QtCore.QRect(160, 10, 131, 31))
            self.btn = QPushButton('pushButton_{}'.format(self.numButton+1), self.page)            
            self.btn.setGeometry(QtCore.QRect(70+180*(i%4),50+150*(i//4), 120, 100))
            self.btn.clicked.connect(partial(self.goto_addkeywindow,self.btn))
            font = QtGui.QFont()
            font.setPointSize(9)
            #self.previous = QtWidgets.QPushButton(self.page)
            #self.previous.setGeometry(QtCore.QRect(120, 10, 31, 31))
            #self.previous.setObjectName("previous")
            #self.previous.setText("<")
            #self.next = QtWidgets.QPushButton(self.page)
            #self.next.setGeometry(QtCore.QRect(280, 10, 31, 31))
            #self.next.setObjectName("next")
            #self.next.setText(">")
            #self.previous.clicked.connect(self.goto_previouswindow)
            #self.next.clicked.connect(self.goto_nextwindow)
            self.btn.setObjectName(self.btn.text())
            all_buttons.append(self.btn)
            self.numButton=self.numButton+1
        self.pageNum=self.pageNum+1
        self.keywindow.addWidget(self.page)

    def makeStartWindow(self):
        self.main_page = QtWidgets.QWidget()
        self.main_page.setObjectName("main_page")
        self.main_blueberrypi = QLabel(self.main_page)
        self.main_blueberrypi.setGeometry(QtCore.QRect(60, 20, 350, 21))
        self.main_blueberrypi.setText("BLUEBERRY PI CUSTOM KEYBOARD")
        font = QtGui.QFont()
        font.setPointSize(14)
        self.main_blueberrypi.setFont(font)
        self.main_blueberrypi.setAlignment(QtCore.Qt.AlignCenter)
        self.main_blueberrypi.setObjectName("main_blueberrypi")
        self.image_blueberrypi = QtWidgets.QLabel(self.main_page)
        self.image_blueberrypi.setGeometry(QtCore.QRect(100, -60, 241, 411))
        self.image_blueberrypi.setText("")
        self.image_blueberrypi.setPixmap(QtGui.QPixmap("../Downloads/preview.png"))
        self.image_blueberrypi.setScaledContents(True)
        self.image_blueberrypi.setObjectName("image_blueberrypi")
        self.startbutton = QtWidgets.QPushButton(self.main_page)
        self.startbutton.setGeometry(QtCore.QRect(160, 230, 111, 41))
        self.startbutton.setText("START")
        self.startbutton.setObjectName("startbutton")
        self.image_blueberrypi.raise_()
        self.main_blueberrypi.raise_()
        self.startbutton.raise_()
        self.keywindow.addWidget(self.main_page)

    def makeAddKeyWindow(self):
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.lineEdit = QtWidgets.QLineEdit(self.page)
        self.lineEdit.setGeometry(QtCore.QRect(180, 290, 113, 33))
        self.lineEdit.setObjectName("lineEdit")
        self.buttonNameLabel = QtWidgets.QLabel(self.page)
        self.buttonNameLabel.setGeometry(QtCore.QRect(40, 290, 133, 33))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.buttonNameLabel.setFont(font)
        self.buttonNameLabel.setObjectName("buttonNameLabel")
        #
        self.deleteButton = QtWidgets.QPushButton(self.page)
        self.deleteButton.setEnabled(True)
        self.deleteButton.setGeometry(QtCore.QRect(315, 290, 83, 33))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.deleteButton.setFont(font)
        self.deleteButton.setObjectName("deleteButton")
        #
        self.m = QtWidgets.QPushButton(self.page)
        self.m.setGeometry(QtCore.QRect(280, 220, 31, 31))
        self.m.setObjectName("m")
        self.F4 = QtWidgets.QPushButton(self.page)
        self.F4.setGeometry(QtCore.QRect(130, 100, 31, 31))
        self.F4.setObjectName("F4")
        self.listWidget = QtWidgets.QListWidget(self.page)
        self.listWidget.setGeometry(QtCore.QRect(40, 30, 301, 61))
        self.listWidget.setObjectName("listWidget")
        self.f = QtWidgets.QPushButton(self.page)
        self.f.setGeometry(QtCore.QRect(170, 190, 31, 31))
        self.f.setObjectName("f")
        self.number_1 = QtWidgets.QPushButton(self.page)
        self.number_1.setGeometry(QtCore.QRect(100, 130, 31, 31))
        self.number_1.setObjectName("number_1")
        self.number_0 = QtWidgets.QPushButton(self.page)
        self.number_0.setGeometry(QtCore.QRect(370, 130, 31, 31))
        self.number_0.setObjectName("number_0")
        self.r = QtWidgets.QPushButton(self.page)
        self.r.setGeometry(QtCore.QRect(130, 160, 31, 31))
        self.r.setObjectName("r")
        self.j = QtWidgets.QPushButton(self.page)
        self.j.setGeometry(QtCore.QRect(260, 190, 31, 31))
        self.j.setObjectName("j")
        self.left = QtWidgets.QPushButton(self.page)
        self.left.setGeometry(QtCore.QRect(310, 250, 31, 31))
        self.left.setObjectName("left")
        self.F9 = QtWidgets.QPushButton(self.page)
        self.F9.setGeometry(QtCore.QRect(280, 100, 31, 31))
        self.F9.setObjectName("F9")
        self.number_7 = QtWidgets.QPushButton(self.page)
        self.number_7.setGeometry(QtCore.QRect(280, 130, 31, 31))
        self.number_7.setObjectName("number_7")
        self.down = QtWidgets.QPushButton(self.page)
        self.down.setGeometry(QtCore.QRect(340, 250, 31, 31))
        self.down.setObjectName("down")
        self.F10 = QtWidgets.QPushButton(self.page)
        self.F10.setGeometry(QtCore.QRect(310, 100, 31, 31))
        self.F10.setObjectName("F10")
        self.y = QtWidgets.QPushButton(self.page)
        self.y.setGeometry(QtCore.QRect(190, 160, 31, 31))
        self.y.setObjectName("y")
        self.space = QtWidgets.QPushButton(self.page)
        self.space.setGeometry(QtCore.QRect(150, 250, 101, 31))
        self.space.setObjectName("space")
        self.i = QtWidgets.QPushButton(self.page)
        self.i.setGeometry(QtCore.QRect(250, 160, 31, 31))
        self.i.setObjectName("i")
        self.b = QtWidgets.QPushButton(self.page)
        self.b.setGeometry(QtCore.QRect(220, 220, 31, 31))
        self.b.setObjectName("b")
        self.dot = QtWidgets.QPushButton(self.page)
        self.dot.setGeometry(QtCore.QRect(250, 250, 31, 31))
        self.dot.setObjectName("dot")
        self.number_4 = QtWidgets.QPushButton(self.page)
        self.number_4.setGeometry(QtCore.QRect(190, 130, 31, 31))
        self.number_4.setObjectName("number_4")
        self.number_2 = QtWidgets.QPushButton(self.page)
        self.number_2.setGeometry(QtCore.QRect(130, 130, 31, 31))
        self.number_2.setObjectName("number_2")
        self.d = QtWidgets.QPushButton(self.page)
        self.d.setGeometry(QtCore.QRect(140, 190, 31, 31))
        self.d.setObjectName("d")
        self.alt = QtWidgets.QPushButton(self.page)
        self.alt.setGeometry(QtCore.QRect(100, 250, 51, 31))
        self.alt.setObjectName("alt")
        self.number_3 = QtWidgets.QPushButton(self.page)
        self.number_3.setGeometry(QtCore.QRect(160, 130, 31, 31))
        self.number_3.setObjectName("number_3")
        self.F8 = QtWidgets.QPushButton(self.page)
        self.F8.setGeometry(QtCore.QRect(250, 100, 31, 31))
        self.F8.setObjectName("F8")
        self.esc = QtWidgets.QPushButton(self.page)
        self.esc.setGeometry(QtCore.QRect(40, 130, 61, 31))
        self.esc.setObjectName("esc")
        self.g = QtWidgets.QPushButton(self.page)
        self.g.setGeometry(QtCore.QRect(200, 190, 31, 31))
        self.g.setObjectName("g")
        self.right = QtWidgets.QPushButton(self.page)
        self.right.setGeometry(QtCore.QRect(370, 250, 31, 31))
        self.right.setObjectName("right")
        self.number_5 = QtWidgets.QPushButton(self.page)
        self.number_5.setGeometry(QtCore.QRect(220, 130, 31, 31))
        self.number_5.setObjectName("number_5")
        self.s = QtWidgets.QPushButton(self.page)
        self.s.setGeometry(QtCore.QRect(110, 190, 31, 31))
        self.s.setObjectName("s")
        self.F5 = QtWidgets.QPushButton(self.page)
        self.F5.setGeometry(QtCore.QRect(160, 100, 31, 31))
        self.F5.setObjectName("F5")
        self.F6 = QtWidgets.QPushButton(self.page)
        self.F6.setGeometry(QtCore.QRect(190, 100, 31, 31))
        self.F6.setObjectName("F6")
        self.x = QtWidgets.QPushButton(self.page)
        self.x.setGeometry(QtCore.QRect(130, 220, 31, 31))
        self.x.setObjectName("x")
        self.F11 = QtWidgets.QPushButton(self.page)
        self.F11.setGeometry(QtCore.QRect(340, 100, 31, 31))
        self.F11.setObjectName("F11")
        self.number_8 = QtWidgets.QPushButton(self.page)
        self.number_8.setGeometry(QtCore.QRect(310, 130, 31, 31))
        self.number_8.setObjectName("number_8")
        self.o = QtWidgets.QPushButton(self.page)
        self.o.setGeometry(QtCore.QRect(280, 160, 31, 31))
        self.o.setObjectName("o")
        self.p = QtWidgets.QPushButton(self.page)
        self.p.setGeometry(QtCore.QRect(310, 160, 31, 31))
        self.p.setObjectName("p")
        self.backspace = QtWidgets.QPushButton(self.page)
        self.backspace.setGeometry(QtCore.QRect(340, 160, 61, 31))
        self.backspace.setObjectName("backspace")
        self.capslock = QtWidgets.QPushButton(self.page)
        self.capslock.setGeometry(QtCore.QRect(40, 190, 41, 31))
        self.capslock.setObjectName("capslock")
        self.ctrl = QtWidgets.QPushButton(self.page)
        self.ctrl.setGeometry(QtCore.QRect(40, 250, 61, 31))
        self.ctrl.setObjectName("ctrl")
        self.c = QtWidgets.QPushButton(self.page)
        self.c.setGeometry(QtCore.QRect(160, 220, 31, 31))
        self.c.setObjectName("c")
        self.n = QtWidgets.QPushButton(self.page)
        self.n.setGeometry(QtCore.QRect(250, 220, 31, 31))
        self.n.setObjectName("n")
        self.i1 = QtWidgets.QPushButton(self.page)
        self.i1.setGeometry(QtCore.QRect(310, 220, 31, 31))
        self.i1.setObjectName("i1")
        self.keyAddButton = QtWidgets.QPushButton(self.page)
        self.keyAddButton.setGeometry(QtCore.QRect(350, 50, 51, 31))
        self.keyAddButton.setObjectName("keyAddButton")
        self.u = QtWidgets.QPushButton(self.page)
        self.u.setGeometry(QtCore.QRect(220, 160, 31, 31))
        self.u.setObjectName("u")
        self.t = QtWidgets.QPushButton(self.page)
        self.t.setGeometry(QtCore.QRect(160, 160, 31, 31))
        self.t.setObjectName("t")
        self.up = QtWidgets.QPushButton(self.page)
        self.up.setGeometry(QtCore.QRect(340, 220, 31, 31))
        self.up.setObjectName("up")
        self.number_9 = QtWidgets.QPushButton(self.page)
        self.number_9.setGeometry(QtCore.QRect(340, 130, 31, 31))
        self.number_9.setObjectName("number_9")
        self.F3 = QtWidgets.QPushButton(self.page)
        self.F3.setGeometry(QtCore.QRect(100, 100, 31, 31))
        self.F3.setObjectName("F3")
        self.w = QtWidgets.QPushButton(self.page)
        self.w.setGeometry(QtCore.QRect(70, 160, 31, 31))
        self.w.setObjectName("w")
        self.k = QtWidgets.QPushButton(self.page)
        self.k.setGeometry(QtCore.QRect(290, 190, 31, 31))
        self.k.setObjectName("k")
        self.F1 = QtWidgets.QPushButton(self.page)
        self.F1.setGeometry(QtCore.QRect(40, 100, 31, 31))
        self.F1.setObjectName("F1")
        self.shift = QtWidgets.QPushButton(self.page)
        self.shift.setGeometry(QtCore.QRect(40, 220, 61, 31))
        self.shift.setObjectName("shift")
        self.i2 = QtWidgets.QPushButton(self.page)
        self.i2.setGeometry(QtCore.QRect(370, 220, 31, 31))
        self.i2.setObjectName("i2")
        self.F7 = QtWidgets.QPushButton(self.page)
        self.F7.setGeometry(QtCore.QRect(220, 100, 31, 31))
        self.F7.setObjectName("F7")
        self.number_6 = QtWidgets.QPushButton(self.page)
        self.number_6.setGeometry(QtCore.QRect(250, 130, 31, 31))
        self.number_6.setObjectName("number_6")
        self.z = QtWidgets.QPushButton(self.page)
        self.z.setGeometry(QtCore.QRect(100, 220, 31, 31))
        self.z.setObjectName("z")
        self.v = QtWidgets.QPushButton(self.page)
        self.v.setGeometry(QtCore.QRect(190, 220, 31, 31))
        self.v.setObjectName("v")
        self.l = QtWidgets.QPushButton(self.page)
        self.l.setGeometry(QtCore.QRect(320, 190, 31, 31))
        self.l.setObjectName("l")
        self.q = QtWidgets.QPushButton(self.page)
        self.q.setGeometry(QtCore.QRect(40, 160, 31, 31))
        self.q.setObjectName("q")
        self.F12 = QtWidgets.QPushButton(self.page)
        self.F12.setGeometry(QtCore.QRect(370, 100, 31, 31))
        self.F12.setObjectName("F12")
        self.enter = QtWidgets.QPushButton(self.page)
        self.enter.setGeometry(QtCore.QRect(350, 190, 51, 31))
        self.enter.setObjectName("enter")
        self.h = QtWidgets.QPushButton(self.page)
        self.h.setGeometry(QtCore.QRect(230, 190, 31, 31))
        self.h.setObjectName("h")
        self.e = QtWidgets.QPushButton(self.page)
        self.e.setGeometry(QtCore.QRect(100, 160, 31, 31))
        self.e.setObjectName("e")
        self.F2 = QtWidgets.QPushButton(self.page)
        self.F2.setGeometry(QtCore.QRect(70, 100, 31, 31))
        self.F2.setObjectName("F2")
        self.a = QtWidgets.QPushButton(self.page)
        self.a.setGeometry(QtCore.QRect(80, 190, 31, 31))
        self.a.setObjectName("a")
        self.comma = QtWidgets.QPushButton(self.page)
        self.comma.setGeometry(QtCore.QRect(280, 250, 31, 31))
        self.comma.setObjectName("comma")
        self.exitButton = QtWidgets.QPushButton(self.page)
        self.exitButton.setGeometry(QtCore.QRect(410, 10, 21, 21))
        self.exitButton.setObjectName("exitButton")        
        self.keywindow.addWidget(self.page)
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "BLUEBERRYPI CUSTOM KEYBOARD"))
        self.main_blueberrypi.setText(_translate("MainWindow", "BLUEBERRY PI CUSTOM KEYBOARD"))
        self.startbutton.setText(_translate("MainWindow", "START"))
        self.keyAddButton.setText(_translate("MainWindow", "ADD"))
        self.exitButton.setText(_translate("MainWindow", "X"))
        self.disable_keys.setText(_translate("MainWindow", "Disable"))
        self.buttonNameLabel.setText(_translate("MainWindow", "Button Name:"))
        self.deleteButton.setText(_translate("MainWindow", "DELETE"))

        for button in all_buttons:
            button.setText(_translate("MainWindow", "+"))

        for button in defined_buttons:        
            objectLabel = database.setDatabase(button.objectName())
            if objectLabel != 0:
                button.setText(objectLabel)

class Keyboard():

    def __init__(self):
        #the structure for a bt keyboard input report (size is 10 bytes)

        self.state=[
            0xA1, #this is an input report
            0x01, #Usage report = Keyboard
            #Bit array for Modifier keys
            [0, #Right GUI - Windows Key
             0, #Right ALT
             0,     #Right Shift
             0,     #Right Control
             0, #Left GUI
             0,     #Left ALT
             0, #Left Shift
             0],    #Left Control
            0x00,   #Vendor reserved
            0x00,   #rest is space for 6 keys
            0x00,
            0x00,
            0x00,
            0x00,
            0x00]

        #print "setting up DBus Client"  
        self.bus = dbus.SystemBus()
        self.btkservice = self.bus.get_object('org.yaptb.btkbservice','/org/yaptb/btkbservice')
        self.iface = dbus.Interface(self.btkservice,'org.yaptb.btkbservice')    

    def change_state(self, button, event, i):
       
        inputStr=database.keyDatabase(button.objectName(), i)
        if inputStr=='ctrl' or inputStr=='shift' or inputStr=='alt':
            inputStr='left'+inputStr;
        elif inputStr=='caps':
            inputStr=inputStr+'lock'
        elif inputStr=='.':
            inputStr='dot'
        evdev_code="KEY_"+inputStr.upper()
        modkey_element=keymap.modkey(evdev_code)
        
        if modkey_element > 0:
            if self.state[2][modkey_element] ==0:
                self.state[2][modkey_element]=1
            else:
                self.state[2][modkey_element]=0
        
        else:
    
            #Get the keycode of the key
            #hex_key = keymap.convert(ecodes.KEY[event.code])
            hex_key=keymap.convert(evdev_code)
            #Loop through elements 4 to 9 of the inport report structure
            for i in range(4,10):
                if self.state[i]== hex_key and event==0:
                    #Code 0 so we need to depress it
                  self.state[i] = 0x00
                elif self.state[i] == 0x00 and event==1:
                    #if the current space if empty and the key is being pressed
                    self.state[i]=hex_key
                    break;

                        
    #poll for keyboard events
    def event_loop(self,button,event):
        cnt=database.countDatabase(button.objectName())
        for i in range(0,cnt):
            if (event==1):
                #for i in range(0,cnt):
                    #only bother if we hit a key and its an up or down event                
                self.change_state(button, event, i)
                self.send_input()
            else:
                #for i in range(0,cnt):  
                    #only bother if we hit a key and its an up or down event                
                self.change_state(button,event,i)
                self.send_input()
                

    #forward keyboard events to the dbus service
    def send_input(self):

        bin_str=""
        element=self.state[2]
        for bit in element:
            bin_str += str(bit)

        self.iface.send_keys(int(bin_str,2),self.state[4:10])

       
class Form(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self,parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
  
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Form()
    w.show()
    kb = Keyboard()
    sys.exit(app.exec())
