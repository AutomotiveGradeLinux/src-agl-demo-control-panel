# Copyright (C) 2023 Suchinton Chakravarty
# Copyright (C) 2024 Konsulko Group
#
# SPDX-License-Identifier: Apache-2.0

import logging
import math
import random
import time
import threading
from PyQt5.QtCore import QObject, pyqtSignal
from extras.KuksaClient import KuksaClient

class VehicleSimulator(QObject):
    # Define signals for updating speed and rpm
    speed_changed = pyqtSignal(int)
    rpm_changed = pyqtSignal(int)

    DEFAULT_IDLE_RPM = 1000
    # NOTE: Highway by Nuremberg Messe
    DEFAULT_STARTING_LAT = 49.416410
    DEFAULT_STARTING_LON = 11.110604

    def __init__(self):
        super().__init__()
        self.running = False
        self.lock = threading.Lock()
        self.thread = None
        self.kuksa_client = KuksaClient()
        self.freq = 10
        self.vehicle_speed = 0
        self.engine_speed = self.DEFAULT_IDLE_RPM
        self.latitude = self.DEFAULT_STARTING_LAT
        self.longitude = self.DEFAULT_STARTING_LON
        self.count = 0

        random.seed()

    def start(self):
        if not self.running:
            self.kuksa_client.set_instance()
            self.reset()
            self.running = True
            if not self.thread.is_alive():
                self.thread.start()

    def stop(self):
        self.running = False

    def reset(self):
        with self.lock:
            self.vehicle_speed = 0
            self.engine_speed = self.DEFAULT_IDLE_RPM
            self.latitude = self.DEFAULT_STARTING_LAT
            self.longitude = self.DEFAULT_STARTING_LON
            self.count = 0
            self.thread = threading.Thread(target=self.run)

    def run(self):
        while self.running:
            if not self.running:
                break

            self.set_signal("Vehicle.Powertrain.Transmission.SelectedGear", 127)

            # Simulate acceleration and update speed and rpm
            self.accelerate(60, 1800, 3)
            self.accelerate(65, 1700, 1)
            self.accelerate(80, 2500, 6)
            self.accelerate(100, 3000, 4)
            self.brake(80, 3000, 3)
            self.accelerate(104, 4000, 6)
            self.brake(40, 2000, 4)
            self.accelerate(90, 3000, 5)
            self.brake(1, 650, 5)

            self.set_signal("Vehicle.Powertrain.Transmission.SelectedGear", 126)

            # Ensure reset is called when not in cruise mode
            if not self.running:
                self.reset()

            time.sleep(5)

    def accelerate(self, target_speed, target_rpm, duration):
        if target_speed <= self.vehicle_speed:
            return
        v = (target_speed - self.vehicle_speed) / (duration * self.freq)
        r = (target_rpm - self.engine_speed) / (duration * self.freq)
        while self.vehicle_speed < target_speed and self.running:
            with self.lock:
                self.vehicle_speed += v
                self.engine_speed += r
                self.speed_changed.emit(int(self.vehicle_speed))
                self.rpm_changed.emit(int(self.engine_speed))
                updates = {}
                updates["Vehicle.Speed"] = self.vehicle_speed
                updates["Vehicle.Powertrain.CombustionEngine.Speed"] = self.engine_speed
                self.simulate_position(self.vehicle_speed, v, False, updates)
                self.count = self.count + 1
                if self.count > 1:
                    self.set_signals(updates)
                    self.count = 0
            time.sleep(1 / self.freq)

    def brake(self, target_speed, target_rpm, duration):
        if target_speed >= self.vehicle_speed:
            return
        v = (self.vehicle_speed - target_speed) / (duration * self.freq)
        r = (self.engine_speed - target_rpm) / (duration * self.freq)
        while self.vehicle_speed > target_speed and self.running:
            with self.lock:
                self.vehicle_speed -= v
                self.engine_speed -= r
                self.speed_changed.emit(int(self.vehicle_speed))
                self.rpm_changed.emit(int(self.engine_speed))
                updates = {}
                updates["Vehicle.Speed"] = self.vehicle_speed
                updates["Vehicle.Powertrain.CombustionEngine.Speed"] = self.engine_speed
                self.simulate_position(self.vehicle_speed, v, True, updates)
                self.count = self.count + 1
                if self.count > 1:
                    self.set_signals(updates)
                    self.count = 0
            time.sleep(1 / self.freq)

    def increase(self, bycruise=True):
        if self.CRUISEACTIVE:
            target_speed = self.vehicle_speed + 5
            target_rpm = self.engine_speed * 1.1
            self.accelerate(target_speed, target_rpm, 2, bycruise)

    def decrease(self, bycruise=True):
        if self.CRUISEACTIVE:
            target_speed = self.vehicle_speed - 5
            target_rpm = self.engine_speed * 0.9
            self.brake(target_speed, target_rpm, 2, bycruise)

    def resume(self, bycruise=True):
        target_speed = self.CRUISESPEED
        target_rpm = self.CRUISERPM
        current_speed = self.get_vehicle_speed()
        if target_speed > current_speed:
            self.accelerate(target_speed, target_rpm, 2, bycruise)
        else:
            self.brake(target_speed, target_rpm, 2, bycruise)

    def set_signal(self, signal, value):
        try:
            self.kuksa_client.set(signal, value, 'value')
        except Exception as e:
            logging.error(f"Error sending value to kuksa {e}")

    def set_signals(self, values):
        try:
            self.kuksa_client.setValues(values)
        except Exception as e:
            logging.error(f"Error sending values to kuksa {e}")

    def simulate_position(self, speed_current, speed_delta, braking, updates):
        # From https://stackoverflow.com/questions/1253499/simple-calculations-for-working-with-lat-lon-and-km-distance
        latKmPerDegree = 110.574
        lonKmPerDegree = 111.320 * math.cos((self.latitude * math.pi) / (180))
        time_seconds = 1 / self.freq
        self.latitude += (speed_current * 0.7 * time_seconds / 3600) / latKmPerDegree
        self.longitude += (speed_current * 0.3 * time_seconds / 3600) / lonKmPerDegree

        accelX = (speed_delta * 1000 / 3600) * self.freq
        throttlePosition = accelX / 6 * 100
        brakePosition = 0
        if throttlePosition > 100:
            throttlePosition = 100
        if braking:
            brakePosition = throttlePosition
            throttlePosition = 0
            accelX = -accelX
        accelY = random.randrange(-150, 150) / 100.0
        accelZ = random.randrange(-100, 100) / 100.0

        pitch = random.randrange(-1000, 1000) / 300.0
        roll = random.randrange(-1000, 1000) / 300.0
        yaw = random.randrange(-1000, 1000) / 300.0

        steeringAngle = random.randrange(-90, 90)

        updates["Vehicle.OBD.ThrottlePosition"] = throttlePosition
        updates["Vehicle.Chassis.Brake.PedalPosition"] = brakePosition
        updates["Vehicle.Chassis.SteeringWheel.Angle"] = steeringAngle
        updates["Vehicle.CurrentLocation.Latitude"] = self.latitude
        updates["Vehicle.CurrentLocation.Longitude"] = self.longitude
        updates["Vehicle.Acceleration.Lateral"] = accelX
        updates["Vehicle.Acceleration.Longitudinal"] = accelY
        updates["Vehicle.Acceleration.Vertical"] = accelZ
        updates["Vehicle.AngularVelocity.Pitch"] = pitch
        updates["Vehicle.AngularVelocity.Roll"] = roll
        updates["Vehicle.AngularVelocity.Yaw"] = yaw
        
