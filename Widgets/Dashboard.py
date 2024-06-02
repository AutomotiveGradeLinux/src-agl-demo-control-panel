# Copyright (C) 2023 Suchinton Chakravarty
# Copyright (C) 2024 Konsulko Group
#
# SPDX-License-Identifier: Apache-2.0

import os
import sys
from PyQt6 import uic
from PyQt6 import QtCore, QtWidgets
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import *
from PyQt6.QtSvg import *
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

current_dir = os.path.dirname(os.path.abspath(__file__))

# ========================================

sys.path.append(os.path.dirname(current_dir))


Form, Base = uic.loadUiType(os.path.join(current_dir, "../ui/Dashboard.ui"))

# ========================================

from extras import config
import res_rc

class Dashboard(Base, Form):
    """
    A class representing the dashboard widget.

    Attributes:
    - tileClickedSignal: A PyQtSignal emitted when a tile is clicked.

    Methods:
    - __init__(self, parent=None): Initializes the Dashboard widget.
    - set_icon(self, tile, size): Sets the icon for the given tile.
    - tile_clicked(self, tile): Handles the tile click event.
    """

    tileClickedSignal = pyqtSignal()

    def __init__(self, parent=None):
        """
        Initializes the Dashboard widget.

        Parameters:
        - parent: The parent widget. Defaults to None.
        """
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)

        Dashboard_tiles = (self.DB_IC_Tile,
                           self.DB_HVAC_Tile,
                           self.DB_Steering_Tile,
                           self.DB_Settings_Tile)

        DashboardTiles = QtWidgets.QButtonGroup(self)

        DashboardTiles.buttonClicked.connect(self.tile_clicked)

        for tile in Dashboard_tiles:
            enabled = True
            if tile == self.DB_HVAC_Tile and not config.hvac_enabled():
                self.DB_HVAC_Tile.setEnabled(False)
                self.DB_HVAC_Tile.setStyleSheet("background-color : darkGray; color : gray")
                enabled = False
            if tile == self.DB_Steering_Tile and not config.steering_wheel_enabled():
                self.DB_Steering_Tile.setEnabled(False)
                self.DB_Steering_Tile.setStyleSheet("background-color : darkGray; color: gray")
                enabled = False

            self.set_icon(tile, 90)
            DashboardTiles.addButton(tile)

    def set_icon(self, tile, icon_size):
        icon_mappings = {
            self.DB_IC_Tile: {
                "normal": ":/Carbon_Icons/carbon_icons/meter.svg",
                "disabled": ":/Carbon_Icons/carbon_icons/meter-disabled.svg"
            },
            self.DB_HVAC_Tile: {
                "normal": ":/Carbon_Icons/carbon_icons/windy--strong.svg",
                "disabled": ":/Carbon_Icons/carbon_icons/windy--strong-disabled.svg"
            },
            self.DB_Steering_Tile: {
                "normal": ":/Images/Images/steering-wheel.svg",
                "disabled": ":/Images/Images/steering-wheel-disabled.svg"
            },
            self.DB_Settings_Tile: {
                "normal": ":/Carbon_Icons/carbon_icons/settings.svg",
                "disabled": ":/Carbon_Icons/carbon_icons/settings.svg"  # Assuming the same icon for simplicity
            }
        }

        icon_key = "disabled" if not tile.isEnabled() else "normal"
        file_path = icon_mappings.get(tile, {}).get(icon_key)

        if not file_path:
            return

        icon = QIcon(file_path)
        tile.setIcon(icon)
        tile.setIconSize(QSize(icon_size, icon_size))

    def tile_clicked(self, tile):
        """
        Handles the tile click event.

        Parameters:
        - tile: The tile that was clicked.
        """
        if tile == self.DB_IC_Tile:
            self.parent().setCurrentIndex(1)
        elif tile == self.DB_HVAC_Tile:
            self.parent().setCurrentIndex(2)
        elif tile == self.DB_Steering_Tile:
            self.parent().setCurrentIndex(3)
        elif tile == self.DB_Settings_Tile:
            self.parent().setCurrentIndex(4)

        self.tileClickedSignal.emit()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    w = Dashboard()
    w.show()
    sys.exit(app.exec())
