import pydub
from aiortc import MediaStreamTrack
from webrtc.types import EMediaStreamAction


class AudioTrackStream(MediaStreamTrack):
    kind = "audio"

    def __init__(self, track, action: EMediaStreamAction):
        super().__init__()
        self.track = track
        self.action = action

    async def recv(self):
        frame = await self.track.recv()
        raw_samples = frame.to_ndarray()

        sound = pydub.AudioSegment(
            data=raw_samples.tobytes(),
            sample_width=frame.format.bytes,
            frame_rate=frame.sample_rate,
            channels=len(frame.layout.channels),
        )

        channel_sounds = sound.split_to_mono()
        channel_samples = [s.get_array_of_samples() for s in channel_sounds]

        print(channel_samples)

        frame_actions = {
            EMediaStreamAction.TO_TEXT.value: lambda x: x + 1,
        }

        return frame
