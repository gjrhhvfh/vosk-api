import os
import json
import tempfile
from flask import Flask, request, jsonify, send_file
import onnx_asr
from gtts import gTTS

app = Flask(__name__)

# Разрешаем CORS для нашего сайта
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'X-API-Key, Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    return response

API_KEY = os.environ.get("API_KEY", "plasti7154")

# Загружаем модель GigaAM v3 (RNNT с пунктуацией)
# Модель скачается автоматически при первом запросе
model = onnx_asr.load_model("gigaam-v3-e2e-rnnt")

def check_key():
    return request.headers.get("X-API-Key", "") == API_KEY

@app.route("/stt", methods=["POST"])
def stt():
    if not check_key():
        return jsonify({"code": 2, "error": "Invalid API key"})
    if "audio" not in request.files:
        return jsonify({"code": 2, "error": "No audio file"})

    audio = request.files["audio"]
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    audio.save(tmp.name)

    try:
        # onnx-asr сам декодирует WAV и запускает модель
        text = model.recognize(tmp.name)
    except Exception as e:
        os.unlink(tmp.name)
        return jsonify({"code": 2, "error": f"STT error: {str(e)}"})

    os.unlink(tmp.name)
    return app.response_class(
        json.dumps({"code": 1, "result": text}, ensure_ascii=False),
        mimetype="application/json; charset=utf-8"
    )

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
    return send_file(tmp.name, mimetype="audio/mpeg", as_attachment=True, download_name="speech.mp3")

@app.route("/", methods=["GET"])
def index():
    return jsonify({"code": 1, "result": "GigaAM STT/TTS API is running"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
