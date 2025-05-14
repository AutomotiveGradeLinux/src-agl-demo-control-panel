# Copyright (C) 2024 Suchinton Chakravarty
#
# SPDX-License-Identifier: Apache-2.0

import can
import time
from rich.console import Console
import os
import argparse
from PyQt6.QtCore import QThread, pyqtSignal
import cantools
import sys
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from extras import config

class CAN_playback(QThread):
    finished = pyqtSignal()

    speedUpdate = pyqtSignal(int)
    gearUpdate = pyqtSignal(str)
    engineSpeedUpdate = pyqtSignal(int)
    throttleUpdate = pyqtSignal(int)
    indicatorUpdate = pyqtSignal(str)

    try:
        playbackFile = config.get_playback_file()
    except Exception as e:
        logging.error("Error loading playback file:", e)
        # playbackFile = os.path.join(current_dir, "can_messages.txt")

    def __init__(self, interface='vcan0'):
        super(CAN_playback, self).__init__()
        self._running = False
        self.console_mode = False
        self.interface = interface
        self.bus = can.interface.Bus(interface='socketcan', channel=self.interface, bitrate=500000)
        self.output_file = self.playbackFile
        
        # Load the DBC file
        self.db = cantools.database.load_file(os.path.join(os.path.dirname(__file__), 'agl-vcar.dbc'))

        # Create a mapping of relevant messages
        self.message_map = {
            'Vehicle_Status_1': self.decode_speed,
            'Transmission': self.decode_gear,
            'Vehicle_Status_2': self.decode_engine_speed,
            'Engine': self.decode_throttle,
            'Vehicle_Status_3': self.decode_indicators
        }

    def write_to_file(self, messages):
        with open(self.output_file, 'w') as file:
            for msg in messages:
                file.write(f"{msg.timestamp},{msg.arbitration_id},{msg.dlc},{','.join(map(lambda b: f'0x{b:02x}', msg.data))}\n")

    def run(self):
        """Override run method to handle playback messages."""
        if os.path.exists(self.output_file):
            messages = []
            with open(self.output_file, 'r') as file:
                for line in file:
                    parts = line.strip().split(',', 3)
                    timestamp, arbitration_id, dlc, data_str = parts
                    data_bytes = [int(byte, 16) for byte in data_str.split(',') if byte]
                    
                    msg = can.Message(
                        timestamp=float(timestamp),
                        arbitration_id=int(arbitration_id, 0),
                        dlc=int(dlc),
                        data=data_bytes
                    )
                    messages.append(msg)
            self.replay_messages(messages)

    def start_playback(self):
        """Start playback if not already running."""
        if not self._running:
            self._running = True
            self.start()  # Start the QThread


    def stop_playback(self):
        """Stop playback."""
        if self._running:
            self.reset()
            
            # Wait for thread to finish before shutting down the bus
            self.wait(1000)
                
            self.finished.emit()

    def reset(self):
        """Reset the playback."""
        self._running = False
        self.speedUpdate.emit(0)
        self.gearUpdate.emit("N")
        self.engineSpeedUpdate.emit(0)
        self.throttleUpdate.emit(0)
        self.indicatorUpdate.emit("HazardOff")

    def replay_messages(self, messages):
        """Replay CAN messages."""
        # self._running = True
        try:
            start_time = messages[0].timestamp  
        except IndexError:
            logging.error("No messages to replay from file:", self.output_file)
            self.reset()

        for msg in messages:
            if not self._running:  # Check if playback should stop
                return
            
            delay = msg.timestamp - start_time
            self.bus.send(msg)
            
            # Decode and emit signals for relevant messages
            if msg.arbitration_id == self.db.get_message_by_frame_id(msg.arbitration_id).frame_id:
                message_name = self.db.get_message_by_frame_id(msg.arbitration_id).name
                if message_name in self.message_map:
                    decoded_data = self.decode_message(message_name, msg.data)
                    self.message_map[message_name](decoded_data)
            
            time.sleep(delay)
            start_time = msg.timestamp

    def decode_message(self, message_name, data):
        message = self.db.get_message_by_name(message_name)
        return message.decode(data)

    def decode_speed(self, decoded_data):
        speed = int(decoded_data['PT_VehicleSpeed'])
        self.speedUpdate.emit(speed)

    def decode_gear(self, decoded_data):
        gear_value = int(decoded_data['Gear'])
        if gear_value == 126:
            gear = "P"
        elif gear_value == 127:
            gear = "D"
        elif gear_value == -1 or gear_value == -2:
            gear = "R"
        elif gear_value == 0:
            gear = "N"
        else:
            gear = f"{gear_value}"
        self.gearUpdate.emit(gear)

    def decode_engine_speed(self, decoded_data):
        engine_speed = int(decoded_data['PT_EngineSpeed'])
        self.engineSpeedUpdate.emit(engine_speed)

    def decode_throttle(self, decoded_data):
        throttle_position = int(decoded_data['ThrottlePosition'])
        self.throttleUpdate.emit(throttle_position)

    def decode_indicators(self, decoded_data):
        if decoded_data['PT_HazardOn'] == 1:
            self.indicatorUpdate.emit('HazardOn')
        if decoded_data['PT_HazardOn'] == 0:
            self.indicatorUpdate.emit('HazardOff')

        if decoded_data['PT_LeftTurnOn'] == 1:
            self.indicatorUpdate.emit('LeftBlinkerOn')
        if decoded_data['PT_LeftTurnOn'] == 0:
            self.indicatorUpdate.emit('LeftBlinkerOff')

        if decoded_data['PT_RightTurnOn'] == 1:
            self.indicatorUpdate.emit('RightBlinkerOn')
        if decoded_data['PT_RightTurnOn'] == 0:
            self.indicatorUpdate.emit('RightBlinkerOff')

    def capture_can_messages(self):
        messages = []
        
        if self.console_mode:
            console = Console()
            console.print(f"Capturing CAN messages on {self.interface}. Press Ctrl+C to stop.")
        

        try:
            while True:
                message = self.bus.recv()
                if message is not None:
                    messages.append(message)
        except KeyboardInterrupt:
            console.print("Capture stopped.")

        return messages

def main():
    from rich.console import Console
    from rich.prompt import Prompt

    parser = argparse.ArgumentParser(description='CAN Message Capture and Playback Tool')
    parser.add_argument('--interface', '-i', type=str, default='vcan0', help='Specify the CAN interface (default: vcan0)')
    args = parser.parse_args()

    can_tool = CAN_playback(interface=args.interface)
    can_tool.console_mode = True

    console = Console()
    while True:
        if can_tool._running:
            console.print("Playback in progress. Please stop playback before capturing new messages.")
            # ask for input 1 to stop playback
            choice = Prompt.ask("Enter your choice", choices=['1'])
            if choice == '1':
                can_tool.stop_playback()
                console.print("Playback stopped. Ready to capture new messages.")
                continue
        else:
            console.print("\n[bold]CAN Message Capture and Playback[/bold]")
            console.print("1. Capture CAN messages")
            console.print("2. Replay captured messages")
            console.print("3. Exit")
    
            choice = Prompt.ask("Enter your choice", choices=['1', '2', '3'])
    
            if choice == '1':
                messages = can_tool.capture_can_messages()
                console.print(f"Captured {len(messages)} messages.")
                can_tool.write_to_file(messages)
                console.print(f"CAN messages written to {can_tool.output_file}")
            elif choice == '2':
                if os.path.exists(can_tool.output_file):
                    console.print("Replaying captured messages...")
                    can_tool.start_playback()
                    console.print("Replay completed.")
                else:
                    console.print(f"No captured messages found in {can_tool.output_file}")
                
            else:
                console.print("Exiting...")
                break

if __name__ == "__main__":
    main()
