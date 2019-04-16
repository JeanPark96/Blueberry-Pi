import sys
from PyQt5 import QtWidgets
from PyQt5 import uic

class Form(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("/home/pi/BlueberryPi/mainwindow.ui")
        self.ui.show()
    def btn_slot(self):
        self.ui.label.setText("11")
    

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Form()
    sys.exit(app.exec_())
