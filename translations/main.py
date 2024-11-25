import json
from typing import Any, Dict, Optional, Union

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from httpx import AsyncClient
from openai import AsyncOpenAI
from openai.types.audio import Transcription
from openai.types.chat import ChatCompletion
from pydantic import BaseModel, Field
from typing_extensions import Literal

# Router configuration
app = APIRouter(tags=["translations"], prefix="/audio")

# Initialize OpenAI client
ai = AsyncOpenAI()


class TranslationResponse(BaseModel):
    """Response model for translation endpoint"""

    content: str = Field(..., description="The translated text")
    source_language: str = Field(..., description="Detected source language")
    source_text: str = Field(..., description="Original transcribed text")


class AudioTranslationError(Exception):
    """Custom exception for audio translation errors"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


async def transcribe_audio(
    file: UploadFile,
    model: str,
    prompt: Optional[str],
    response_format: str,
    temperature: float,
) -> str:
    """Transcribe audio file using OpenAI's Whisper API"""
    try:
        file_content = await file.read()
        transcription: Transcription = await ai.audio.transcriptions.create(
            file=(file.filename, file_content, file.content_type),
            model=model,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
        )

        # Handle different response formats
        if response_format == "json":
            return json.loads(transcription.model_dump_json())["text"]
        elif response_format == "text":
            return str(transcription)
        elif response_format == "verbose_json":
            response_data = json.loads(transcription.model_dump_json())
            return response_data["text"]
        else:
            raise AudioTranslationError(
                f"Unsupported response format: {response_format}"
            )

    except Exception as e:
        raise AudioTranslationError("Failed to transcribe audio", {"error": str(e)})
    finally:
        await file.seek(0)  # Reset file pointer


async def translate_text(text: str) -> tuple[str, str]:
    """Translate text to English and detect source language"""
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a translation bot. Detect the language and translate the text to English. "
                    "Respond in JSON format with two fields: "
                    "'translation' (the English translation) and "
                    "'source_language' (the detected source language). "
                    "Example: {'translation': 'Hello world', 'source_language': 'Spanish'}"
                ),
            },
            {"role": "user", "content": text},
        ]

        response: ChatCompletion = await ai.chat.completions.create(
            model="llama-3.2-90b-text-preview",
            messages=messages,
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        return result["translation"], result["source_language"]

    except Exception as e:
        raise AudioTranslationError("Failed to translate text", {"error": str(e)})


@app.post(
    "/translations",
    response_model=TranslationResponse,
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid input"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Processing error"},
    },
)
async def translate_audio(
    file: UploadFile = File(..., description="Audio file to translate"),
    model: Literal["whisper-large-v3"] = Form(
        default="whisper-large-v3", description="Whisper model to use"
    ),
    prompt: Optional[str] = Form(
        default=None, description="Optional prompt for transcription"
    ),
    response_format: Literal["json", "text", "verbose_json"] = Form(
        default="json", description="Response format for transcription"
    ),
    temperature: float = Form(
        default=0.0, ge=0.0, le=1.0, description="Sampling temperature"
    ),
) -> TranslationResponse:
    """
    Translate audio file to English text.

    1. Transcribes the audio using OpenAI's Whisper
    2. Detects the language and translates to English
    3. Returns the translation and metadata
    """
    try:
        # Validate file
        if not file.content_type.startswith(("audio/", "video/")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an audio file",
            )

        # Step 1: Transcribe
        transcription = await transcribe_audio(
            file=file,
            model=model,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
        )

        # Step 2: Translate
        translation, source_language = await translate_text(transcription)

        # Step 3: Return response
        return TranslationResponse(
            content=translation,
            source_language=source_language,
            source_text=transcription,
        )

    except AudioTranslationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"message": e.message, "details": e.details},
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}",
        )
    finally:
        await file.close()
