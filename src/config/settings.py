import os
from dotenv import load_dotenv

load_dotenv()

class Settings():

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

    MODEL_NAME = "groq/compound-mini"
    
    TEMPERATURE = 0.2

    MAX_RETRIES = 1


settings = Settings()  