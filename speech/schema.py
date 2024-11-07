from pydantic import BaseModel, Field
from typing_extensions import TypeAlias, Self
import random
from typing import Literal, Optional
from fastapi import UploadFile, File, Query
from uuid import UUID, uuid4
import numpy as np

import hashlib
import numpy as np
from typing import Union
from uuid import UUID

def compute_fingerprint(audio_data: Union[bytes, np.ndarray], user: str, secret_text: str = "default_secret") -> str:
    """
    Compute a fingerprint for voice data using audio content, user ID, and a secret text.
    
    Args:
        audio_data: Either raw bytes or numpy array of audio data
        user: UUID of the user
        secret_text: Secret text to use in fingerprint generation
    
    Returns:
        str: Hex digest of the fingerprint
    """
    # Convert bytes to numpy array if needed
    if isinstance(audio_data, bytes):
        audio_data = np.frombuffer(audio_data, dtype=np.int16)
    
    # Ensure audio_data is a numpy array
    if not isinstance(audio_data, np.ndarray):
        raise ValueError("Audio data must be either bytes or numpy array")

    # Create a SHA-256 hasher
    hasher = hashlib.sha256()
    
    # Add the secret text first
    hasher.update(secret_text.encode('utf-8'))
    
    # Add the user UUID
    hasher.update(str(user).encode('utf-8'))
    
    # Process audio data in chunks to handle large files efficiently
    chunk_size = 8192  # Process 8KB at a time
    
    # Convert audio data to bytes if it's not already
    audio_bytes = audio_data.tobytes()
    
    for i in range(0, len(audio_bytes), chunk_size):
        chunk = audio_bytes[i:i + chunk_size]
        hasher.update(chunk)
    
    # Get the final hash
    fingerprint = hasher.hexdigest()
    
    return fingerprint


SpeakerName: TypeAlias = Literal[
    "EN",
    "ES",
    "Claribel Dervla",
    "Daisy Studious",
    "Gracie Wise",
    "Tammie Ema",
    "Alison Dietlinde",
    "Ana Florence",
    "Annmarie Nele",
    "Asya Anara",
    "Brenda Stern",
    "Gitta Nikolina",
    "Henriette Usha",
    "Sofia Hellen",
    "Tammy Grit",
    "Tanja Adelina",
    "Vjollca Johnnie",
    "Andrew Chipper",
    "Badr Odhiambo",
    "Dionisio Schuyler",
    "Royston Min",
    "Viktor Eka",
    "Abrahan Mack",
    "Adde Michal",
    "Baldur Sanjin",
    "Craig Gutsy",
    "Damien Black",
    "Gilberto Mathias",
    "Ilkin Urbano",
    "Kazuhiko Atallah",
    "Ludvig Milivoj",
    "Suad Qasim",
    "Torcull Diarmuid",
    "Viktor Menelaos",
    "Zacharie Aimilios",
    "Nova Hogarth",
    "Maja Ruoho",
    "Uta Obando",
    "Lidiya Szekeres",
    "Chandra MacFarland",
    "Szofi Granger",
    "Camilla Holmström",
    "Lilya Stainthorpe",
    "Zofija Kendrick",
    "Narelle Moon",
    "Barbora MacLean",
    "Alexandra Hisakawa",
    "Alma María",
    "Rosemary Okafor",
    "Ige Behringer",
    "Filip Traverse",
    "Damjan Chapman",
    "Wulf Carlevaro",
    "Aaron Dreschner",
    "Kumar Dahl",
    "Eugenio Mataracı",
    "Ferran Simen",
    "Xavier Hayasaka",
    "Luis Moray",
    "Marcos Rudaski",
]

speakers: list[SpeakerName] = [
    "EN",
    "ES",
    "Claribel Dervla",
    "Daisy Studious",
    "Gracie Wise",
    "Tammie Ema",
    "Alison Dietlinde",
    "Ana Florence",
    "Annmarie Nele",
    "Asya Anara",
    "Brenda Stern",
    "Gitta Nikolina",
    "Henriette Usha",
    "Sofia Hellen",
    "Tammy Grit",
    "Tanja Adelina",
    "Vjollca Johnnie",
    "Andrew Chipper",
    "Badr Odhiambo",
    "Dionisio Schuyler",
    "Royston Min",
    "Viktor Eka",
    "Abrahan Mack",
    "Adde Michal",
    "Baldur Sanjin",
    "Craig Gutsy",
    "Damien Black",
    "Gilberto Mathias",
    "Ilkin Urbano",
    "Kazuhiko Atallah",
    "Ludvig Milivoj",
    "Suad Qasim",
    "Torcull Diarmuid",
    "Viktor Menelaos",
    "Zacharie Aimilios",
    "Nova Hogarth",
    "Maja Ruoho",
    "Uta Obando",
    "Lidiya Szekeres",
    "Chandra MacFarland",
    "Szofi Granger",
    "Camilla Holmström",
    "Lilya Stainthorpe",
    "Zofija Kendrick",
    "Narelle Moon",
    "Barbora MacLean",
    "Alexandra Hisakawa",
    "Alma María",
    "Rosemary Okafor",
    "Ige Behringer",
    "Filip Traverse",
    "Damjan Chapman",
    "Wulf Carlevaro",
    "Aaron Dreschner",
    "Kumar Dahl",
    "Eugenio Mataracı",
    "Ferran Simen",
    "Xavier Hayasaka",
    "Luis Moray",
    "Marcos Rudaski",
]
SpeakerLanguage: TypeAlias = Literal["en", "es", "fr", "de", "it", "nl", "ru", "tr"]
AudioFormat: TypeAlias = Literal["mp3", "wav", "ogg", "flac"]


def get_speaker() -> SpeakerName:
    try:
        return random.choice(speakers)
    except IndexError:
        raise ValueError("No speakers available")

class VoiceObject(BaseModel):
    id:str = Field(default_factory=lambda:str(uuid4()))
    fingerprint: str
    user: str
    audio: bytes

    @classmethod
    async def from_upload(cls, *, upload:UploadFile=File(...),user:UUID=Query(default_factory=uuid4))->Self:
        data = await upload.read()
        return cls(fingerprint=compute_fingerprint(data,str(user)),user=str(user),audio=data)

class CreateSpeechRequest(BaseModel):
    model: Literal["xtts"] = Field(
        default="xtts", description="The speech synthesis model to use."
    )
    text: str = Field(..., description="The text to convert to speech.")
    voice: SpeakerName = Field(
        default_factory=get_speaker, description="The voice to use for the speech."
    )
    voice_id: Optional[str] = Field(
        default=None, description="The custom voice to use for the speech."
    )
    response_format: AudioFormat = Field(
        default="mp3", description="The desired format for the speech output."
    )
    speed: float = Field(
        default=1.0,
        ge=0.25,
        le=4.0,
        description="The speed of the generated speech (0.25x to 4.0x).",
    )
    language: SpeakerLanguage = Field(
        default="en", description="The language of the input text."
    )

    def speaker(self) -> str:
        return self.voice_id or self.voice