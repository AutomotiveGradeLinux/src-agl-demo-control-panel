# Copyright (C) 2023 Suchinton Chakravarty
# Copyright (C) 2024 Konsulko Group
#
# SPDX-License-Identifier: Apache-2.0

import os
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QFrame, QSlider, QWidget
from PyQt6 import QtWidgets
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import QTimer

current_dir = os.path.dirname(os.path.abspath(__file__))

# ========================================

sys.path.append(os.path.dirname(current_dir))

Form, Base = uic.loadUiType(os.path.join(current_dir, "../ui/HVAC.ui"))

# ========================================

from extras.KuksaClient import KuksaClient
import res_rc

class HVAC_Paths():
    def __init__(self):
        self.leftTemp = "Vehicle.Cabin.HVAC.Station.Row1.Driver.Temperature"
        self.leftFanSpeed = "Vehicle.Cabin.HVAC.Station.Row1.Driver.FanSpeed"
        self.rightTemp = "Vehicle.Cabin.HVAC.Station.Row1.Passenger.Temperature"
        self.rightFanSpeed = "Vehicle.Cabin.HVAC.Station.Row1.Passenger.FanSpeed"

def TumblerWidget():
    """QWidget for controlling HVAC Temperature."""
    
    TumblerQML = os.path.join(current_dir, "../QMLWidgets/Temp_Tumbler/TempTumbler.qml")

    TumblerWidget = QQuickWidget()
    TumblerWidget.setSource(QUrl.fromLocalFile(TumblerQML))
    TumblerWidget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
    TumblerWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)

    return TumblerWidget

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

        leftFrame = self.findChild(QFrame, "leftFrame")
        
        # Create left temperature tumbler
        self.LeftTempTumbler = TumblerWidget()
        # Connect the left tumbler signal to the handler
        self.LeftTempTumbler.rootObject().valueChanged.connect(self.onLeftTempChanged)

        # Replace placeholder LeftTemp_Placeholder with the LeftTempTumbler widget
        leftFrame.layout().replaceWidget(self.findChild(QWidget, "LeftTemp_Placeholder"), self.LeftTempTumbler)

        rightFrame = self.findChild(QFrame, "rightFrame")
        
        # Create right temperature tumbler
        self.RightTempTumbler = TumblerWidget()
        
        # Connect the right tumbler signal to the handler
        self.RightTempTumbler.rootObject().valueChanged.connect(self.onRightTempChanged)

        # Replace placeholder RightTemp_Placeholder with the RightTempTumbler widget
        rightFrame.layout().replaceWidget(self.findChild(QWidget, "RightTemp_Placeholder"), self.RightTempTumbler)

        self.leftFanSpeed_slider = self.findChild(
            QSlider, "leftFanSpeed_slider")
        self.leftFanSpeed_slider.valueChanged.connect(
            self.leftFanSpeed_sliderChanged)

        self.rightFanSpeed_slider = self.findChild(
            QSlider, "rightFanSpeed_slider")
        self.rightFanSpeed_slider.valueChanged.connect(
            self.rightFanSpeed_sliderChanged)
        
        # after 2 seconds reconnect the signals
        QTimer.singleShot(500, self.reconnectSignals)      
        
    # funcyion to reconnect the tumbler signals 
    def reconnectSignals(self):
        self.LeftTempTumbler.rootObject().valueChanged.connect(self.onLeftTempChanged)
        self.RightTempTumbler.rootObject().valueChanged.connect(self.onRightTempChanged)

    def changeTemperature(self, tumbler_widget, change):
        """Change tumbler value by incrementing or decrementing."""
        
        # use the inc_Value method from the QML object if change is 1 then increment, else decrement
        # Access the root object of the QML component
        self.LeftTempTumbler.rootObject().property("inc_Value", change)

    def onLeftTempChanged(self, newValue):
        """Slot to handle changes in left temperature tumbler."""
        
        print(f"Left Temperature Tumbler stopped at value: {newValue}°C")
        self.setTemperature(newValue, self.HVAC.leftTemp)

    def onRightTempChanged(self, newValue):
        """Slot to handle changes in right temperature tumbler."""
        
        print(f"Right Temperature Tumbler stopped at value: {newValue}°C")
        self.setTemperature(newValue, self.HVAC.rightTemp)

    def setTemperature(self, temp, path):
        self.kuksa_client.set(path, str(temp), "targetValue")

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
    app = QApplication(sys.argv)
    w = HVACWidget()
    w.show()
    sys.exit(app.exec())