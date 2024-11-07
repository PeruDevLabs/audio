from typing import Optional

from fastapi import APIRouter, HTTPException, status, File, UploadFile
from httpx import AsyncClient
from openai import AsyncOpenAI
from openai._utils._proxy import LazyProxy
from openai.types.audio.transcription import Transcription
from pydantic import BaseModel, Field
from typing_extensions import Literal
from openai import AsyncOpenAI

def get_client():
    return AsyncOpenAI()

app = APIRouter(tags=["translations"], prefix="/audio")

class TranscriptionCreate(BaseModel, LazyProxy[AsyncOpenAI]):
    file: str = Field(..., description="The URL of the audio file to transcribe.")
    model: Literal["whisper-large-v3"] = Field(
        default="whisper-large-v3", description="The model to use for transcription."
    )
    language: Optional[str] = Field(
        default="en",
        description="The language of the input audio. Supplying the input language in ISO-639-1 format will improve accuracy and latency.",
    )
    prompt: str = Field(
        ...,
        description="An optional text to guide the model's style or continue a previous audio segment. The prompt should match the audio language.",
    )
    response_format: Literal["json", "text", "srt", "verbose_json", "vtt"]
    temperature: float

    def __load__(self):
        return get_client()


@app.post("/translations")
async def handler(request: TranscriptionCreate) -> Transcription:
    try:
        async with AsyncClient() as client:
            response = await client.get(request.file)
            data = response.content
            
            return await request.__load__().audio.transcriptions.create(
            file=("audio.mp3", data),
            model=request.model,
            language=request.language or "en",
            prompt="Translate the speech inferred text to English",
            response_format=request.response_format,
            temperature=request.temperature,
        )
    except (Exception, HTTPException) as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e