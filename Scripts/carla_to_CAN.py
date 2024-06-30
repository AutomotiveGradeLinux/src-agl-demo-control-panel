# Copyright (C) 2024 Suchinton Chakravarty
#
# SPDX-License-Identifier: Apache-2.0

import carla
import math
import can
import cantools
import argparse

# ==============================================================================
# -- CAN -----------------------------------------------------------------------
# ==============================================================================


class CAN(object):
    """
    Represents a Controller Area Network (CAN) interface for sending messages to a vehicle.

    Attributes:
        db (cantools.database.can.Database): The CAN database.
        can_bus (can.interface.Bus): The CAN bus interface.
        speed_message (cantools.database.can.Message): The CAN message for vehicle speed.
        gear_message (cantools.database.can.Message): The CAN message for transmission gear.
        Vehicle_Status_2_message (cantools.database.can.Message): The CAN message for engine speed.
        throttle_message (cantools.database.can.Message): The CAN message for throttle position.
        Vehicle_Status_3_message (cantools.database.can.Message): The CAN message for indicator lights.
        speed_cache (int): The cached vehicle speed.
        throttle_cache (int): The cached throttle position.
        engine_speed_cache (int): The cached engine RPM.
        gear_cache (str): The cached transmission gear.
        lights_cache (str): The cached indicator lights state.
    """

    def __init__(self):
        self.db = cantools.database.load_file('agl-vcar.dbc')
        self.can_bus = can.interface.Bus('vcan0', interface='socketcan')

        self.speed_message = self.db.get_message_by_name('Vehicle_Status_1')
        self.gear_message = self.db.get_message_by_name('Transmission')

        self.Vehicle_Status_2_message = self.db.get_message_by_name(
            'Vehicle_Status_2')
        self.throttle_message = self.db.get_message_by_name('Engine')

        self.Vehicle_Status_3_message = self.db.get_message_by_name(
            'Vehicle_Status_3')

        self.speed_cache = 0
        self.throttle_cache = 0
        self.engine_speed_cache = 0
        self.gear_cache = "P"
        self.lights_cache = None

    def send_car_speed(self, speed):
        """
        Sends the vehicle speed to the CAN bus.

        Args:
            speed (int): The vehicle speed in km/h.
        """
        if speed != 0:
            self.send_gear("D")
        else:
            self.send_gear("P")
        data = self.speed_message.encode({'PT_VehicleAvgSpeed': speed})
        message = can.Message(
            arbitration_id=self.speed_message.frame_id, data=data)
        self.can_bus.send(message)

    def send_gear(self, gear):
        """
        Sends the transmission gear to the CAN bus.

        Args:
            gear (str): The transmission gear ('P', 'R', 'N', 'D').
            Where, 0 = Neutral, 1/2/.. = Forward gears, -1/-2/.. = Reverse gears, 126 = Park, 127 = Drive
        """
        if gear == "P":
            data = self.gear_message.encode({'Gear': 126})
        elif gear == "R":
            data = self.gear_message.encode({'Gear': -1, 'Gear': -2})
        elif gear == "N":
            data = self.gear_message.encode({'Gear': 0})
        elif gear == "D":
            data = self.gear_message.encode({'Gear': 127})
        message = can.Message(
            arbitration_id=self.gear_message.frame_id, data=data)
        self.can_bus.send(message)

    def send_engine_speed(self, engine_speed):
        """
        Sends the engine speed to the CAN bus.

        Args:
            engine_speed (int): The engine speed in RPM.
        """
        data = self.Vehicle_Status_2_message.encode({'PT_FuelLevelPct': 100,
                                                     'PT_EngineSpeed': engine_speed,
                                                     'PT_FuelLevelLow': 0})

        message = can.Message(
            arbitration_id=self.Vehicle_Status_2_message.frame_id, data=data)
        self.can_bus.send(message)

    def send_throttle(self, throttle):
        """
        Sends the throttle position to the CAN bus.

        Args:
            throttle (int): The throttle position in percentage.
        """
        data = self.throttle_message.encode({'ThrottlePosition': throttle})
        message = can.Message(
            arbitration_id=self.throttle_message.frame_id, data=data)
        self.can_bus.send(message)

    def send_indicator(self, indicator):
        """
        Sends the indicator lights state to the CAN bus.

        Args:
            indicator (str): The indicator lights state ('LeftBlinker', 'RightBlinker', 'HazardLights').
        """
        # Mapping indicator names to signal values
        indicators_mapping = {
            'LeftBlinker': {'PT_LeftTurnOn': 1},
            'RightBlinker': {'PT_RightTurnOn': 1},
            'HazardLights': {'PT_HazardOn': 1}
        }

        # Default signal values
        signals = {'PT_HazardOn': 0, 'PT_LeftTurnOn': 0, 'PT_RightTurnOn': 0}

        # Update signals based on the indicator argument
        signals.update(indicators_mapping.get(indicator, {}))

        # Encode and send the CAN message
        data = self.Vehicle_Status_3_message.encode(signals)
        message = can.Message(
            arbitration_id=self.Vehicle_Status_3_message.frame_id, data=data)
        self.can_bus.send(message)

    def send_can_message(self, speed=0, rpm=0, throttle=0, gear="P", lights=None):
        """
        Sends a complete set of CAN messages for vehicle control.

        Args:
            speed (int): The vehicle speed in km/h.
            rpm (int): The engine speed in RPM.
            throttle (int): The throttle position in percentage.
            gear (str): The transmission gear ('P', 'R', 'N', 'D').
        """
        if speed != self.speed_cache:
            self.send_car_speed(speed)
            self.speed_cache = speed

        if throttle != self.throttle_cache:
            self.send_throttle(throttle)
            self.throttle_cache = throttle

        if gear != self.gear_cache:
            if gear == 1:
                self.send_gear("D")
            if gear == -1:
                self.send_gear("R")
            if gear == 0:
                self.send_gear("N")
            self.gear_cache = gear

        if rpm != self.engine_speed_cache:
            self.send_engine_speed(rpm)
            self.engine_speed_cache = rpm

        if lights is not None and lights != self.lights_cache:
            self.send_indicator(lights)
            self.lights_cache = lights


def main(host='127.0.0.1', port=2000):
    parser = argparse.ArgumentParser(description='Carla to CAN Converter')
    parser.add_argument('--host', default='127.0.0.1', help='IP of the host server')
    parser.add_argument('--port', default=2000, type=int, help='TCP port to listen to')
    args = parser.parse_args()

    client = carla.Client(args.host, args.port)
    client.set_timeout(2.0)

    world = client.get_world()

    can = CAN()

    player_vehicle = None

    for actor in world.get_actors():
        if 'vehicle' in actor.type_id and actor.attributes['role_name'] == 'hero':
            player_vehicle = actor
            break

    if player_vehicle is None:
        print("Player vehicle not found.")
        return

    try:

        speed_kmh_cache = None
        engine_rpm_cache = None
        throttle_cache = None
        gear_cache = None
        lights_cache = None

        while True:
            control = player_vehicle.get_control()
            physics_control = player_vehicle.get_physics_control()
            velocity = player_vehicle.get_velocity()
            gear = player_vehicle.get_control().gear
            speed_kmh = 3.6 * \
                math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)

            engine_rpm = physics_control.max_rpm * control.throttle

            if gear > 0:
                gear_ratio = physics_control.forward_gears[min(
                    gear, len(physics_control.forward_gears)-1)].ratio
                engine_rpm = physics_control.max_rpm * control.throttle / gear_ratio
            else:
                engine_rpm = physics_control.max_rpm * control.throttle

            lights = player_vehicle.get_light_state()

            # if any values have changed, try to send the CAN message
            if (speed_kmh != speed_kmh_cache or
                engine_rpm != engine_rpm_cache or
                control.throttle != throttle_cache or
                gear != gear_cache or
                lights != lights_cache):

                speed_kmh_cache = speed_kmh
                engine_rpm_cache = engine_rpm
                throttle_cache = control.throttle
                gear_cache = gear
                lights_cache = lights

                can.send_can_message(speed_kmh, engine_rpm,
                                     control.throttle, gear, lights)

    except Exception as e:
        print(
            f"An error occurred: {e}. The CARLA simulation might have stopped.")
    finally:
        if can.can_bus is not None:
            can.can_bus.shutdown()
            print("CAN bus properly shut down.")


if __name__ == "__main__":
    main()
