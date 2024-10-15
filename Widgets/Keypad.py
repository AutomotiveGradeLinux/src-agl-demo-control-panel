import os
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QToolButton, QApplication, QWidget
from PyQt6.QtGui import QPixmap, QIcon
import requests

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

Form, Base = uic.loadUiType(os.path.join(current_dir, "../ui/Keypad.ui"))

import res_rc
from extras import config

class KeypadWidget(Base, Form):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)

        # Load configuration
        self.host, self.port = config.get_keypad_config()
        
        frame = self.findChild(QWidget, "frame")

        # Mapping of keys to API endpoints and button labels
        self.key_endpoints = {
            "Key_1": ("/cgi-bin/flutter.cgi", "Flutter Demo"),
            "Key_2": ("/cgi-bin/qt.cgi", "Qt Demo"),
            "Key_3": ("/cgi-bin/momi.cgi", "Momi Demo"),
            "Key_4": ("/cgi-bin/bomb.cgi", "Bomb Demo")
        }

        # Connect all keys to the same slot and configure buttons
        for key_name, (endpoint, label) in self.key_endpoints.items():
            key_button = self.findChild(QToolButton, key_name)
            key_button.setObjectName(key_name)  # Set button name
            
            # Set button label
            key_button.setText(label)
            # set font size and style based on height of the button
            font = key_button.font()
            font.setPointSize(int(key_button.height()))
            font.setBold(True)
            font.setItalic(True)
            key_button.setFont(font)

            # place the label under the icon
            # key_button.setIconSize(key_button.size())


            # Connect button click to API trigger
            key_button.clicked.connect(lambda _, x=key_name: self.trigger_api(x))

        # Hide unused keys based on configuration
        keys_to_hide = config.get_keypad_keys_to_hide()
        for key_name in keys_to_hide:
            key_button = self.findChild(QToolButton, "Key_" + key_name)
            key_button.hide()

    def trigger_api(self, key_name):
        endpoint = self.key_endpoints[key_name][0]  # Get the endpoint from the tuple
        if endpoint:
            url = f"http://{self.host}:{self.port}{endpoint}"
            try:
                response = requests.get(url, timeout=5)
                response.raise_for_status()
                print(f"API triggered successfully: {url}")
            except requests.exceptions.RequestException as e:
                print(f"Error triggering API: {str(e)}")
        else:
            print("No action defined for this key.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = KeypadWidget()
    w.show()
    sys.exit(app.exec())