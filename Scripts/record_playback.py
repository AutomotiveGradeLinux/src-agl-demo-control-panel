# Copyright (C) 2024 Suchinton Chakravarty
#
# SPDX-License-Identifier: Apache-2.0

import can
import time
from rich.console import Console
import os
import argparse

class CAN_playback:
    def __init__(self, interface='vcan0'):
        """
        Initialize the CAN Tool with the specified interface.

        Args:
            interface (str): The CAN interface name (default: 'vcan0')
        """
        self.console_mode = False
        self.interface = interface
        self.bus = can.interface.Bus(interface='socketcan', channel=self.interface, bitrate=500000)
        self.output_file = os.path.join(os.path.dirname(__file__), 'can_messages.txt')

    def write_to_file(self, messages):
        """
        Write captured CAN messages to a file.

        Args:
            messages (list): List of can.Message objects to write
        """
        with open(self.output_file, 'w') as file:
            for msg in messages:
                file.write(f"{msg.timestamp},{msg.arbitration_id},{msg.dlc},{','.join(map(lambda b: f'0x{b:02x}', msg.data))}\n")

    def playback_messages(self):
        if os.path.exists(self.output_file):
                #console.print("Replaying captured messages...")
                messages = []
                with open(self.output_file, 'r') as file:
                    for line in file:
                        parts = line.strip().split(',', 3)  # Split into at most 4 parts
                        timestamp, arbitration_id, dlc, data_str = parts
                        # Extract the data bytes, removing '0x' and splitting by ','
                        data_bytes = [int(byte, 16) for byte in data_str.split(',') if byte]
                        
                        msg = can.Message(
                            timestamp=float(timestamp),
                            arbitration_id=int(arbitration_id, 0),
                            dlc=int(dlc),
                            data=data_bytes
                        )
                        messages.append(msg)
                self.replay_messages(messages)
    
    def stop(self):
        self._running = False
        if self.bus is not None:
            self.bus.shutdown()

    def replay_messages(self, messages):
        """
        Replay CAN messages on the specified bus.

        Args:
            messages (list): List of can.Message objects to replay
        """
        self._running = True
        start_time = messages[0].timestamp
        for msg in messages:
            delay = msg.timestamp - start_time
            self.bus.send(msg)
            time.sleep(delay)
            start_time = msg.timestamp
            if self._running == False:  return

    def capture_can_messages(self):
        """
        Capture CAN messages from the specified bus.

        Returns:
            list: List of captured can.Message objects
        """
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

    parser = argparse.ArgumentParser(description='CAN Message Capture and Replay Tool')
    parser.add_argument('--interface', '-i', type=str, default='vcan0', help='Specify the CAN interface (default: vcan0)')
    args = parser.parse_args()

    # Initialize the CAN Tool with the specified interface
    can_tool = CAN_playback(interface=args.interface)
    can_tool.console_mode = True

    console = Console()
    while True:
        console.print("\n[bold]CAN Message Capture and Replay[/bold]")
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
                can_tool.playback_messages()
                console.print("Replay completed.")
            else:
                console.print(f"No captured messages found in {can_tool.output_file}")
            
            

        else:
            console.print("Exiting...")
            break

if __name__ == "__main__":
    main()

