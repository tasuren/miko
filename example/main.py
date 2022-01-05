# Examples - Simple

from dataclasses import dataclass

from flask import Flask
from miko import Manager

app = Flask(__name__)
manager = Manager()

@dataclass
class User:
    name: str
    comment: str

@app.get("/")
def index():
    return manager.render(
        "index.html",
        user=User(
            "麻弓＝タイム", "小さい胸は貴重なのよっ、ステータスなのよっ！？"
        ),
        logged_in=True
    )

app.run()