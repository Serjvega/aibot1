import os
import random
import requests  # Добавьте это
from flask import Flask, render_template, request, jsonify, send_from_directory, Response
from groq import Groq
from dotenv import load_dotenv
from urllib.parse import quote # Для обработки кириллицы

load_dotenv()
app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/')
def index():
    return render_template('index.html')

# НОВЫЙ МАРШРУТ ДЛЯ КАРТИНОК
@app.route('/proxy-image')
def proxy_image():
    url = request.args.get('url')
    if not url:
        return "No URL", 400
    # Сервер сам скачивает картинку
    response = requests.get(url, stream=True)
    return Response(response.content, content_type=response.headers['Content-Type'])

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get("message", "").strip()
        
        low_input = user_input.lower()
        if low_input.startswith("нарисуй") or low_input.startswith("draw"):
            prompt = user_input.replace("нарисуй", "").replace("draw", "").strip()
            
            # Кодируем промпт, чтобы не было ошибок с пробелами и русскими буквами
            safe_prompt = quote(prompt)
            seed = random.randint(1, 999999)
            
            # Ссылка теперь ведет на ваш сервер через прокси
            pollinations_url = f"https://pollinations.ai/p/{safe_prompt}?width=1024&height=1024&seed={seed}&nologo=true"
            # Мы возвращаем ссылку на наш прокси-маршрут
            proxy_url = f"/proxy-image?url={quote(pollinations_url)}"
            
            return jsonify({
                "response": f"Запрос принят: {prompt}",
                "image": proxy_url
            })

        # Обычный чат
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": user_input}],
        )
        return jsonify({"response": completion.choices[0].message.content})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# PWA маршруты
@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory(os.path.dirname(__file__), 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory(os.path.dirname(__file__), 'sw.js')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
