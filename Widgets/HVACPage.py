# Copyright (C) 2023 Suchinton Chakravarty
# Copyright (C) 2024 Konsulko Group
#
# SPDX-License-Identifier: Apache-2.0

from extras.KuksaClient import KuksaClient
import os
import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QListWidget, QSlider, QPushButton

current_dir = os.path.dirname(os.path.abspath(__file__))

# ========================================

sys.path.append(os.path.dirname(current_dir))


Form, Base = uic.loadUiType(os.path.join(current_dir, "../ui/HVAC.ui"))

# ========================================


class HVAC_Paths():
    def __init__(self):
        self.leftTemp = "Vehicle.Cabin.HVAC.Station.Row1.Driver.Temperature"
        self.leftFanSpeed = "Vehicle.Cabin.HVAC.Station.Row1.Driver.FanSpeed"
        self.rightTemp = "Vehicle.Cabin.HVAC.Station.Row1.Passenger.Temperature"
        self.rightFanSpeed = "Vehicle.Cabin.HVAC.Station.Row1.Passenger.FanSpeed"

        # temperatureList contains values from 32 to 16
        self.temperatureList = [str(i) + "°C" for i in range(32, 15, -1)]


class HVACWidget(Base, Form):
    """
    A widget for controlling HVAC settings.

    Inherits from Base and Form.
    """

    def __init__(self, parent=None):
        """
        Initializes the HVACWidget.

        Args:
        - parent: The parent widget. Defaults to None.
        """

        super(self.__class__, self).__init__(parent)
        self.setupUi(self)

        self.HVAC = HVAC_Paths()

        self.kuksa_client = KuksaClient()

        self.leftTempList = self.findChild(QListWidget, "leftTempList")
        self.leftTempList.addItems(self.HVAC.temperatureList)
        self.leftTempList.setCurrentRow(0)
        self.leftTempList.itemClicked.connect(self.leftTempListClicked)
        self.leftTempList.itemSelectionChanged.connect(
            self.leftTempListClicked)
        self.leftTempList.wheelEvent = lambda event: None

        self.rightTempList = self.findChild(QListWidget, "rightTempList")
        self.rightTempList.addItems(self.HVAC.temperatureList)
        self.rightTempList.setCurrentRow(0)
        self.rightTempList.itemClicked.connect(self.rightTempListClicked)
        self.rightTempList.itemSelectionChanged.connect(
            self.rightTempListClicked)
        self.rightTempList.wheelEvent = lambda event: None

        self.leftTempUp = self.findChild(QPushButton, "leftTempUp")
        self.leftTempUp.clicked.connect(
            lambda: self.leftTempList.setCurrentRow(self.leftTempList.currentRow() - 1))

        self.leftTempDown = self.findChild(QPushButton, "leftTempDown")
        self.leftTempDown.clicked.connect(
            lambda: self.leftTempList.setCurrentRow(self.leftTempList.currentRow() + 1))

        self.rightTempUp = self.findChild(QPushButton, "rightTempUp")
        self.rightTempUp.clicked.connect(
            lambda: self.rightTempList.setCurrentRow(self.rightTempList.currentRow() - 1))

        self.rightTempDown = self.findChild(QPushButton, "rightTempDown")
        self.rightTempDown.clicked.connect(
            lambda: self.rightTempList.setCurrentRow(self.rightTempList.currentRow() + 1))

        self.leftFanSpeed_slider = self.findChild(
            QSlider, "leftFanSpeed_slider")
        self.leftFanSpeed_slider.valueChanged.connect(
            self.leftFanSpeed_sliderChanged)

        self.rightFanSpeed_slider = self.findChild(
            QSlider, "rightFanSpeed_slider")
        self.rightFanSpeed_slider.valueChanged.connect(
            self.rightFanSpeed_sliderChanged)

    def leftTempListClicked(self):
        """
        Handles the event when an item in the left temperature list is clicked.
        Sets the corresponding VSS signal to the selected temperature value.
        """

        self.setTemperature(self.leftTempList, self.HVAC.leftTemp)

    def rightTempListClicked(self):
        """
        Handles the event when an item in the right temperature list is clicked.
        Sets the corresponding VSS signal to the selected temperature value.
        """

        self.setTemperature(self.rightTempList, self.HVAC.rightTemp)

    def setTemperature(self, list_widget, path):
        item = list_widget.currentItem()
        if item is not None:
            list_widget.scrollToItem(item, 1)
            self.kuksa_client.set(path, item.text()[:-2], "targetValue")
            print(item.text())

    def leftFanSpeed_sliderChanged(self):
        """
        Handles the event when the left fan speed slider is changed.
        Sets the corresponding VSS signal to the fan speed value.
        """

        value = self.leftFanSpeed_slider.value()
        self.kuksa_client.set(self.HVAC.leftFanSpeed, str(value), "targetValue")
        print(value)

    def rightFanSpeed_sliderChanged(self):
        """
        Handles the event when the right fan speed slider is changed.
        Sets the corresponding VSS signal to the fan speed value.
        """

        value = self.rightFanSpeed_slider.value()
        self.kuksa_client.set(self.HVAC.rightFanSpeed, str(value), "targetValue")
        print(value)


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = HVACWidget()
    w.show()
    sys.exit(app.exec_())
