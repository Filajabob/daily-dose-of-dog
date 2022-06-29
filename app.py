from flask import Flask
from threading import Thread

app = Flask('')


@app.route('/')
def home():
    return "Doggos aren't here."


def run():
    t = Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": 8080})
    t.start()