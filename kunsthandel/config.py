import os


class DebugConfig:
    # These values are usually set to environment variables. I don't like this procedure of hard coding them into my machine
    SECRET_KEY = '5c9c4d68d7eea5a7423653599139f072'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # "///" -> relative path from this file