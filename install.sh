#!/bin/bash

SERVICE_NAME="streamlit_analytics" 
sudo adduser \
   --system \
   --shell /bin/bash \
   --group \
   --disabled-password \
   streamlit
sudo mkdir -p /opt/${SERVICE_NAME} 
sudo chown streamlit:streamlit /opt/${SERVICE_NAME}
sudo cp -rf src/*.py /opt/${SERVICE_NAME}/
sudo cp -f requirements.txt /opt/${SERVICE_NAME}/
sudo cp -rf src/pages /opt/${SERVICE_NAME}/
sudo cp -rf src/logo.png /opt/${SERVICE_NAME}/
sudo cp -rf src/pgnDictionaries /opt/${SERVICE_NAME}/
sudo  runuser -l 'streamlit' -c "python -m venv /opt/${SERVICE_NAME}/venv"
sudo  runuser -l 'streamlit' -c "/opt/${SERVICE_NAME}/venv/bin/pip install -r /opt/${SERVICE_NAME}/requirements.txt"




sudo cp -f service/${SERVICE_NAME}.service /lib/systemd/system 
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl restart ${SERVICE_NAME}
