from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Mengambil API Key dari Environment Variables di Render (Lebih Aman)
FONNTE_TOKEN = os.getenv("FONNTE_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
AI_MODEL = "meta-llama/llama-3-8b-instruct:free"

def tanyakan_ke_ai(pesan_user):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": AI_MODEL,
        "messages": [
            {"role": "system", "content": "Kamu adalah asisten WhatsApp yang ramah dan membantu."},
            {"role": "user", "content": pesan_user}
        ]
    }
    try:
        response = requests.post("https://openrouter.ai", headers=headers, json=payload, timeout=10)
        return response.json()['choices']['message']['content']
    except Exception as e:
        print("Error OpenRouter:", e)
        return "Maaf, sistem AI sedang sibuk."

def kirim_balasan_wa(nomor_tujuan, pesan_balasan):
    url = "https://fonnte.com"
    headers = {"Authorization": FONNTE_TOKEN}
    payload = {"target": nomor_tujuan, "message": pesan_balasan}
    try:
        requests.post(url, headers=headers, data=payload, timeout=10)
    except Exception as e:
        print("Error Fonnte:", e)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.form
    pesan_masuk = data.get('message')
    pengirim = data.get('sender')
    
    if pesan_masuk and pengirim:
        jawaban_ai = tanyakan_ke_ai(pesan_masuk)
        kirim_balasan_wa(pengirim, jawaban_ai)
        
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    # Render membutuhkan port dinamis
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
  
