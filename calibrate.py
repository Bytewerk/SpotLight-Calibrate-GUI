#!/usr/bin/python
import sys
import can
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QDesktopWidget, QSlider, QLabel, QSpinBox


class MainWindow(QWidget):

    MIN_X = 0x300
    MAX_X = 0x1200
    MIN_Y = 0x300
    MAX_Y = 0x1200

    CAN_ID_START = 0x200
    CAN_ID_OFFSET_SET_POS = 0x01
    CAN_ID_OFFSET_SET_UPPER_LIMIT = 0x02
    CAN_ID_OFFSET_SET_LOWER_LIMIT = 0x03
    CAN_ID_OFFSET_SET_POS_RAW = 0x04
    CAN_ID_OFFSET_SET_ADDRESS = 0x06
    CAN_ID_OFFSET_STORE_CONFIG = 0x07

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.can = can.interface.Bus('can0', bustype='socketcan_native')

    def init_ui(self):
        y = 10
        laConfigAddress = QLabel("Address: ", self)
        laConfigAddress.setGeometry(10, y+6, 590, 15)

        self.spSelectAddress = QSpinBox(self)
        self.spSelectAddress.setRange(0, 255)
        self.spSelectAddress.setGeometry(80, y, 60, 25)

        y += 50
        self.laPosPitch = QLabel("Pitch: ", self)
        self.laPosPitch.setGeometry(10, y, 590, 10)

        y += 10
        self.sliderPitch = QSlider(self)
        self.sliderPitch.setMinimum(self.MIN_X)
        self.sliderPitch.setMaximum(self.MAX_X)
        self.sliderPitch.setValue(self.MAX_X/2)
        self.sliderPitch.setValue(self.MIN_X + (self.MAX_X-self.MIN_X)/2)
        self.sliderPitch.setGeometry(10, y, 590, 50)
        self.sliderPitch.setOrientation(Qt.Horizontal)
        self.sliderPitch.valueChanged.connect(self.slidersChanged)

        y += 50
        self.laPosYaw = QLabel("Yaw: ", self)
        self.laPosYaw.setGeometry(10, y, 590, 10)

        y += 10
        self.sliderYaw = QSlider(self)
        self.sliderYaw.setMinimum(self.MIN_Y)
        self.sliderYaw.setMaximum(self.MAX_Y)
        self.sliderYaw.setValue(self.MIN_Y + (self.MAX_Y-self.MIN_Y)/2)
        self.sliderYaw.setGeometry(10, y, 590, 50)
        self.sliderYaw.setOrientation(Qt.Horizontal)
        self.sliderYaw.valueChanged.connect(self.slidersChanged)

        y += 70
        btLowerLimit = QPushButton('set lower limit', self)
        btLowerLimit.setGeometry(10, y, 100, 25)
        btLowerLimit.clicked.connect(self.btLowerLimitClicked)
        btUpperLimit = QPushButton('set upper limit', self)
        btUpperLimit.setGeometry(120, y, 100, 25)
        btUpperLimit.clicked.connect(self.btUpperLimitClicked)
        btStoreEeprom = QPushButton('store eeprom', self)
        btStoreEeprom.setGeometry(230, y, 100, 25)
        btStoreEeprom.clicked.connect(self.btStoreEepromClicked)

        self.spSetAddress = QSpinBox(self)
        self.spSetAddress.setRange(0, 255)
        self.spSetAddress.setGeometry(340, y, 50, 25)

        btSetAddress = QPushButton('Set ID', self)
        btSetAddress.setGeometry(390, y, 60, 25)
        btSetAddress.clicked.connect(self.btSetAddressClicked)

        btQuit = QPushButton('Quit', self)
        btQuit.setGeometry(500, y, 100, 25)
        btQuit.clicked.connect(QApplication.instance().quit)

        self.setWindowTitle("Servo Calibration")
        self.resize(610, 250)
        self.center()
        self.show()

    def get_id(self):
        return self.spSelectAddress.value()

    def slidersChanged(self):
        self.set_pos_raw(self.get_id(), self.sliderPitch.value(), self.sliderYaw.value())

    def btLowerLimitClicked(self):
        self.set_lower_limit(self.get_id())

    def btUpperLimitClicked(self):
        self.set_upper_limit(self.get_id())

    def btSetAddressClicked(self):
        self.set_address(self.get_id(), self.spSetAddress.value())
        self.spSelectAddress.setValue(self.spSetAddress.value())

    def btStoreEepromClicked(self):
        self.store_config(self.get_id())

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def set_pos_raw(self, id, pitch, yaw, brightness=0):
        data = [
            (pitch >> 8) & 0xFF,
            (pitch >> 0) & 0xFF,
            (yaw >> 8) & 0xFF,
            (yaw >> 0) & 0xFF,
            brightness
        ]
        msg = can.Message(arbitration_id=self.CAN_ID_START + id*0x10 + self.CAN_ID_OFFSET_SET_POS_RAW, data=data)
        self.can.send(msg)

    def set_lower_limit(self, id):
        msg = can.Message(arbitration_id=self.CAN_ID_START + id*0x10 + self.CAN_ID_OFFSET_SET_LOWER_LIMIT, data=[])
        self.can.send(msg)

    def set_upper_limit(self, id):
        msg = can.Message(arbitration_id=self.CAN_ID_START + id*0x10 + self.CAN_ID_OFFSET_SET_UPPER_LIMIT, data=[])
        self.can.send(msg)

    def set_address(self, id, new_address):
        msg = can.Message(arbitration_id=self.CAN_ID_START + id * 0x10 + self.CAN_ID_OFFSET_SET_ADDRESS, data=[new_address])
        self.can.send(msg)

    def store_config(self, id):
        msg = can.Message(arbitration_id=self.CAN_ID_START + id * 0x10 + self.CAN_ID_OFFSET_STORE_CONFIG, data=[])
        self.can.send(msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
