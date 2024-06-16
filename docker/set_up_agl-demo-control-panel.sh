#!/bin/bash

# Disable the package proxy.
export http_proxy=""
export https_proxy=""

# Clone AGL Demo Control Panel
cd /opt
http_proxy="" https_proxy="" git clone "https://gerrit.automotivelinux.org/gerrit/src/agl-demo-control-panel"
cd agl-demo-control-panel

python3 -m venv test
source test/bin/activate
pip3 install -r requirements.txt
pyside6-rcc assets/res.qrc -o res_rc.py