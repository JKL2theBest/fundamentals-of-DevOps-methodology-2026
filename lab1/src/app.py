from flask import Flask

app = Flask(__name__)

app.json.ensure_ascii = False


@app.route("/")
def hello():
    return {"message": "Хаю-хай, с вами Докер! Надеюсь, запущен хорошим конфигом..."}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
