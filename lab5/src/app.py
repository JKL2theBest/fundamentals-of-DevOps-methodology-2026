import os
from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
app.json.ensure_ascii = False

# Эта строчка автоматически оборачивает все роуты и собирает метрики
metrics = PrometheusMetrics(app)

# Статичная информация о приложении
metrics.info("app_info", "Application info", version="1.0.0")


@app.route("/")
def hello():
    message = os.getenv("APP_MESSAGE", "Хаю-хай! Мониторинг запущен 📈")
    return {"message": message}


@app.route("/error")
def error():
    # Намеренная ошибка
    1 / 0
    return "This will not be reached"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
