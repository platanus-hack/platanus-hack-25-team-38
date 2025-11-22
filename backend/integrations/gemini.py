import os
import httpx


def generate_content(text: str, model: str = "gemini-2.5-flash-lite"):
    """
    Genera contenido usando la API de Gemini.
    
    Args:
        text: El texto/pregunta a enviar a Gemini
        model: El modelo a usar (default: gemini-2.5-flash)
    
    Returns:
        La respuesta de la API de Gemini
    """
    api_key = os.getenv('GEMINI_API_KEY')
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY no está configurada en las variables de entorno")
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    headers = {
        'Content-Type': 'application/json',
        'x-goog-api-key': api_key
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": text
                    }
                ]
            }
        ]
    }
    
    with httpx.Client() as client:
        response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()

