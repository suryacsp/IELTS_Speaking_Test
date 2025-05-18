import os 
from dotenv import load_dotenv

load_dotenv()

class Config:

    SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    @staticmethod
    def init_app(app):
        # This hook can be used to initialize extensions or perform
        # any app-specific configuration at create_app time
        pass