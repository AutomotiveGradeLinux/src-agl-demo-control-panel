"""
   Copyright 2023 Suchinton Chakravarty

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import os
import platform
import can
from configparser import ConfigParser
import logging

python_version = f"python{'.'.join(platform.python_version_tuple()[:2])}"


def check_paths(*paths):
    return {path: os.path.exists(path) for path in paths}


USER_CONFIG_PATH = os.path.join(os.path.expanduser("~"),
                                ".local/share/agl-demo-control-panel/config.ini")

CONFIG_PATHS = check_paths(
    USER_CONFIG_PATH,
    "/etc/agl-demo-control-panel/config.ini",
    "/etc/agl-demo-control-panel.ini",
    os.path.abspath(os.path.join(os.path.dirname(__file__), 'config.ini'))
)

CA_PATHS = check_paths(
    "/etc/kuksa-val/CA.pem",
    f"/usr/lib/{python_version}/site-packages/kuksa_client/kuksa_server_certificates/CA.pem",
    os.path.abspath(os.path.join(os.path.dirname(
        __file__), "../assets/cert/CA.pem"))
)

WS_TOKEN_PATHS = check_paths(
    f"/usr/lib/{python_version}/site-packages/kuksa_client/kuksa_server_certificates/jwt/super-admin.json.token",
    os.path.join(os.path.expanduser(
        "~"), f".local/lib/{python_version}/site-packages/kuksa_client/kuksa_server_certificates/jwt/super-admin.json.token")
)

GRPC_TOKEN_PATHS = check_paths(
    os.path.abspath(os.path.join(os.path.dirname(__file__),
                    "../assets/token/grpc/actuate-provide-all.token"))
)

config = ConfigParser()
config_path = next((path for path, exists in CONFIG_PATHS.items() if exists), None)
if config_path:
    config.read(config_path)

PLAYBACK_FILE_PATHS = check_paths(
    config.get('default', 'file-playback-path', fallback=None),
    "/home/agl-driver/can_messages.txt",
    "/etc/agl-demo-control-panel/can_messages.txt",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../assets/can_messages.txt"))
)

CA_PATH = next((path for path, exists in CA_PATHS.items() if exists), None)
WS_TOKEN = next((path for path, exists in WS_TOKEN_PATHS.items() if exists), None)
GRPC_TOKEN = next((path for path, exists in GRPC_TOKEN_PATHS.items() if exists), None)
PLAYBACK_FILE = next((path for path, exists in PLAYBACK_FILE_PATHS.items() if exists), None)

KUKSA_CONFIG = {}
KUKSA_TOKEN = None

def load_config():
    """
    Initializes configuration from the config.ini file.

    Args:

    Returns:
        Tuple[str, Dict[Union[str, bool]], str]: A tuple containing a dictionary containing
        the configuration option and the token to use for the selected protocol.
    """
    global KUKSA_CONFIG, KUKSA_TOKEN
    KUKSA_CONFIG.clear()

    if config.has_section('vss-server'):
        KUKSA_CONFIG['ip'] = config['vss-server']['ip']
        KUKSA_CONFIG['port'] = config['vss-server']['port']
        KUKSA_CONFIG['protocol'] = config['vss-server']['protocol']
        KUKSA_CONFIG['insecure'] = False if config['vss-server']['insecure'] == 'False' else True

        if config.has_option('vss-server', 'cacert'):
            KUKSA_CONFIG['cacertificate'] = config['vss-server']['cacert'] if os.path.exists(
                config['vss-server']['cacert']) else CA_PATH
        else:
            KUKSA_CONFIG['cacertificate'] = None

        KUKSA_CONFIG['tls_server_name'] = config['vss-server']['tls_server_name']

        if config.has_option('vss-server', 'token'):
            if config['vss-server']['token'] == 'default':
                KUKSA_TOKEN = get_default_token(KUKSA_CONFIG['protocol'])
            elif os.path.exists(config['vss-server']['token']):
                KUKSA_TOKEN = config['vss-server']['token']
        else:
            ValueError(
                f"Token file {config['vss-server']['token']} not found")
    else:
        raise ValueError(
            f"Config section {'vss-server'} not found in config.ini")

    return KUKSA_CONFIG, KUKSA_TOKEN


def get_default_token(protocol):
    if protocol == 'grpc':
        return GRPC_TOKEN
    else:
        return WS_TOKEN


def save_config(new_config, auth_token, CA_File=None):
    """
    save values to config.ini under [vss-server]
    """

    config.set('vss-server', 'ip', str(new_config['ip']))
    config.set('vss-server', 'port', str(new_config['port']))
    config.set('vss-server', 'protocol', str(new_config['protocol']))
    config.set('vss-server', 'insecure', str(new_config['insecure']))
    config.set('vss-server', 'tls_server_name',
               str(new_config['tls_server_name']))
    if auth_token in WS_TOKEN_PATHS or auth_token in GRPC_TOKEN_PATHS or auth_token == 'default':
        config.set('vss-server', 'token', 'default')
    else:
        config.set('vss-server', 'token', str(auth_token))

    if CA_File in CA_PATHS or CA_File == 'default':
        config.set('vss-server', 'cacert', 'default')
    else:
        config.set('vss-server', 'cacert', str(CA_File))

    # Always save to the user config
    config_path = USER_CONFIG_PATH
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    with open(config_path, 'w') as configfile:
        config.write(configfile)


def fullscreen_mode():
    return config.getboolean('default', 'fullscreen-mode', fallback=False)

def hvac_enabled():
    return config.getboolean('default', 'hvac-enabled', fallback=True)

def steering_wheel_enabled():
    return config.getboolean('default', 'steering-wheel-enabled', fallback=True)

def file_playback_enabled():
    return config.getboolean('default', 'file-playback-enabled', fallback=True)

def get_playback_file():
    if PLAYBACK_FILE is not None:
        return PLAYBACK_FILE
    else:
        # save file in project baseDir/Scripts/can_messages.txt
        with open(os.path.join(os.path.dirname(__file__), "can_messages.txt"), "w") as file:
            file.write("")
        # update config.ini
        config.set('default', 'file-playback-path', os.path.join(os.path.dirname(__file__), "can_messages.txt"))
        with open(USER_CONFIG_PATH, 'w') as configfile:
            config.write(configfile)
            
        return os.path.join(os.path.dirname(__file__), "can_messages.txt")
        
# Function to get the can interface name from config.ini
def get_can_interface():
    print(config.get('default', 'can-interface', fallback=None))
    return config.get('default', 'can-interface', fallback=None)

# function to check if can interface is enabled or not
def can_interface_enabled():
    can_interface = get_can_interface()
    if can_interface is not None:
        try:
            # check if an interface by the name exists
            can.interface.Bus(interface='socketcan', channel=can_interface)
            return True
        except Exception as e:
            logging.error(f"Error: {e}")
            return False
    return False

if not config.has_section('vss-server'):
    config.add_section('vss-server')
    temp = {
        'ip': "localhost",
        'port': "55555",
        'protocol': "grpc",
        'insecure': "",
        'cacert': "",
        'token': "",
        'tls_server_name': "",
    }
    save_config(temp, 'default', 'default')
