from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config.settings import settings

def get_groq_llm():
    return ChatGroq(
        api_key = settings.GROQ_API_KEY,
        model = settings.MODEL_NAME,
        temperature=settings.TEMPERATURE
    )


def get_gemini_llm():
    return ChatGoogleGenerativeAI(
        google_api_key=settings.GEMINI_API_KEY,
        model=settings.GEMINI_MODEL_NAME,
        temperature=settings.TEMPERATURE,
    )


def get_llm(provider: str):
    normalized_provider = (provider or "").strip().lower()

    if "gemini" in normalized_provider:
        return get_gemini_llm()

    return get_groq_llm()