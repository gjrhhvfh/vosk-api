import os
import json
import tempfile
import urllib.request
import zipfile
from flask import Flask, request, jsonify, send_file
from vosk import Model, KaldiRecognizer, SetLogLevel
from gtts import gTTS

SetLogLevel(-1)  # отключаем лишние логи Vosk

app = Flask(__name__)

API_KEY = os.environ.get("API_KEY", "plasti7154")
MODEL_PATH = "vosk-model-small-ru-0.22"
MODEL_URL = "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"


# Скачиваем модель, если её нет
if not os.path.exists(MODEL_PATH):
    print("Скачиваем модель Vosk...")
    urllib.request.urlretrieve(MODEL_URL, "model.zip")
    with zipfile.ZipFile("model.zip", "r") as z:
        z.extractall(".")
    os.remove("model.zip")
    print("Модель готова!")

# Загружаем модель
model = Model(MODEL_PATH)


def check_key():
    key = request.headers.get("X-API-Key", "")
    return key == API_KEY


@app.route("/stt", methods=["POST"])
def stt():
    if not check_key():
        return jsonify({"code": 2, "error": "Invalid API key"})

    if "audio" not in request.files:
        return jsonify({"code": 2, "error": "No audio file"})

    audio = request.files["audio"]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio.save(tmp.name)

    rec = KaldiRecognizer(model, 16000)
    rec.SetWords(False)

    text = ""
    with open(tmp.name, "rb") as f:
        while True:
            data = f.read(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                text += res.get("text", "") + " "

    res = json.loads(rec.FinalResult())
    text += res.get("text", "")

    os.unlink(tmp.name)
    return jsonify({"code": 1, "result": text.strip()})


@app.route("/tts", methods=["POST"])
def tts():
    if not check_key():
        return jsonify({"code": 2, "error": "Invalid API key"})

    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"code": 2, "error": "No text provided"})

    tts_obj = gTTS(text=text, lang="ru")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts_obj.save(tmp.name)

    return send_file(
        tmp.name,
        mimetype="audio/mpeg",
        as_attachment=True,
        download_name="speech.mp3"
    )


@app.route("/", methods=["GET"])
def index():
    return jsonify({"code": 1, "result": "Vosk STT/TTS API is running"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
