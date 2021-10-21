import pydub
import logging
import os
from uuid import uuid4
from aiortc import MediaStreamTrack
from deeprtc.modules.webrtc.types import EMediaStreamAction
from deeprtc.common.settings import model, base_dir


logger = logging.getLogger(__name__)


class AudioTrackStream(MediaStreamTrack):
    kind = "audio"
    sound_window_len = 5000

    def __init__(self, track, action: EMediaStreamAction):
        super().__init__()
        self.track = track
        self.action = action
        self.sound_chunk = pydub.AudioSegment.empty()

    async def recv(self):
        frame = await self.track.recv()
        raw_samples = frame.to_ndarray()

        sound = pydub.AudioSegment(
            data=raw_samples.tobytes(),
            sample_width=frame.format.bytes,
            frame_rate=frame.sample_rate,
            channels=len(frame.layout.channels),
        )

        self.sound_chunk += sound

        len_chunk = len(self.sound_chunk)

        print(f'Len of sound chunk: {len_chunk}')

        if len(self.sound_chunk) > self.sound_window_len:
            res = self.sound_chunk.set_channels(1)
            try:
                filename = f'{uuid4().hex}.wav'
                res.export(filename, format='wav')
                # wav = np.array(sample)
                full_path = str(base_dir / filename)
                text = model.transcribe(
                    paths2audio_files=[full_path])
                # np.frombuffer(memoryBuff.getbuffer(), dtype=np.int16))
                print(f'Text: {text}')
                os.remove(full_path)
            except Exception as err:
                logger.error(err)
            finally:
                self.sound_chunk = pydub.AudioSegment.empty()

        return frame
