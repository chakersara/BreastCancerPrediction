from flask import Flask
from flask_sqlalchemy import SQLAlchemy



def createApp():
    app=Flask(__name__)
    DB_URL="sqlite:///../docs.db"
    app.config['CORS_HEADERS'] = 'Content-Type'
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_URL
    app.config["SECRET_KEY"]="amen_dawla"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # app.config['WHOOSH_BASE'] = 'whoosh'
    
    return app


def createBD(app):
    return SQLAlchemy(app)
