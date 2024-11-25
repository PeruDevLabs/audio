from fastapi import APIRouter

from .schema import CreateSpeechRequest
from .service import XTTS

app = APIRouter(prefix="/audio")
xtts = XTTS.from_pretrained()


@app.post("/speech")
def speech_handler(body: CreateSpeechRequest):
    return xtts.handler(body=body)
