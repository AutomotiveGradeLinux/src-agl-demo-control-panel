# Copyright (C) 2023 Suchinton Chakravarty
# Copyright (C) 2024 Konsulko Group
#
# SPDX-License-Identifier: Apache-2.0

import os
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QButtonGroup

current_dir = os.path.dirname(os.path.abspath(__file__))

# ========================================

sys.path.append(os.path.dirname(current_dir))


Form, Base = uic.loadUiType(os.path.join(
    current_dir, "../ui/SteeringControls.ui"))

# ========================================


import extras.FeedCAN as feed_can
from Widgets import settings
from extras.KuksaClient import KuksaClient
import res_rc

class Steering_Paths():
    def __init__(self):
        self.switches = {
            "VolumeUp": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.VolumeUp",
                "CAN": "021#FFFFFFFF40000000"},
            "VolumeDown": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.VolumeDown",
                "CAN": "021#FFFFFFFF10000000"},
            "VolumeMute": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.VolumeMute",
                "CAN": "021#FFFFFFFF01000000"},
            "Mode": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.Mode",
                "CAN": "021#FFFFFFFF20000000"},
            "NextTrack": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.Next",
                "CAN": "021#FFFFFFFF08000000"},
            "PreviousTrack": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.Previous",
                "CAN": "021#FFFFFFFF80000000"},
            "Info": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.Info",
                "CAN": "021#FFFFFFFF02000000"},
            "PhoneCall": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.PhoneCall",
                "CAN": "021#FFFFFFFF00010000"},
            "PhoneHangup": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.PhoneHangup",
                "CAN": "021#FFFFFFFF00020000"},
            "Voice": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.Voice",
                "CAN": "021#FFFFFFFF00040000"},
            "LaneDeparture": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.LaneDepartureWarning",
                "CAN": "021#FFFFFFFF00000001"},
            "Horn": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.Horn",
                "CAN": "021#FFFFFFFF00000080"},
            "CruiseEnable": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.CruiseEnable",
                "CAN": "021#FFFFFFFF00008000"},
            "CruiseSet": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.CruiseSet",
                "CAN": "021#FFFFFFFF00001000"},
            "CruiseResume": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.CruiseResume",
                "CAN": "021#FFFFFFFF00004000"},
            "CruiseCancel": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.CruiseCancel",
                "CAN": "021#FFFFFFFF00000800"},
            "CruiseLimit": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.CruiseLimit",
                "CAN": "021#FFFFFFFF00000200"},
            "CruiseDistance": {
                "VSS": "Vehicle.Cabin.SteeringWheel.Switches.CruiseDistance",
                "CAN": "021#FFFFFFFF00000100"}
        }


class SteeringCtrlWidget(Base, Form):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)

        self.Steering = Steering_Paths()
        self.kuksa_client = KuksaClient()
        self.settings = settings

        self.add_buttons()

    def add_buttons(self):

        # Define button groups and actions
        ControlsBtns = [self.VolumeUp,
                        self.VolumeDown,
                        self.Mode,
                        self.VolumeMute,
                        self.NextTrack,
                        self.PreviousTrack,
                        self.Info,
                        self.PhoneCall,
                        self.PhoneHangup,
                        self.Voice,
                        self.LaneDeparture,
                        self.Horn,
                        self.CruiseEnable,
                        self.CruiseSet,
                        self.CruiseResume,
                        self.CruiseCancel,
                        self.CruiseLimit,
                        self.CruiseDistance]

        self.ControlsBtnsGroup = QButtonGroup()

        for btn in ControlsBtns:
            self.ControlsBtnsGroup.addButton(btn)

        self.ControlsBtnsGroup.buttonClicked.connect(self.controls_clicked)

    def controls_clicked(self, button):
        button_clicked = button.objectName()
        signal_type = settings.Steering_Signal_Type
        if signal_type == "VSS":
            self.kuksa_client.set(self.Steering.switches[button_clicked]["VSS"], "true")
            self.kuksa_client.set(self.Steering.switches[button_clicked]["VSS"], "false")
        elif signal_type == "CAN":
            feed_can.send_can_signal(
                self.Steering.switches[button_clicked]["CAN"])
            # Making sure button state goes back to off
            feed_can.send_can_signal("021#FFFFFFFF00000000")


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = SteeringCtrlWidget()
    w.show()
    sys.exit(app.exec())
