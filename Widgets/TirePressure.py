# Copyright (C) 2024 Suchinton Chakravarty
# Copyright (C) 2024 Konsulko Group
#
# SPDX-License-Identifier: Apache-2.0

import os
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QLabel, QLCDNumber
from PyQt6.QtCore import QTimer
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import QUrl
import logging
import json

current_dir = os.path.dirname(os.path.abspath(__file__))

# ========================================

sys.path.append(os.path.dirname(current_dir))

Form, Base = uic.loadUiType(os.path.join(current_dir, "../ui/TirePressure.ui"))

# ========================================

from extras.KuksaClient import KuksaClient
import res_rc

class TirePressure_Paths():
    def __init__(self):
        self.Tires = {
            0 : "Vehicle.Chassis.Axle.Row1.Wheel.Left.Tire.Pressure",
            1 : "Vehicle.Chassis.Axle.Row1.Wheel.Right.Tire.Pressure",
            2 : "Vehicle.Chassis.Axle.Row2.Wheel.Left.Tire.Pressure",
            3 : "Vehicle.Chassis.Axle.Row2.Wheel.Right.Tire.Pressure"
            }

def TireSelectionWidget():
    """
    A widget for selecting the tire to control.

    Returns:
    - A QListWidget.
    """

    QMLPath = os.path.join(current_dir, "../QMLWidgets/Tire_Pressure/TirePressure.qml")
    widget = QQuickWidget()
    widget.setSource(QUrl.fromLocalFile(QMLPath))
    widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
    return widget

class TirePressure(Base, Form):
    """
    A widget for controlling TirePressure settings.

    Inherits from Base and Form.
    """

    def __init__(self, parent=None):
        """
        Initializes the TirePressureWidget.

        Args:
        - parent: The parent widget. Defaults to None.
        """

        super(self.__class__, self).__init__(parent)
        self.setupUi(self)

        self.TirePressurePath = TirePressure_Paths()
        self.kuksa_client = KuksaClient()
        self.TireSelector = TireSelectionWidget()
        
        placeholder = self.findChild(QWidget, "TS_Placeholher")
        frame = self.findChild(QWidget, "frame")
        frame.layout().replaceWidget(placeholder, self.TireSelector)
        self.TPIncreaseBtn = self.findChild(QPushButton, "TPIncreaseBtn")
        self.TPDecreaseBtn = self.findChild(QPushButton, "TPDecreaseBtn")
        self.TPUnit = self.findChild(QLabel, "TPUnit")
        self.TPLCD = self.findChild(QLCDNumber, "TPLCD")

        self.TireSelector.rootObject().valueChanged.connect(self.update_TP_LCD_value)
        self.TPIncreaseBtn.clicked.connect(self.increase_pressure)
        self.TPDecreaseBtn.clicked.connect(self.decrease_pressure)

        # after 2 seconds reconnect the signals
        QTimer.singleShot(500, self.reconnectSignals)  

    def reconnectSignals(self):
        self.TireSelector.rootObject().valueChanged.connect(self.update_TP_LCD_value)

    def update_TP_LCD_value(self):
        """
        Updates the value on the LCD display when a new tire is selected.
        """
        selected_tire = self.TireSelector.rootObject().property("selectedTireIndex")
        print(selected_tire)
        tire = str(self.TirePressurePath.Tires[selected_tire])
        try:
            value = int(json.loads(self.kuksa_client.get(tire))["value"]["value"])
            self.set_LCD_Value(value)
            
            unit = str(json.loads(self.kuksa_client.get("Vehicle.Cabin.Infotainment.HMI.TirePressureUnit"))["value"]["value"])
            self.TPUnit.setText(unit)
        except Exception as e:
            logging.error(e)

    def set_LCD_Value(self, value):
        """
        Sets the value of the LCD display.
        """
        self.TPLCD.display(value)

    def get_selected_tire_pressure(self):
        """
        Gets the pressure of the selected tire.
        """

        selected_tire = self.TireSelector.rootObject().property("selectedTireIndex")
        tire = str(self.TirePressurePath.Tires[selected_tire])
        value = int(json.loads(self.kuksa_client.get(tire))["value"]["value"])
        return value

    def increase_pressure(self):
        """
        Increases the pressure of the selected tire.
        """

        selected_tire = self.TireSelector.rootObject().property("selectedTireIndex")
        
        if selected_tire == -1:
            return
        
        tire = str(self.TirePressurePath.Tires[selected_tire])
        current = self.get_selected_tire_pressure()
        self.kuksa_client.set(tire, current + 1)
        self.set_LCD_Value(current + 1)


    def decrease_pressure(self):
        """
        Decreases the pressure of the selected tire.
        """
    
        selected_tire = self.TireSelector.rootObject().property("selectedTireIndex")

        if selected_tire == -1:
            return
        
        tire = str(self.TirePressurePath.Tires[selected_tire])
        current = self.get_selected_tire_pressure()
        self.kuksa_client.set(tire, current - 1)
        self.set_LCD_Value(current - 1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TirePressure()
    w.show()
    sys.exit(app.exec())
