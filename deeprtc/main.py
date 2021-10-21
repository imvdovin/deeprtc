import logging
import uuid
import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from aiortc import RTCSessionDescription, RTCPeerConnection
from aiortc.contrib.media import MediaBlackhole, MediaRelay
from deeprtc.common.settings import get_settings
from deeprtc.common.exceptions.failed_on_start import FailedOnStartException
from deeprtc.modules.webrtc.audio_track import AudioTrackStream
from deeprtc.modules.webrtc.types import EMediaStreamAction
from deeprtc.modules.file.controller import router as file_router


app = FastAPI()

root_dir = Path(__file__).resolve().parent

static_path = root_dir / 'static'

app.mount(str(static_path), StaticFiles(directory=static_path), name="static")

app.include_router(file_router, prefix="/files")

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates_path = root_dir / 'templates'

templates = Jinja2Templates(directory=str(templates_path))


logger = logging.getLogger(__name__)

ROOT = os.path.dirname(__file__)


pcs = set()
relay = MediaRelay()


@ app.on_event("startup")
async def on_start():
    settings = get_settings()

    for k, v in settings.__dict__.items():
        if v != '' and v != None:
            continue
        raise FailedOnStartException(f'Set up value for {k} in .env')


@ app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("index.html", {'request': request})


@ app.post("/offer")
async def offer(request: Request):
    params = await request.json()
    logger.info(params)
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", pc_id)

    # prepare local media
    recorder = MediaBlackhole()

    @ pc.on("datachannel")
    def on_datachannel(channel):
        @ channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @ pc.on("connectionstatechange")
    async def on_connectionstatechange():
        log_info("Connection state is %s", pc.connectionState)
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @ pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            pc.addTrack(
                AudioTrackStream(
                    relay.subscribe(track), action=EMediaStreamAction.TO_TEXT
                )
            )

        @ track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)
            await recorder.stop()

    # handle offer
    await pc.setRemoteDescription(offer)
    await recorder.start()

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }
