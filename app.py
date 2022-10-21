from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pyscopg2://trellodev:password123@127.0.0.1:5432/trello'

db = SQLAlchemy(app)

@app.route('/')
def index():
    return "<h1>hello world!</h1>"

