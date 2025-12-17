import os
import random
from flask import Flask, render_template, request, jsonify, send_from_directory
from groq import Groq
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

app = Flask(__name__)

# Настройка клиента Groq
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Выбранная модель
MODEL = "llama-3.3-70b-versatile"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_input = data.get("message", "").strip()
        
        if not user_input:
            return jsonify({"error": "Пустое сообщение"}), 400

        # ПРОВЕРКА: Генерация изображений
        cmd = user_input.lower()
        if cmd.startswith("нарисуй") or cmd.startswith("draw"):
            prompt = user_input.replace("нарисуй", "").replace("Нарисуй", "").replace("draw", "").replace("Draw", "").strip()
            if not prompt:
                return jsonify({"response": "Что именно нарисовать? Напиши, например: 'Нарисуй рыжего кота'"})
            
            # Используем Pollinations.ai для картинок
            seed = random.randint(1, 999999)
            image_url = f"https://pollinations.ai/p/{prompt}?width=1024&height=1024&seed={seed}"
            return jsonify({
                "response": f"Генерирую изображение по запросу: {prompt}",
                "image": image_url
            })

        # ОБЫЧНЫЙ ЧАТ: Groq API
        completion = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Ты профессиональный ИИ-ассистент. Отвечай дружелюбно и помогай пользователю во всём."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
        )
        
        return jsonify({"response": completion.choices[0].message.content})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Произошла ошибка на сервере Groq"}), 500

# Файлы для превращения в приложение (PWA)
@app.route('/manifest.json')
def serve_manifest():
    return send_from_directory('.', 'manifest.json')

@app.route('/sw.js')
def serve_sw():
    return send_from_directory('.', 'sw.js')

if __name__ == '__main__':
    # 0.0.0.0 позволяет заходить на сайт с телефона в одной Wi-Fi сети
    app.run(host='0.0.0.0', port=5000, debug=True)