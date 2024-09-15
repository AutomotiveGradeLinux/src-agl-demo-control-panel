import os
import sys
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton
import requests
from urllib.parse import urljoin

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

Form, Base = uic.loadUiType(os.path.join(current_dir, "../ui/Keypad.ui"))

import res_rc

class KeypadWidget(Base, Form):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        self.host = "localhost"
        self.port = 8080

        # Mapping of keys to API endpoints
        self.key_endpoints = {
            "Key_1": "/cgi-bin/flutter.cgi",
            "Key_2": "/cgi-bin/qt.cgi",
            "Key_3": "/cgi-bin/momi.cgi",
            "Key_4": "/cgi-bin/bomb.cgi",
            "Key_5": "",  # This key won't do anything
        }

        # Connect all keys to the same slot
        for key_name in self.key_endpoints.keys():
            key_button = self.findChild(QPushButton, key_name)
            key_button.clicked.connect(lambda _, x=key_name: self.trigger_api(x))

    def trigger_api(self, key_name):
        endpoint = self.key_endpoints[key_name]
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
