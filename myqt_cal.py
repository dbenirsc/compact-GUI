import sys
import time
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import pyqtgraph as pg
import ServerRecord as SR
import struct
from matplotlib import cm
import pickle
import os.path

global L, W, S, BGI
L = 156
W = 208
S = L*W

class App(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)

        self.dev = SR.usbinit()
        self.plat = 0x54
        self.android = "\x01"

        self.proc = 0x3E
        self.cal = "\x08\x00"

        self.mode = 0x3C
        self.run = "\x01\x00"
        self.sleep ="\x00\x00"

        self.save = 0
        self.BGI = 30

        #### Create Gui Elements ####
        self.mainbox = QtGui.QWidget()
        self.setCentralWidget(self.mainbox)
        self.mainbox.setLayout(QtGui.QVBoxLayout())

        self.label = QtGui.QLabel()
        self.mainbox.layout().addWidget(self.label)

        self.imv = pg.ImageView(parent=self.label)
        self.imv.setColorMap
        self.imv.show()

        self.button1 = QtGui.QPushButton('Save')
        self.button1.clicked.connect(self.saveButton)
        self.mainbox.layout().addWidget(self.button1)

        self.button2 = QtGui.QPushButton('Take Background')
        self.button2.clicked.connect(self.BackGround)
        self.mainbox.layout().addWidget(self.button2)

        self.textbox1 = QtGui.QLineEdit()
        self.textbox1.setText('Save Filename')
        self.mainbox.layout().addWidget(self.textbox1)

        self.textbox2 = QtGui.QLineEdit()
        self.textbox2.setText('Number of frames')
        self.mainbox.layout().addWidget(self.textbox2)

        ### Startup Procedure to set camera settings.
        self.short_msg(self.mode, self.sleep)

        self.short_msg(self.proc, self.cal)
        time.sleep(1)
        self.short_msg(self.mode, self.run)
        time.sleep(1)

        self.BackGround()
        self.t_start = time.time()
        self.t_now = self.t_start
        self.count = 0
        self._update()

    def saveButton(self):

        if not os.path.isfile(self.textbox1.text()):
            self.save = 1
            self.savecount = 0
            self.savesize = int(self.textbox2.text())
            self.saveData = []
            self.saveTime = []
        else:
            print "File name already exists"

    def _update(self):
        self.count += 1
        byte = SR.read_frame(self.dev)
        Image_raw = np.fromstring(byte, dtype="short").reshape(156,208)
        Image = Image_raw-self.BG

        Image [0, 40] = 0
        self.imv.setImage(Image, autoHistogramRange=False, autoLevels=False)

        if self.save == 1:
            self.saveData.append(Image_raw)
            self.saveTime.append(time.time())
            self.savecount += 1
            if self.savecount%10 == 0:
                print "Saving: On frame %d" % self.savecount

            if self.savecount == self.savesize:
                self.save = 0
                with open(self.textbox1.text(), 'wb') as fp:
                    pickle.dump([self.saveData, self.saveTime, self.BG], fp)

                self.saveData = []

        if self.count % 100 == 0:
            self.t_prev = self.t_now
            self.t_now = time.time() - self.t_start
            hour = self.t_now/3600
            minute = self.t_now%3600/60
            second = self.t_now%3600%60
            dt = self.t_now-self.t_prev
            avg_framerate = 100/dt
            print "%d:%d:%d" % (hour, minute, second)
            print "Average frame rate is: %d" % round(avg_framerate,1)

        QtCore.QTimer.singleShot(1, self._update)


    def BackGround(self):
        BG_A = np.zeros((L,W,self.BGI))
        for k in range(0,self.BGI):
            byte = SR.read_frame(self.dev)
            BG_A[:,:,k] = np.fromstring(byte, dtype="short").reshape(156,208)

        self.BG = np.mean(BG_A, 2)

    def short_msg(self, sett, command):
        SR.send_msg(self.dev, 0x41, sett, 0, 0, command)

    def factorysettings(self):
        SR.send_msg(self.dev,0x41, 0x56, 0, 0, '\x20\x00\x30\x00\x00\x00')
        SR.send_msg(self.dev,0x41, 0x56, 0, 0, '\x20\x00\x50\x00\x00\x00')
        SR.send_msg(self.dev,0x41, 0x56, 0, 0, '\x0C\x00\x70\x00\x00\x00')
        SR.send_msg(self.dev,0x41, 0x56, 0, 0, '\x06\x00\x08\x00\x00\x00')


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    thisapp = App()
    thisapp.show()
    sys.exit(app.exec_())
