#!/bin/bash
# Обновляем список пакетов и скачиваем wget, unzip и file
apt-get update && apt-get install -y wget unzip file

# Устанавливаем Python-зависимости
pip install -r requirements.txt

# Скачиваем модель Vosk
wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip

# Распаковываем
unzip vosk-model-small-ru-0.22.zip

# (Опционально, чтобы проверить, что файлы на месте)
ls -la
