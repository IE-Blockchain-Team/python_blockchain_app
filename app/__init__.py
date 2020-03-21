from flask import Flask

app = Flask(__name__)
app.secret_key = b'secret_key_here'

from app import views