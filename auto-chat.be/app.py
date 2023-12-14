from flask import Flask
from controllers.chatbot import chatbot_Blueprint
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]  = "./config/appcredentials.json"


app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


app.register_blueprint(chatbot_Blueprint)