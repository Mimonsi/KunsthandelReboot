import os


class BaseConfig:
    BABEL_TRANSLATION_DIRECTORIES = "./translations"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    SECRET_KEY = "76d6ec9f1ee1e0b7841452d30421e398"  # Secret key - replace with your own
    SQLALCHEMY_DATABASE_URI = "sqlite:///development.db?charset=utf8mb4"  # "///" -> relative path from this file
    BASE_URL = "http://localhost:5000"
    STORAGE_DATABASE_FILE = "development.db"
    DEBUG_TB_PROFILER_ENABLED = True
    DEBUG_TB_TEMPLATE_EDITOR_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SECRET_KEY = "123456"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    BASE_URL = "http://localhost:5000"
    STORAGE_DATABASE_FILE = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CACHE_TYPE = "null"
    WTF_CSRF_ENABLED = False

    DEBUG_TB_PROFILER_ENABLED = False
    DEBUG_TB_TEMPLATE_EDITOR_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_ENABLED = False


class ProductionConfig(BaseConfig):
    SECRET_KEY = "ff8c8fd92c91b8b8decaecaa719b2b3a"
    SQLALCHEMY_DATABASE_URI = "sqlite:///production.db?charset=utf8mb4"
    BASE_URL = "http://utest.webgadgets.de:81"
    STORAGE_DATABASE_FILE = "production.db"
