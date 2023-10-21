from typing import Dict, Any, Optional, List

from fastapi import FastAPI, Query, Form, HTTPException, UploadFile, File
from fastapi_socketio import SocketManager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
import shutil
from pathlib import Path
from pydub import AudioSegment

from v1.src.util.responsemodel import ResponseModel
from v1.src.modules.openai_module import OpenAIModule
from v1.src.modules.persistence import Persistence

app: FastAPI = FastAPI()

API_V1_ENDPOINT = "/api/v1"
OPENAI_V1_ENDPOINT = "/openai/v1"

# Set up CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sio = SocketManager(app=app)
app.mount("/ws", sio)

@app.get("/", response_model=ResponseModel)
async def default():
    return ResponseModel(success=True, message={"hi": "test"})

@app.get(f"{API_V1_ENDPOINT}/", response_model=ResponseModel)
async def test():
    return ResponseModel(success=True, message={"test": "passed"})

@app.get(f"{API_V1_ENDPOINT}/users/get_all_data")
async def get_all():
    return ResponseModel(
        success=True,
        message={"user_data": Persistence.get_all_users()}
    )

@app.get(f"{API_V1_ENDPOINT}/users/get_user")
async def get_user(user_id: str = Query()):
    return ResponseModel(
        success=True,
        message={"user_data": Persistence.get_user(user_id=user_id)}
    )

@app.post("/upload_audio/")
async def upload_audio(file: UploadFile = File(...)):
    # Ensure the upload directory exists
    UPLOAD_DIRECTORY = Path(__file__).parent / "uploads"
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

    # Save the uploaded file
    temp_path = UPLOAD_DIRECTORY / file.filename
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    mp3_path = UPLOAD_DIRECTORY / "audio.mp3"

    AudioSegment.from_file(str(temp_path)).export(str(mp3_path), format="mp3")

    # Transcribe using Whisper
    with open(mp3_path, "rb") as f:
        response = await OpenAIModule.whisper_transcription(f)
        transcription = response['text']

    # Clean up (Optional: remove temporary files)
    Path(temp_path).unlink()
    Path(mp3_path).unlink()

    return ResponseModel(
        success=True,
        message={"transcription": transcription}
    )


@app.post("/upload_video/")
async def upload_video(file: UploadFile = File(...)):
    print('ghj')
    # Ensure the upload directory exists
    UPLOAD_DIRECTORY = Path(__file__).parent / "uploads"
    UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)

    # Save the uploaded file
    temp_path = UPLOAD_DIRECTORY / file.filename
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    mp3_path = UPLOAD_DIRECTORY / "video.mov"

    AudioSegment.from_file(str(temp_path)).export(str(mp3_path), format="mov")

    # Clean up (Optional: remove temporary files)
    Path(temp_path).unlink()
    Path(mp3_path).unlink()

    return ResponseModel(
        success=True,
        message={}
    )