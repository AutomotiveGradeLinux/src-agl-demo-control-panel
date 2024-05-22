# Copyright (C) 2023 Suchinton Chakravarty
# Copyright (C) 2024 Konsulko Group
#
# SPDX-License-Identifier: Apache-2.0

import logging
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal
from . import Kuksa_Instance as kuksa_instance
import threading

class KuksaClient(QThread):
    """
    A class to handle sending values to Kuksa.

    Attributes:
    -----------
    stop_flag : bool
        A flag to stop the thread.
    kuksa : kuksa_instance.KuksaClientSingleton.instance()
        An instance of the Kuksa client.
    client : kuksa_instance.KuksaClientSingleton.instance().client
        A client object to interact with the Kuksa server.
    """
    
    sending_values = pyqtSignal()
    finished_sending_values = pyqtSignal()

    def __init__(self, parent=None):
        """
        Constructs all the necessary attributes for the FeedKuksa object.

        Parameters:
        -----------
        parent : QObject
            The parent object of the FeedKuksa object.
        """
        QThread.__init__(self, parent)
        self.stop_flag = False
        self.kuksa = None
        self.client = None

    def run(self):
        """
        Starts the thread and sets the instance of the Kuksa client.
        """
        logging.info("Starting thread")
        self.set_instance()

    def stop(self):
        """
        Stops the thread.
        """
        self.stop_flag = True

        logging.info("Stopping thread")

    def set_instance(self):
        """
        Sets the instance of the Kuksa client.
        """
        self.kuksa = kuksa_instance.KuksaClientSingleton.instance()
        self.client = self.kuksa.get_client()

    def set(self, path=None, value=None, attribute=None):
        """
        Sets VSS value.

        Parameters:
        -----------
        path : str
            The VSS signal path.
        value : str
            The value to be set.
        attribute : str
            The value attribute ("value" or "targetValue" (for actuators)).

        Raises:
        -------
        Exception
            If there is an error setting the value.
        """
        
        if self.client is None:
            #logging.error("Kuksa client is None, try reconnecting")
            return

        if not self.client.checkConnection():
            logging.error("Client is not connected, try reconnecting")
            threading.Thread(target=self.set_instance).start()
            return

        try:
            if attribute is not None:
                self.sending_values.emit()
                self.client.setValue(path, value, attribute)
                self.finished_sending_values.emit()
            else:
                self.sending_values.emit()
                self.client.setValue(path, value)
                self.finished_sending_values.emit()
        except Exception as e:
            logging.error(f"Error sending values to kuksa {e}")
            threading.Thread(target=self.set_instance).start()

    def setValues(self, values : dict[str, any] = None):
        """
        Sets VSS values.

        Parameters:
        -----------
        values : Dict[str, Any]
            The values to be set.

        Raises:
        -------
        Exception
            If there is an error setting the values.
        """
        
        if self.client is None:
            #logging.error("Kuksa client is None, try reconnecting")
            return

        if not self.client.checkConnection():
            logging.error("Client is not connected, try reconnecting")
            threading.Thread(target=self.set_instance).start()
            return

        try:
            self.sending_values.emit()
            self.client.setValues(values)
        except Exception as e:
            logging.error(f"Error sending values to kuksa {e}")
            threading.Thread(target=self.set_instance).start()
