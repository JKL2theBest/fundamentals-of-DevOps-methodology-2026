import os
from flask import Flask

app = Flask(__name__)
app.json.ensure_ascii = False


@app.route("/")
def hello():
    # Читаем переменную окружения APP_MESSAGE.
    # Если её нет, выводим стандартный текст.
    message = os.getenv("APP_MESSAGE", "Хаю-хай, с вами Докер (по умолчанию)!")
    return {"message": message}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
