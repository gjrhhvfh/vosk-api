#!/bin/bash
pip install -r requirements.txt

# Скачиваем модель
wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip

# Распаковываем
unzip vosk-model-small-ru-0.22.zip

# Проверяем, что папка на месте (выведет список файлов)
ls -la
