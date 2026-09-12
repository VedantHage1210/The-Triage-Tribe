"""
Visual Observation Service — Section 10.2.
Hard rule (do not weaken this, per Section 1.4 and 10.1): the prompt must
never allow a percentage, severity score, or definitive diagnosis. This is
a deliberate safety design, not a placeholder to "improve" later.
"""
import base64

from app.core.config import get_settings
from app.schemas.triage_schema import VisualCheckResult
from app.services.llm_client import LLMClient

settings = get_settings()
llm = LLMClient()

OBSERVATION_SYSTEM_PROMPT = """You are a visual observation assistant. You do NOT diagnose and must NEVER
output a percentage, severity score, or definitive condition name as fact.
Describe only visible features (color, swelling, texture, visible patterns).
State clearly this is not a medical diagnosis. If the image is unclear, low
quality, or you cannot make a confident observation, say so explicitly rather
than guessing. Write every field entirely in {language_name} — do not mix in
English words or sentences.

Keep each item in "visible_features" short — a 3-6 word phrase (e.g. "mild
redness along the eyelid"), not a full sentence. Put any longer explanation
in "general_note" instead.

Output strict JSON only:
{{
  "visible_features": ["string", ...],
  "general_note": "string",
  "recommend_professional_check": true,
  "image_quality_sufficient": true
}}"""


def _call_vision_anthropic(system_prompt: str, image_b64: str, media_type: str, category: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=settings.LLM_API_KEY)
    response = client.messages.create(
        model=settings.LLM_MODEL,
        max_tokens=512,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {"type": "base64", "media_type": media_type, "data": image_b64},
                    },
                    {
                        "type": "text",
                        "text": f"This is a photo of the patient's {category}. Provide your observation.",
                    },
                ],
            }
        ],
    )
    return response.content[0].text


def _call_vision_gemini(system_prompt: str, image_bytes: bytes, media_type: str, category: str) -> str:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.LLM_API_KEY)
    response = client.models.generate_content(
        model=settings.LLM_MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=media_type),
            f"This is a photo of the patient's {category}. Provide your observation.",
        ],
        config=types.GenerateContentConfig(system_instruction=system_prompt),
    )
    return response.text


LANGUAGE_NAMES = {"en": "English", "de": "German"}


def analyze_image(image_bytes: bytes, media_type: str, category: str, language: str) -> VisualCheckResult:
    """
    category: "eyes" or "skin" only (Section 10.1 scope decision).
    Raises on failure — caller (API layer) must catch and fall back safely,
    same philosophy as Section 7.5.
    """
    language_name = LANGUAGE_NAMES.get(language, "English")
    system_prompt = OBSERVATION_SYSTEM_PROMPT.format(language_name=language_name)

    if settings.LLM_PROVIDER == "gemini":
        raw_text = _call_vision_gemini(system_prompt, image_bytes, media_type, category)
    else:
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        raw_text = _call_vision_anthropic(system_prompt, image_b64, media_type, category)

    cleaned = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    import json

    parsed = json.loads(cleaned)
    return VisualCheckResult(**parsed)
