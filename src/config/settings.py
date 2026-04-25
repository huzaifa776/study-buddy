import os
from dotenv import load_dotenv

load_dotenv()

class Settings():

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

    MODEL_NAME = "llama-3.3-70b-versatile"
    GEMINI_MODEL_NAME = "gemini-3.1-flash-lite-preview"
    
    TEMPERATURE = 0.9

    MAX_RETRIES = 3


settings = Settings()  