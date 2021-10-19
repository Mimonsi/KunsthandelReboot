import os


class DebugConfig:
    SECRET_KEY = '76d6ec9f1ee1e0b7841452d30421e398' # Secret key - replace with your own
    SQLALCHEMY_DATABASE_URI = 'sqlite:///development.db'  # "///" -> relative path from this file


class ProductionConfig:
    SECRET_KEY = 'ff8c8fd92c91b8b8decaecaa719b2b3a'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///production.db'
