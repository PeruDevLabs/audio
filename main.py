import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from speech.handler import app as speech_app
from translations.main import app as translations_app
from transcribe.main import app as transcribe_app



def create_app():
    os.environ["COQUI_TOS_AGREED"] = "true"
    app = FastAPI(
        title="Audio API",
        description="API for audio processing",
        version="0.0.1",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    for _ in [speech_app, translations_app, transcribe_app]:
        app.include_router(_, prefix="/v1")
    return app


app = create_app()