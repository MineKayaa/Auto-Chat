from flask import Flask
from controllers.chatbot import chatbot_Blueprint
from controllers.agent import agent_Blueprint
import os
from flask_cors import CORS
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]  = "~/Users/macbook/.config/gcloud/application_default_credentials.json"

app = Flask(__name__)

CORS(app)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


app.register_blueprint(chatbot_Blueprint)
app.register_blueprint(agent_Blueprint)