#!/bin/bash
pip install -r requirements.txt
# Скачиваем и распаковываем модель Vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip
unzip vosk-model-small-ru-0.22.zip
