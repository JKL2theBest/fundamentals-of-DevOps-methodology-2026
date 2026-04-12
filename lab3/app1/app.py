from flask import Flask, request

app = Flask(__name__)


@app.route("/")
def home():
    return f"<h1>САЙТ 1</h1><p>Запрос пришел с IP: {request.headers.get('X-Real-IP', request.remote_addr)}</p>"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
