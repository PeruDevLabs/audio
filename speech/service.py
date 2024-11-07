import io
from typing import Any, AsyncGenerator, Type
from typing_extensions import Self
import spacy
import torch
from fastapi.responses import StreamingResponse
from pydub import AudioSegment  # type: ignore
from TTS.api import TTS  # type: ignore
from .schema import CreateSpeechRequest, SpeakerLanguage, AudioFormat

class XTTS(TTS):
    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.nlp_en = spacy.load("en_core_web_sm")
        self.nlp_es = spacy.load("es_core_news_sm")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(path={self.path})"

    @classmethod
    def from_pretrained(
        cls: Type[Self], *, path: str = "tts_models/multilingual/multi-dataset/xtts_v2"
    ) -> Self:
        return cls(path).to(
            torch.device("cuda" if torch.cuda.is_available() else torch.device("mps") if torch.backends.mps.is_available() else "cpu")
        )

    def split_text(self, *, text: str, language: str):
        nlp = self.nlp_en if language == "en" else self.nlp_es
        doc = nlp(text)
        for sent in doc.sents:
            yield sent.text

    async def stream_audio(
        self,
        *,
        text: str,
        speaker: str,
        language: SpeakerLanguage,
        speed: float,
        response_format: AudioFormat,
    ) -> AsyncGenerator[bytes, None]:
        for group in self.split_text(text=text, language=language):
            audio_buffer = io.BytesIO()
            self.tts_to_file(  # type: ignore
                text=group,
                speaker=speaker,
                language=language,
                file_path=audio_buffer,  # type: ignore
                speed=speed,
                split_sentences=False,
            )
            chunk_buffer = io.BytesIO()
            audio_buffer.seek(0)
            segment: AudioSegment = AudioSegment.from_file(audio_buffer, format="wav", frame_rate=22050, channels=1, sample_width=2)  # type: ignore
            segment.export(out_f=chunk_buffer, format=response_format)  # type: ignore
            chunk_buffer.seek(0)
            for chunk in iter(lambda: chunk_buffer.read(4096), b""):
                yield chunk
            chunk_buffer.close()
            audio_buffer.close()

    def handler(self, body: CreateSpeechRequest) -> StreamingResponse:
        return StreamingResponse(
            self.stream_audio(
                text=body.text,
                speaker=body.speaker(),
                language=body.language,
                speed=body.speed,
                response_format=body.response_format,
            ),
            media_type=f"audio/{body.response_format}",
            headers={
                "Content-Disposition": f"attachment; filename=speech.{body.response_format}",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Transfer-Encoding": "chunked",
                "X-Accel-Buffering": "no",
                "Accept-Ranges": "bytes",
            },
        )

