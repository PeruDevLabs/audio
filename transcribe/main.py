import typing as tp
from fastapi import APIRouter, HTTPException, status, Form, Query, File, UploadFile
from httpx import AsyncClient
from openai import AsyncOpenAI
from openai._utils._proxy import LazyProxy
from pydantic import BaseModel, Field
from typing_extensions import Literal
from dotenv import load_dotenv

load_dotenv()
from .utils import get_logger

logger = get_logger()

def get_client():
    return AsyncOpenAI()


app = APIRouter(tags=["audio"], prefix="/audio")
ai = AsyncOpenAI()

@app.post("/transcriptions")
async def transcriptions_handler(
    language:tp.Optional[str]=Query(default="es"),
    file:UploadFile = File(...),
    model:tp.Literal["whisper-large-v3"] = Form(default="whisper-large-v3"),
    prompt:tp.Optional[str] = Form(default=None),
    response_format:tp.Literal["json","text","srt","verbose_json","vtt"]=Form(default="json"),
    temperature:float=Form(default=1.0)
):
    try:
        return await get_client().audio.transcriptions.create(
            file=(file.filename, await file.read(),file.content_type),
            model=model,
            language=language,
            prompt=prompt,
            response_format=response_format,
            temperature=temperature,
        )
    except (Exception, HTTPException) as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
