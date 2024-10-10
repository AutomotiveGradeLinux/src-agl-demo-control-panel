# Copyright (C) 2024 Suchinton Chakravarty
# Copyright (C) 2024 Konsulko Group
#
# SPDX-License-Identifier: Apache-2.0

import os
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QPushButton, QWidget, QLabel
from PyQt6.QtQuickWidgets import QQuickWidget
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtCore import QUrl
import logging

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

        self.TPIncreaseBtn.clicked.connect(self.increase_pressure)
        self.TPDecreaseBtn.clicked.connect(self.decrease_pressure)

    def get_Current(self, tire):
        """
        Initializes the TirePressure widget.
        """

        try:
            self.TPUnit = self.kuksa_client.get("Vehicle.Cabin.Infotainment.HMI.TirePressureUnit")
            return self.kuksa_client.get(self.TirePressurePath.Tires[tire])
        except Exception as e:
            logging.error(f"Error getting tire pressure values: {e}")


    def increase_pressure(self):
        """
        Increases the pressure of the selected tire.
        """

        selected_tire = self.TireSelector.rootObject().property("selectedTireIndex")
        
        current_pressure = self.get_Current(selected_tire)
        if current_pressure is None:
            return
        else:
            self.kuksa_client.setValues({self.TirePressurePath.Tires[selected_tire]: current_pressure + 1})


    def decrease_pressure(self):
        """
        Decreases the pressure of the selected tire.
        """

        selected_tire = self.TireSelector.rootObject().property("selectedTireIndex")

        current_pressure = self.get_Current(selected_tire)
        if current_pressure is None:
            return
        else:
            self.kuksa_client.setValues({self.TirePressurePath.Tires[selected_tire]: current_pressure - 1})

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = TirePressure()
    w.show()
    sys.exit(app.exec())
