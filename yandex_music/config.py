class Config:
    """Configuration class for flask application."""

    DEBUG = True
    SECRET_KEY = "ed12ejdh3ud38dAKDJij32d"
    SQLALCHEMY_DATABASE_URI = "sqlite:///music.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
