from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


def get_llm(model: str = "gemini-2.5-flash"):
    return ChatGoogleGenerativeAI(
        model=model, google_api_key=settings.GOOGLE_API_KEY, max_retries=3, timeout=60
    )


def get_fast_llm():
    """
    Lighter model for gradding/scoring nodes.
    Faster and cheaper than full model
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=settings.GOOGLE_API_KEY,
        max_retries=3,
        timeout=60
    )
