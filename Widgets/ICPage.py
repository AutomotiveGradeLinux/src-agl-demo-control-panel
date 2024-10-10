# Copyright (C) 2023 Suchinton Chakravarty
# Copyright (C) 2024 Konsulko Group
#
# SPDX-License-Identifier: Apache-2.0

import os
import logging
import sys
from PyQt6 import uic, QtCore, QtWidgets
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QWidget, QFrame, QDockWidget
from PyQt6.QtQuickWidgets import QQuickWidget
import threading

current_dir = os.path.dirname(os.path.abspath(__file__))

# ========================================

sys.path.append(os.path.dirname(current_dir))


Form, Base = uic.loadUiType(os.path.join(current_dir, "../ui/IC.ui"))

# ========================================

import extras.config as config
from extras.KuksaClient import KuksaClient
from extras.VehicleSimulator import VehicleSimulator
from Scripts.record_playback import CAN_playback
import res_rc
from Widgets.animatedToggle import AnimatedToggle

def Gauge(gaugeType):
    """QWidget
    This function creates gauge widgest of types RPM, Speed, Fuel and Coolant.

    Returns:
    - A QQuickWidget object representing the gauge widget.
    """

    RPM_GaugeQML = os.path.join(
        current_dir, "../QMLWidgets/Full_Gauge/RPMGauge.qml")
    Speed_GaugeQML = os.path.join(
        current_dir, "../QMLWidgets/Full_Gauge/SpeedGauge.qml")
    Fuel_GaugeQML = os.path.join(
        current_dir, "../QMLWidgets/Half_Gauge/FuelGauge.qml")
    Coolant_GaugeQML = os.path.join(
        current_dir, "../QMLWidgets/Half_Gauge/CoolantGauge.qml")

    gauge = QQuickWidget()
    if gaugeType == "RPM":
        gauge.setSource(QtCore.QUrl(RPM_GaugeQML))

    elif gaugeType == "Speed":
        gauge.setSource(QtCore.QUrl(Speed_GaugeQML))

    elif gaugeType == "Fuel":
        gauge.setSource(QtCore.QUrl(Fuel_GaugeQML))

    elif gaugeType == "Coolant":
        gauge.setSource(QtCore.QUrl(Coolant_GaugeQML))

    gauge.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
    gauge.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                        QtWidgets.QSizePolicy.Policy.Expanding)

    return gauge


class IC_Paths():
    def __init__(self):
        self.speed = "Vehicle.Speed"
        self.engineRPM = "Vehicle.Powertrain.CombustionEngine.Speed"
        self.leftIndicator = "Vehicle.Body.Lights.DirectionIndicator.Left.IsSignaling"
        self.rightIndicator = "Vehicle.Body.Lights.DirectionIndicator.Right.IsSignaling"
        self.hazard = "Vehicle.Body.Lights.Hazard.IsSignaling"
        self.fuelLevel = "Vehicle.Powertrain.FuelSystem.RelativeLevel"
        self.coolantTemp = "Vehicle.Powertrain.CombustionEngine.ECT"
        self.selectedGear = "Vehicle.Powertrain.Transmission.SelectedGear"


class ICWidget(Base, Form):
    """
    This class represents the ICWidget which is a widget for the AGL Demo Control Panel.
    It inherits from the Base and Form classes.
    """

    def __init__(self, parent=None):
        """
        Initializes the ICWidget object.

        Args:
        - parent: The parent widget. Defaults to None.
        """
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)

        self.IC = IC_Paths()

        self.kuksa_client = KuksaClient()
        self.simulator = VehicleSimulator()
        self.simulator_running = False

        header_frame = self.findChild(QWidget, "header_frame")
        layout = header_frame.layout()

        self.Frame_1 = self.findChild(QWidget, "frame_1")
        self.Fuel_Gauge_Frame = self.findChild(QFrame, "fuel_gauge_frame")
        self.Coolant_Gauge_Frame = self.findChild(
            QFrame, "coolant_gauge_frame")

        self.Script_toggle = AnimatedToggle()

        layout.replaceWidget(self.demoToggle, self.Script_toggle)
        self.demoToggle.deleteLater()

        buttons = [self.parkBtn,
                   self.reverseBtn,
                   self.neutralBtn,
                   self.driveBtn]

        # group for the buttons for mutual exclusion

        self.simulator.speed_changed.connect(self.set_Vehicle_Speed)
        self.simulator.rpm_changed.connect(self.set_Vehicle_RPM)

        self.driveGroupBtns = QtWidgets.QButtonGroup(self)
        self.driveGroupBtns.setExclusive(True)

        for button in buttons:
            self.driveGroupBtns.addButton(button)

        self.driveGroupBtns.buttonClicked.connect(self.driveBtnClicked)

        Speed_Gauge_Placeholder = self.findChild(
            QWidget, "Speed_Gauge_Placeholder")
        self.Speed_Gauge = Gauge("Speed")
        self.Frame_1.layout().replaceWidget(Speed_Gauge_Placeholder, self.Speed_Gauge)

        self.Speed_slider.valueChanged.connect(self.update_Speed_gauge)
        self.Speed_slider.setMinimum(0)
        self.Speed_slider.setMaximum(240)

        RPM_Gauge_Placeholder = self.findChild(
            QWidget, "RPM_Gauge_Placeholder")
        self.RPM_Gauge = Gauge("RPM")
        self.Frame_1.layout().replaceWidget(RPM_Gauge_Placeholder, self.RPM_Gauge)

        self.RPM_slider.valueChanged.connect(self.update_RPM_monitor)
        self.RPM_slider.setMinimum(0)
        self.RPM_slider.setMaximum(8000)

        fuel_Gauge_Placeholder = self.findChild(
            QWidget, "fuel_Gauge_Placeholder")
        self.Fuel_Gauge = Gauge("Fuel")
        self.Fuel_Gauge_Frame.layout().replaceWidget(
            fuel_Gauge_Placeholder, self.Fuel_Gauge)

        coolant_Gauge_Placeholder = self.findChild(
            QWidget, "coolant_Gauge_Placeholder")
        self.Coolant_Gauge = Gauge("Coolant")
        self.Coolant_Gauge_Frame.layout().replaceWidget(
            coolant_Gauge_Placeholder, self.Coolant_Gauge)

        self.coolantTemp_slider.valueChanged.connect(
            self.update_coolantTemp_monitor)
        self.fuelLevel_slider.valueChanged.connect(
            self.update_fuelLevel_monitor)

        self.leftIndicatorBtn.setCheckable(True)
        self.rightIndicatorBtn.setCheckable(True)
        self.hazardBtn.setCheckable(True)

        self.leftIndicatorBtn.toggled.connect(self.leftIndicatorBtnClicked)
        self.rightIndicatorBtn.toggled.connect(self.rightIndicatorBtnClicked)
        self.hazardBtn.toggled.connect(self.hazardBtnClicked)

        self.Script_toggle.clicked.connect(self.handle_Script_toggle)

        try:
            self.Playback = CAN_playback()
            self.Playback_connections()
        except Exception as e:
            logging.error(f"Error creating playback object {e}")

        self.TirePressureDock = self.findChild(QDockWidget, "TirePressureDock")
        self.TirePressureBtn = self.findChild(
            QtWidgets.QPushButton, "TirePressureBtn")
        self.TirePressureBtn.clicked.connect(self.toggle_TirePressureDock)

    def toggle_TirePressureDock(self):
        if self.TirePressureBtn.isChecked():
            self.Hide_TirePressure(True)
        else:
            self.Hide_TirePressure(False)

    def Hide_TirePressure(self, bool_arg):
        widthExtended = 0 if bool_arg else 400
        self.TirePressureDock.setFixedWidth(widthExtended)
        

    def Playback_connections(self):
        self.Playback.speedUpdate.connect(self.set_Vehicle_Speed)
        self.Playback.gearUpdate.connect(self.playback_set_Vehicle_Gear)
        self.Playback.engineSpeedUpdate.connect(self.set_Vehicle_RPM)
        self.Playback.indicatorUpdate.connect(
            self.playback_set_Vehicle_Indicators)

    def playback_set_Vehicle_Gear(self, gear):
        if gear == "P":
            self.parkBtn.setChecked(True)
        if gear == "D":
            self.driveBtn.setChecked(True)
        if gear == "R":
            self.reverseBtn.setChecked(True)
        if gear == "N":
            self.neutralBtn.setChecked(True)

    def playback_set_Vehicle_Indicators(self, indicator):
        if indicator == "HazardOn":
            self.hazardBtn.setChecked(True)
        elif indicator == "HazardOff":
            self.hazardBtn.setChecked(False)
        elif indicator == "LeftBlinkerOn":
            self.leftIndicatorBtn.setChecked(True)
        elif indicator == "LeftBlinkerOff":
            self.leftIndicatorBtn.setChecked(False)
        elif indicator == "RightBlinkerOn":
            self.rightIndicatorBtn.setChecked(True)
        elif indicator == "RightBlinkerOff":
            self.rightIndicatorBtn.setChecked(False)

    def set_Vehicle_Speed(self, speed):
        self.Speed_slider.setValue(speed)

    def set_Vehicle_RPM(self, rpm):
        self.RPM_slider.setValue(rpm)

    def update_Speed_gauge(self):
        """
        Updates the speed monitor with the current speed value.
        """
        speed = int(self.Speed_slider.value())
        speed = speed / 240
        self.Speed_Gauge.rootObject().setProperty('value', speed)
        if not self.simulator_running:
            try:
                self.kuksa_client.set(self.IC.speed, str(speed), 'value')
            except Exception as e:
                logging.error(f"Error sending values to kuksa {e}")

    def update_RPM_monitor(self):
        """
        Updates the RPM monitor with the current RPM value.
        """
        rpm = int(self.RPM_slider.value())
        rpm = rpm / 8000
        self.RPM_Gauge.rootObject().setProperty('value', rpm)
        if not self.simulator_running:
            try:
                self.kuksa_client.set(self.IC.engineRPM, str(rpm), 'value')
            except Exception as e:
                logging.error(f"Error sending values to kuksa {e}")

    def update_coolantTemp_monitor(self):
        """
        Updates the coolant temperature monitor with the current coolant temperature value.
        """
        coolantTemp = int(self.coolantTemp_slider.value())
        gaugeValue = coolantTemp / 100
        self.Coolant_Gauge.rootObject().setProperty('value', gaugeValue)
        try:
            self.kuksa_client.set(
                self.IC.coolantTemp, str(coolantTemp), 'value')
        except Exception as e:
            logging.error(f"Error sending values to kuksa {e}")

    def update_fuelLevel_monitor(self):
        """
        Updates the fuel level monitor with the current fuel level value.
        """
        fuelLevel = int(self.fuelLevel_slider.value())
        FuelGaugeLevel = fuelLevel / 100
        self.Fuel_Gauge.rootObject().setProperty('value', FuelGaugeLevel)
        print(self.Fuel_Gauge.rootObject().property('value'))
        try:
            self.kuksa_client.set(self.IC.fuelLevel, str(fuelLevel))
        except Exception as e:
            logging.error(f"Error sending values to kuksa {e}")

    def hazardBtnClicked(self):
        """
        Handles the hazard button click event.
        """
        hazardIcon = QPixmap(":/Images/Images/hazard.png")
        painter = QPainter(hazardIcon)
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_SourceIn)

        if self.hazardBtn.isChecked():
            color = QtCore.Qt.GlobalColor.yellow
            value = "true"
        else:
            color = QtCore.Qt.GlobalColor.black
            value = "false"

        painter.fillRect(hazardIcon.rect(), color)
        painter.end()
        self.hazardBtn.setIcon(QIcon(hazardIcon))

        self.leftIndicatorBtn.setChecked(self.hazardBtn.isChecked())
        self.rightIndicatorBtn.setChecked(self.hazardBtn.isChecked())

        try:
            self.kuksa_client.set(self.IC.leftIndicator, value, "targetValue")
            self.kuksa_client.set(self.IC.rightIndicator, value, "targetValue")
            self.kuksa_client.set(self.IC.hazard, value, "targetValue")
        except Exception as e:
            logging.error(f"Error sending values to kuksa {e}")

    def leftIndicatorBtnClicked(self):
        """
        Handles the left indicator button click event.
        """
        leftIndicatorIcon = QPixmap(":/Images/Images/left.png")
        painter = QPainter(leftIndicatorIcon)
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_SourceIn)

        if self.leftIndicatorBtn.isChecked():
            color = QtCore.Qt.GlobalColor.green
            value = "true"
        else:
            color = QtCore.Qt.GlobalColor.black
            value = "false"

        painter.fillRect(leftIndicatorIcon.rect(), color)
        painter.end()
        self.leftIndicatorBtn.setIcon(QIcon(leftIndicatorIcon))

        try:
            self.kuksa_client.set(self.IC.leftIndicator, value)
        except Exception as e:
            logging.error(f"Error sending values to kuksa {e}")

    def rightIndicatorBtnClicked(self):
        """
        Handles the right indicator button click event.
        """
        rightIndicatorIcon = QPixmap(":/Images/Images/right.png")
        painter = QPainter(rightIndicatorIcon)
        painter.setCompositionMode(
            QPainter.CompositionMode.CompositionMode_SourceIn)

        if self.rightIndicatorBtn.isChecked():
            color = QtCore.Qt.GlobalColor.green
            value = "true"
        else:
            color = QtCore.Qt.GlobalColor.black
            value = "false"

        painter.fillRect(rightIndicatorIcon.rect(), color)
        painter.end()
        self.rightIndicatorBtn.setIcon(QIcon(rightIndicatorIcon))

        try:
            self.kuksa_client.set(self.IC.rightIndicator, value)
        except Exception as e:
            logging.error(f"Error sending values to kuksa {e}")

    def accelerationBtnPressed(self):
        """
        Handles the acceleration button press event.
        """
        self.startTime = QtCore.QTime.currentTime()
        self.acceleration_timer = QtCore.QTimer()
        self.acceleration_timer.timeout.connect(
            lambda: self.updateSpeedAndEngineRpm("Accelerate"))
        self.acceleration_timer.start(100)

    def accelerationBtnReleased(self):
        if self.Speed_slider.value() <= 0:
            self.acceleration_timer.stop()
        else:
            self.acceleration_timer.timeout.connect(
                lambda: self.updateSpeedAndEngineRpm("Decelerate"))
            self.acceleration_timer.start(100)

    def handle_Script_toggle(self):
        if config.file_playback_enabled():
            if not config.can_interface_enabled():
                self.Script_toggle.showError()
                self.Script_toggle.setChecked(False)
                return
            try:
                self.Playback = CAN_playback()
                self.Playback_connections()
            except Exception as e:
                self.Script_toggle.showError()
                logging.error(f"Error creating playback object {e}")
                return

            if self.Script_toggle.isChecked():
                # start the playback thread
                self.thread = QThread()
                self.Playback.moveToThread(self.thread)
                self.thread.started.connect(self.Playback.playback_messages)
                self.thread.start()
                # hide sliders from the layout, their space will be taken by the playback widgets
                self.Speed_slider.hide()
                self.RPM_slider.hide()

                # set default values for coolent and fuel
                self.coolantTemp_slider.setValue(90)
                self.fuelLevel_slider.setValue(50)

            elif not self.Script_toggle.isChecked():
                self.Playback.stop()
                self.thread.quit()
                self.thread.wait()

                self.Speed_slider.show()
                self.RPM_slider.show()

        else:
            if self.Script_toggle.isChecked():
                self.Speed_slider.setEnabled(False)
                self.RPM_slider.setEnabled(False)
                # self.accelerationBtn.setEnabled(False)
                for button in self.driveGroupBtns.buttons():
                    button.setEnabled(False)
                self.set_Vehicle_RPM(1000)
                self.set_Vehicle_Speed(0)
                self.simulator_running = True
                self.simulator.start()
            else:
                self.simulator.stop()
                self.simulator_running = False
                self.Speed_slider.setEnabled(True)
                self.RPM_slider.setEnabled(True)
                # self.accelerationBtn.setEnabled(True)
                for button in self.driveGroupBtns.buttons():
                    button.setEnabled(True)

    def updateSpeedAndEngineRpm(self, action, acceleration=(60/5)):
        if action == "Accelerate":
            pass
        elif action == "Decelerate":
            acceleration = -acceleration

        currentTime = QtCore.QTime.currentTime()
        duration = self.startTime.msecsTo(currentTime)
        self.current_speed = AccelerationFns.calculate_speed(
            duration, acceleration)
        self.current_rpm = AccelerationFns.calculate_engine_rpm(
            self.current_speed)

        if self.current_speed <= 0:
            self.current_speed = 0
            self.current_rpm = 0
            self.acceleration_timer.stop()

        if self.current_speed >= 240:
            self.current_speed = 240
            self.current_rpm = 0
            self.acceleration_timer.stop()

        self.Speed_slider.setValue(self.current_speed)
        self.RPM_slider.setValue(self.current_rpm)

        self.update_Speed_gauge()
        self.update_RPM_monitor()

    def driveBtnClicked(self):
        gear_mapping = {
            self.driveBtn: "127",
            self.parkBtn: "126",
            self.reverseBtn: "-1",
            self.neutralBtn: "0"
        }

        checked_button = self.driveGroupBtns.checkedButton()

        if checked_button in gear_mapping:
            gear_value = gear_mapping[checked_button]
            # self.accelerationBtn.setEnabled(True)
            self.Speed_slider.setEnabled(checked_button != self.neutralBtn)
            self.RPM_slider.setEnabled(True)
            try:
                self.kuksa_client.set(self.IC.selectedGear, gear_value)
            except Exception as e:
                logging.error(f"Error sending values to kuksa {e}")
        else:
            print("Unknown button checked!")


class AccelerationFns():
    def calculate_speed(time, acceleration) -> int:
        # acceleration = 60 / 5 # acceleration from 0 to 60 in 5 seconds
        time = time / 1000  # convert milliseconds to seconds
        speed = acceleration * time  # calculate speed
        return int(speed)

    def calculate_engine_rpm(speed) -> int:
        wheel_diameter = 0.48  # in meters
        wheel_circumference = wheel_diameter * 3.14  # in meters

        # Adjust the gear ratios to match the desired speed and rpm
        gear_ratios = [3.36, 2.10, 1.48, 1.16, 0.95, 0.75]
        speed = speed * 1000 / 3600  # Convert speed from km/h to m/s
        wheel_rps = speed / wheel_circumference

        current_gear = None
        for i in range(len(gear_ratios)):
            if wheel_rps * gear_ratios[i] < 8000 / 60:
                current_gear = i + 1
                break

        # If no gear is found, use the highest gear
        if current_gear is None:
            current_gear = len(gear_ratios)

        engine_rpm = wheel_rps * gear_ratios[current_gear - 1] * 60

        return int(engine_rpm)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = ICWidget()
    w.show()
    sys.exit(app.exec())
